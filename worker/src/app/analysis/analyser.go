package analysis

import (
	"analysis/src/app/iex"
	"analysis/src/app/permutations"
	"sync"
)

func NewAnalyser() *Analyser {
	return &Analyser{
		Input:  new(AnalysisInput),
		Output: new(AnalysisOutput),
	}
}

func (a *Analyser) AnalysePortfolio(holdings []Holding, tickerTimeseriesBySymbol iex.TickerTimeseriesBySymbol) (*Analyser, error) {
	if a == nil {
		a = NewAnalyser()
	}
	portfolioReturns := calculatePortfolioReturns(holdings, tickerTimeseriesBySymbol)

	ch := make(chan *float64)
	wg := sync.WaitGroup{}
	haf := permutations.NewHeapsAlgorithmFlat[float64]()
	for permutation := range permutations.GeneratePermutations(portfolioReturns, haf) {
		wg.Add(1)
		go func(permutation *[]float64, wg *sync.WaitGroup) {
			annualReturn := 1.0
			for _, monthlyReturn := range *permutation {
				annualReturn *= monthlyReturn
			}
			ch <- &annualReturn
			wg.Done()
		}(permutation, &wg)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	histogram := NewHistogram(30)
	for annualReturn := range ch {
		histogram.Add(*annualReturn)
	}

	rawData := []float64{}
	for _, bin := range histogram.bins {
		rawData = append(rawData, bin.count)
	}
	distribution := NewDistribution(histogram.bins)
	distribution = distribution.fitCurve()
	distribution = distribution.CalculateMetrics(0.1)

	a.Output = &distribution.Metrics

	return a, nil
}
