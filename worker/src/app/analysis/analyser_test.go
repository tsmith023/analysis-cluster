package analysis

import (
	"analysis/src/app/iex"
	"testing"
)

func TestAnalysePortfolio(t *testing.T) {
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

	var analyser *Analyser
	output, _ := analyser.AnalysePortfolio(holdings, tickerTimeseriesBySymbol)
	t.Fatalf("analysisOutput: %v", output)
}
