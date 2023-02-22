package analysis

import (
	"analysis/src/app/iex"
	"math"
)

// func GeneratePermutations(tickerData []iex.TickerDatum) (TickerDailyReturnsPerms error) {

// }

func generateReturnPerPeriod(numberOfDays int, tickerTimeseries []iex.TickerDatum) <-chan *float64 {
	ch := make(chan *float64)
	go func() {
		defer close(ch)
		count := 1
		returns := 1.0
		for _, datum := range tickerTimeseries {
			if count == numberOfDays {
				ch <- &returns
				count = 1
				returns = 1
			} else {
				count++
				returns *= (1 + datum.ChangePercent)
			}
		}
	}()
	return ch
}

func calculateHoldingReturns(holdings []Holding, numberOfDays int, tickerTimeseriesBySymbol iex.TickerTimeseriesBySymbol) ([][]float64, int) {
	allWeightedReturns := [][]float64{}
	maxNumberOfPoints := 0
	for _, holding := range holdings {
		weightedReturns := []float64{}
		for value := range generateReturnPerPeriod(numberOfDays, tickerTimeseriesBySymbol[holding.Symbol]) {
			weightedReturns = append(weightedReturns, *value*holding.Percentage)
			if len(weightedReturns) > maxNumberOfPoints {
				maxNumberOfPoints = len(weightedReturns)
			}

		}
		allWeightedReturns = append(allWeightedReturns, weightedReturns)
	}
	return allWeightedReturns, maxNumberOfPoints
}

func findDaysPerPeriod(numberOfPeriods int, tickerTimeseriesBySymbol iex.TickerTimeseriesBySymbol) int {
	numberOfDays := 0
	for _, timeseries := range tickerTimeseriesBySymbol {
		if length := int(math.Ceil(float64(len(timeseries) / numberOfPeriods))); length > numberOfDays {
			numberOfDays = length
		}
	}
	return numberOfDays
}

func calculatePortfolioReturns(holdings []Holding, tickerTimeseriesBySymbol iex.TickerTimeseriesBySymbol) []float64 {
	maxNumberOfPoints := 0

	numberOfDays := findDaysPerPeriod(10, tickerTimeseriesBySymbol)
	if numberOfDays == 0 {
		panic("Calculated numberOfDays to be zero within calculatePortfolioReturns")
	}

	allWeightedReturns, maxNumberOfPoints := calculateHoldingReturns(holdings, numberOfDays, tickerTimeseriesBySymbol)

	portfolioReturns := make([]float64, maxNumberOfPoints, maxNumberOfPoints)
	for idx := range portfolioReturns {
		portfolioReturns[idx] = 1
	}

	for _, weightedReturns := range allWeightedReturns {
		diff := 0
		if len(weightedReturns) != maxNumberOfPoints {
			diff = maxNumberOfPoints - len(weightedReturns)
		}
		for i := diff; i < maxNumberOfPoints; i++ {
			portfolioReturns[i] *= weightedReturns[i-diff]
		}
	}
	return portfolioReturns
}
