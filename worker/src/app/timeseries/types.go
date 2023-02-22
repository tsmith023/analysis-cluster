package timeseries

import "time"

type ChannelOutput struct {
	Symbol string
	Datum  HoldingDatum
}

type CumulativeData struct {
	cost           float64
	shares         float64
	tradesByDate   TradesByDate
	firstTradeDate time.Time
}

type Holding struct {
	Symbol string  `json:"symbol"`
	Trades []Trade `json:"trades"`
}

type HoldingDatum struct {
	Cost           float64        `json:"cost"`
	Date           string         `json:"date"`
	MovingAverages MovingAverages `json:"moving_averages"`
	Shares         float64        `json:"shares"`
	Value          float64        `json:"value"`
}

type MovingAverages struct {
	FiftyDay      float64 `json:"fifty_day"`
	OneHundredDay float64 `json:"one_hundred_day"`
	TwoHundredDay float64 `json:"two_hundred_day"`
	TwentyDay     float64 `json:"twenty_day"`
}

type PortfolioDatum struct {
	Cost           float64        `json:"cost"`
	Date           string         `json:"date"`
	MovingAverages MovingAverages `json:"moving_averages"`
	Value          float64        `json:"value"`
}

type TimeseriesInput struct {
	Currency string    `json:"currency"`
	Id       string    `json:"id"`
	Range    string    `json:"range"`
	Holdings []Holding `json:"holdings"`
}

type TimeseriesOutput struct {
	// Map Go naming style to Python naming style to match FastAPI OpenAPI spec of Controller
	Id                        string                    `json:"id"`
	HoldingTimeseriesBySymbol map[string][]HoldingDatum `json:"holding_timeseries_by_symbol"`
	PortfolioTimeseries       []PortfolioDatum          `json:"portfolio_timeseries"`
	Range                     string                    `json:"range"`
}

type Timeseries struct {
	Input  *TimeseriesInput
	Output *TimeseriesOutput
}

type Trade struct {
	BuyOrSell bool    `json:"buy_or_sell"`
	Cost      float64 `json:"cost"`
	Date      string  `json:"date"`
	Shares    float64 `json:"shares"`
}

type TradesByDate map[string][]Trade
