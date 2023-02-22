package timeseries

import (
	"analysis/src/app/iex"
	"time"

	"github.com/samber/lo"
)

func NewTimeseries() *Timeseries {
	return &Timeseries{
		Input:  new(TimeseriesInput),
		Output: new(TimeseriesOutput),
	}
}

func calculateCumulativeData(firstTickerDatumDate time.Time, trades []Trade) *CumulativeData {
	cost, shares, tradesByDate := float64(0), float64(0), make(map[string][]Trade)
	firstTradeDate := time.Now()
	for _, trade := range trades {
		tradesByDate[trade.Date] = append(tradesByDate[trade.Date], trade)
		tradeDate := parseDate(trade.Date)
		if tradeDate.Before(firstTradeDate) {
			firstTradeDate = tradeDate
		}
		if tradeDate.Before(firstTickerDatumDate) {
			if trade.BuyOrSell {
				cost += trade.Cost
				shares += trade.Shares
			} else {
				cost -= trade.Cost
				shares -= trade.Shares
			}
		}
	}
	return &CumulativeData{
		cost:           cost,
		shares:         shares,
		tradesByDate:   tradesByDate,
		firstTradeDate: firstTradeDate,
	}
}

func parseDate(date string) time.Time {
	format := "2006-01-02"
	parsedDate, err := time.Parse(format, date)
	if err != nil {
		panic(err)
	}
	return parsedDate
}

func calculateAverage(rates []float64) float64 {
	ave := 0.0
	for _, rate := range rates {
		ave += rate
	}
	return ave / float64(len(rates))
}

func generateHoldingData(forexData iex.ForexDataByDate, tickerData []iex.TickerDatum, trades []Trade) <-chan HoldingDatum {
	// sort.SliceStable(tickerData, func(i, j int) bool {
	// 	before := parseDate(tickerData[i].Date)
	// 	after := parseDate(tickerData[j].Date)
	// 	return before.Before(after)
	// })

	firstTickerDatumDate := parseDate(tickerData[0].Date)
	cumulativeData := calculateCumulativeData(firstTickerDatumDate, trades)

	relevantTickerData := lo.DropWhile(tickerData, func(datum iex.TickerDatum) bool {
		return parseDate(datum.Date).Before(cumulativeData.firstTradeDate)
	})

	ch := make(chan HoldingDatum)
	go func(cd *CumulativeData) {
		defer close(ch)
		for _, datum := range relevantTickerData {
			dailyTrades, okT := cumulativeData.tradesByDate[datum.Date]
			dailyForex, _ := forexData[datum.Date]
			if okT {
				for _, trade := range dailyTrades {
					if trade.BuyOrSell {
						cd.cost += trade.Cost
						cd.shares += trade.Shares
					} else {
						cd.cost -= trade.Cost
						cd.shares -= trade.Shares
					}
				}
			}
			ch <- HoldingDatum{
				Cost: cd.cost,
				Date: datum.Date,
				MovingAverages: MovingAverages{
					cd.shares * datum.FiftyDay * dailyForex.FiftyDay,
					cd.shares * datum.OneHundredDay * dailyForex.OneHundredDay,
					cd.shares * datum.TwoHundredDay * dailyForex.TwoHundredDay,
					cd.shares * datum.TwentyDay * dailyForex.TwentyDay,
				},
				Shares: cd.shares,
				Value:  cd.shares * datum.Close * dailyForex.Rate,
			}
		}
	}(cumulativeData)
	return ch
}
