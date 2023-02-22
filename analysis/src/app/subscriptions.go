package app

import (
	"analysis/src/app/analysis"
	"analysis/src/app/controller"
	"analysis/src/app/iex"
	"analysis/src/app/timeseries"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/nats-io/nats.go"
)

type JsonError struct {
	Error string `json:"error"`
	Id    string `json:"id"`
	Range string `json:"range"`
}

func NewJsonError(err error, id string, period string) *JsonError {
	return &JsonError{
		Error: err.Error(),
		Id:    id,
		Range: period,
	}
}

func portfolioAnalysisSubscriber(cr controller.ControllerRequestor, ir iex.IexRequestor, nc *nats.Conn) {
	nc.QueueSubscribe(os.Getenv("ANALYSIS_SUBSCRIPTION_TASK"), "workers", func(msg *nats.Msg) {
		start := time.Now()
		fmt.Println("Got task request on:", msg.Subject)

		var err error
		analyser := analysis.NewAnalyser()

		if err := json.Unmarshal(msg.Data, analyser.Input); err != nil {
			log.Panic(err)
		}
		id := analyser.Input.Id
		period := analyser.Input.Range
		fmt.Println(fmt.Sprintf("Successfully parsed analysis request for user %s over period %s", id, period))

		symbols := make([]string, len(analyser.Input.Holdings))
		for idx, holding := range analyser.Input.Holdings {
			symbols[idx] = holding.Symbol
		}

		tickerDataBySymbol, err := ir.GetHistoricalPrices(period, symbols)
		if err != nil {
			fmt.Println(err.Error())
			if err := cr.PostResult(id, NewJsonError(err, id, period)); err != nil {
				log.Panic(err)
			}
		}

		analyser, err = analyser.AnalysePortfolio(analyser.Input.Holdings, tickerDataBySymbol)
		if err != nil {
			fmt.Println(err.Error())
			if err := cr.PostResult(id, NewJsonError(err, id, period)); err != nil {
				log.Panic(err)
			}
		}

		analyser.Output.Id = id
		analyser.Output.Range = period
		if err := cr.PostResult(id, analyser.Output); err != nil {
			log.Panic(err)
		}

		elapsed := time.Since(start)
		fmt.Println("Processed the task request on:", msg.Subject, "in time:", elapsed)

		analyser = nil // Notify the GC to free this memory
	})
}

func portfolioTimeseriesSubscriber(cr controller.ControllerRequestor, ir iex.IexRequestor, nc *nats.Conn) {
	nc.QueueSubscribe(os.Getenv("TIMESERIES_SUBSCRIPTION_TASK"), "workers", func(msg *nats.Msg) {
		start := time.Now()
		fmt.Println("Got task request on:", msg.Subject)

		var err error
		timeseries := timeseries.NewTimeseries()

		if err := json.Unmarshal(msg.Data, timeseries.Input); err != nil {
			log.Panic(err)
		}
		id := timeseries.Input.Id
		period := timeseries.Input.Range
		fmt.Println(fmt.Sprintf("Successfully parsed timeseries request for user %s over period %s", id, period))

		symbols := make([]string, len(timeseries.Input.Holdings))
		for idx, holding := range timeseries.Input.Holdings {
			symbols[idx] = holding.Symbol
		}

		tickerTimeseriesBySymbol, err := ir.GetHistoricalPrices(period, symbols)
		if err != nil {
			if err = cr.PostResult(id, NewJsonError(err, id, period)); err != nil {
				log.Panic(err)
			}
		}

		forexDataBySymbol, err := ir.GetHistoricalForexes(timeseries.Input.Currency, period, symbols)
		if err != nil {
			if err = cr.PostResult(id, NewJsonError(err, id, period)); err != nil {
				log.Panic(err)
			}
		}

		timeseries, err = timeseries.CalculateTimeseries(timeseries.Input.Holdings, tickerTimeseriesBySymbol, forexDataBySymbol)
		if err != nil {
			if err = cr.PostResult(id, NewJsonError(err, id, period)); err != nil {
				log.Panic(err)
			}
		}

		timeseries.Output.Id = id
		timeseries.Output.Range = period
		if err = cr.PostResult(id, timeseries.Output); err != nil {
			log.Panic(err)
		}

		elapsed := time.Since(start)
		fmt.Println("Processed the task request on:", msg.Subject, "in time:", elapsed)

		timeseries = nil // Notify the GC to free this memory
	})
}
