package analysis

import (
	"log"
	"math"
	"sync"

	"gonum.org/v1/gonum/diff/fd"
	"gonum.org/v1/gonum/mat"
	"gonum.org/v1/gonum/optimize"
)

func NewDistribution(bins []bin) *Distribution {
	return &Distribution{
		bins:              bins,
		mean:              1,
		standardDeviation: 0.1,
		weighting:         0.05,
	}
}

func (d *Distribution) binLength() float64 {
	return float64(len(d.bins))
}

func (d *Distribution) f(x float64) float64 {
	return threeParameterLognormalDistribution(d.mean, d.standardDeviation, x, d.weighting)
}

func threeParameterLognormalDistribution(mean float64, standardDeviation float64, variable float64, weighting float64) float64 {
	alpha := 1 / (standardDeviation * math.Pow(2*math.Pi, .5))
	beta := -1 / (2 * math.Pow(standardDeviation, 2))
	x := math.Abs(variable - weighting)
	return alpha * math.Exp(beta*math.Pow(math.Log(x)-mean, 2)) / x
}

func residual(x float64, y float64, vars []float64) float64 {
	return y - threeParameterLognormalDistribution(vars[0], vars[1], x, vars[2])
}

func (d *Distribution) fitnessFunction(x []float64) float64 {
	sum := 0.0
	for i := 0; i < len(d.bins); i++ {
		sum += math.Pow(residual(float64(i), d.bins[i].value, x), 2)
	}
	return sum
}

func (d *Distribution) fitCurve() *Distribution {
	fcn := func(x []float64) float64 {
		return d.fitnessFunction(x)
	}
	grad := func(grad, x []float64) {
		fd.Gradient(grad, fcn, x, nil)
	}
	hess := func(h *mat.SymDense, x []float64) {
		fd.Hessian(h, fcn, x, nil)
	}

	p := optimize.Problem{
		Func: fcn,
		Grad: grad,
		Hess: hess,
	}
	var meth = &optimize.NelderMead{}
	var p0 = []float64{1, 0.1, 0.01}

	res, err := optimize.Minimize(p, p0, nil, meth)
	if err != nil {
		log.Panic(err)
	}
	// fmt.Printf(`location: %v, stats: %v, status: %v`, res.Location, res.Stats, res.Status)

	d.mean = res.Location.X[0]
	d.standardDeviation = res.Location.X[1]
	d.weighting = res.Location.X[2]
	return d
}

// resolution governs the stepsize as step=1/res, so resolution=10 is a stepsize of 0.1
func (d *Distribution) createIntegrandRange(min int, max int, resolution int, fn func(float64) float64) ([]float64, []float64) {
	N := max * resolution
	x := make([]float64, N)
	f := make([]float64, N)
	for i := min; i < N; i++ {
		inc := float64(i / resolution)
		x = append(x, inc)
		f = append(f, fn(inc))
	}
	return x, f
}

func (d *Distribution) calculateAnnualisedRateOfReturn(mar float64) {
	integrand := func(x float64) float64 {
		return x * d.f(x)
	}
	d.Metrics.AnnualisedRateOfReturn = Trapezoidal(-500, 500, 10000, integrand)
}

func (d *Distribution) calculateDownsideDeviation(mar float64) {
	integrand := func(x float64) float64 {
		return math.Pow(x-mar, 2) * d.f(x)
	}
	d.Metrics.DownsideDeviation = Trapezoidal(-1000, mar, 10000, integrand)
}

func (d *Distribution) calculateMeanSquaredError(mar float64) {
	d.Metrics.MeanSquaredError = d.fitnessFunction([]float64{d.mean, d.standardDeviation, d.weighting}) / d.binLength()
}

func (d *Distribution) calculateUpsidePotential(mar float64) {
	integrand := func(x float64) float64 {
		return (x - mar) * d.f(x)
	}
	d.Metrics.UpsidePotential = Trapezoidal(mar, 1000, 10000, integrand)
}

func (d *Distribution) CalculateMetrics(mar float64) *Distribution {
	metrics := []func(float64){
		d.calculateAnnualisedRateOfReturn,
		d.calculateDownsideDeviation,
		d.calculateMeanSquaredError,
		d.calculateUpsidePotential,
	}
	var wg sync.WaitGroup
	for _, fn := range metrics {
		wg.Add(1)
		go func(fn func(float64), wg *sync.WaitGroup) {
			fn(mar)
			wg.Done()
		}(fn, &wg)
	}
	wg.Wait()
	d.Metrics.UpsideProbability = 1 - d.f(mar)
	d.Metrics.SortinoRatio = (d.Metrics.AnnualisedRateOfReturn - mar) / d.Metrics.DownsideDeviation
	return d
}
