package analysis

import (
	"analysis/src/app/iex"
	"math"
	"testing"
)

func Test_generateReturnPerPeriod(t *testing.T) {
	tickerTimeseries := make([]iex.TickerDatum, 32, 32)
	testTickerDatum := iex.TickerDatum{
		ChangePercent: 0.1,
		Close:         100,
		Date:          "2020-06-06",
		FiftyDay:      50,
		OneHundredDay: 100,
		TwoHundredDay: 200,
		TwentyDay:     20,
	}
	for i := 0; i < 32; i++ {
		tickerTimeseries[i] = testTickerDatum
	}

	values := []float64{}
	for value := range generateReturnPerPeriod(30, tickerTimeseries) {
		values = append(values, *value)
	}
	if len(values) != 1 {
		t.Fatalf(`len(values) != 1: %v`, values)
	}
	if values[0] != math.Pow(1.1, 30) {
		t.Fatalf(`%v != %v`, values[0], math.Pow(1.1, 30))
	}
}

func Test_calculateHoldingReturns(t *testing.T) {
	holdings := []Holding{}
	holdings = append(holdings, Holding{
		Symbol:     "TSLA",
		Percentage: 1,
	})
	tickerTimeseriesBySymbol := make(map[string][]iex.TickerDatum)

	tickerTimeseries := make([]iex.TickerDatum, 32, 32)
	testTickerDatum := iex.TickerDatum{
		ChangePercent: 0.1,
		Close:         100,
		Date:          "2020-06-06",
		FiftyDay:      50,
		OneHundredDay: 100,
		TwoHundredDay: 200,
		TwentyDay:     20,
	}
	for i := 0; i < 32; i++ {
		tickerTimeseries[i] = testTickerDatum
	}

	tickerTimeseriesBySymbol["TSLA"] = tickerTimeseries
	holdingReturns, maxNumberOfPoints := calculateHoldingReturns(holdings, 30, tickerTimeseriesBySymbol)
	if len(holdingReturns) != 1 {
		t.Fatalf(`len(holdingReturns) != 1: %v`, holdingReturns)
	}
	if len(holdingReturns[0]) != 1 {
		t.Fatalf(`len(holdingReturns[0]) != 1: %v`, holdingReturns[0])
	}
	if holdingReturns[0][0] != math.Pow(1.1, 30) {
		t.Fatalf(`%v != %v`, holdingReturns[0][0], math.Pow(1.1, 30))
	}
	if maxNumberOfPoints != 1 {
		t.Fatalf(`maxNumberOfPoints != 1: %v`, maxNumberOfPoints)
	}
}

func Test_calculatePortfolioReturns(t *testing.T) {
	holdings := []Holding{}
	holdings = append(holdings, Holding{
		Symbol:     "TSLA",
		Percentage: 0.5,
	})
	tickerTimeseriesBySymbol := make(map[string][]iex.TickerDatum)

	length := 60
	tickerTimeseries := make([]iex.TickerDatum, length, length)
	testTickerDatum := iex.TickerDatum{
		ChangePercent: 0.1,
		Close:         100,
		Date:          "2020-06-06",
		FiftyDay:      50,
		OneHundredDay: 100,
		TwoHundredDay: 200,
		TwentyDay:     20,
	}
	for i := 0; i < length; i++ {
		tickerTimeseries[i] = testTickerDatum
	}

	tickerTimeseriesBySymbol["TSLA"] = tickerTimeseries
	portfolioReturns := calculatePortfolioReturns(holdings, tickerTimeseriesBySymbol)
	if len(portfolioReturns) != 10 {
		t.Fatalf(`len(portfolioReturns) != 10: %v`, portfolioReturns)
	}
	actual := 2 * portfolioReturns[0]
	expected := math.Pow(1.1, 5)
	if math.Round(actual*1000/1000) != math.Round(expected*1000/1000) {
		t.Fatalf(`%v != %v`, math.Round(actual*1000/1000), math.Round(expected*1000/1000))
	}
}
