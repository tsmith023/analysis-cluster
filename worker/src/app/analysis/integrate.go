package analysis

import (
	"sync"
)

func Trapezoidal(a float64, b float64, trapezoidNumber int, fn func(float64) float64) float64 {
	switch {
	case trapezoidNumber == 0:
		panic("integrate: cannot integrate with no trapezoids")
	case trapezoidNumber == 1:
		panic("integrate: cannot integrate with only one trapezoid")
	case a == b:
		panic("integrate: bounds cannot be equal")
	case a > b:
		panic("integrate: a must be less than b")
	}

	step := (b - a) / float64(trapezoidNumber)

	var wg sync.WaitGroup
	ch := make(chan float64)
	for i := 0; i < trapezoidNumber-1; i++ {
		wg.Add(1)
		go func(idx int, wg *sync.WaitGroup) {
			current := a + float64(idx)*step
			next := a + float64(idx+1)*step
			ch <- 0.5 * (next - current) * (fn(next) + fn(current))
			wg.Done()
		}(i, &wg)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	integral := 0.0
	for value := range ch {
		integral += value
	}

	return integral
}
