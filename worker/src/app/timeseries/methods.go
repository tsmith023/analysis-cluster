package timeseries

import (
	iex "analysis/src/app/iex"
	"errors"
	"sort"
	"sync"
)

func (ma MovingAverages) sumMovingAverages(nma MovingAverages) MovingAverages {
	ma.FiftyDay += nma.FiftyDay
	ma.OneHundredDay += nma.OneHundredDay
	ma.TwoHundredDay += nma.TwoHundredDay
	ma.TwentyDay += nma.TwentyDay
	return ma
}

func (pd *PortfolioDatum) sumHoldingDatum(hd *HoldingDatum) *PortfolioDatum {
	if pd == nil {
		return &PortfolioDatum{
			Cost:           hd.Cost,
			Date:           hd.Date,
			MovingAverages: hd.MovingAverages,
			Value:          hd.Value,
		}
	}
	pd.Cost += hd.Cost
	pd.MovingAverages = pd.MovingAverages.sumMovingAverages(hd.MovingAverages)
	pd.Value += hd.Value
	return pd
}

func (t *Timeseries) CalculateTimeseries(holdings []Holding, tickerDataBySymbol iex.TickerTimeseriesBySymbol, forexDataBySymbol iex.ForexDataBySymbol) (*Timeseries, error) {
	if t == nil {
		panic(errors.New("t is nil"))
	}
	portfolioDataByDate := map[string]*PortfolioDatum{}
	holdingTimeseriesBySymbol := map[string][]HoldingDatum{}

	ch := make(chan ChannelOutput)
	wg := sync.WaitGroup{}
	for _, v := range holdings {
		wg.Add(1)
		go func(holding Holding, ch chan<- ChannelOutput, wg *sync.WaitGroup) {
			for holdingDatum := range generateHoldingData(forexDataBySymbol[holding.Symbol], tickerDataBySymbol[holding.Symbol], holding.Trades) {
				ch <- ChannelOutput{
					Symbol: holding.Symbol,
					Datum:  holdingDatum,
				}
			}
			wg.Done()
		}(v, ch, &wg)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	for output := range ch {
		holdingTimeseriesBySymbol[output.Symbol] = append(holdingTimeseriesBySymbol[output.Symbol], output.Datum)
		portfolioDataByDate[output.Datum.Date] = portfolioDataByDate[output.Datum.Date].sumHoldingDatum(&output.Datum)
	}

	var portfolioTimeseries []*PortfolioDatum
	for _, datum := range portfolioDataByDate {
		portfolioTimeseries = append(portfolioTimeseries, datum)
	}

	sort.SliceStable(portfolioTimeseries, func(i, j int) bool {
		before := parseDate(portfolioTimeseries[i].Date)
		after := parseDate(portfolioTimeseries[j].Date)
		return before.Before(after)
	})

	for _, datum := range portfolioTimeseries {
		t.Output.PortfolioTimeseries = append(t.Output.PortfolioTimeseries, *datum)
	}
	t.Output.HoldingTimeseriesBySymbol = holdingTimeseriesBySymbol
	return t, nil
}
