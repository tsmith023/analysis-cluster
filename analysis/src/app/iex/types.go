package iex

import "net/http"

type TickerDatum struct {
	ChangePercent float64 `json:"change_percent"`
	Close         float64 `json:"close"`
	Date          string  `json:"date"`
	FiftyDay      float64 `json:"fifty_day"`
	OneHundredDay float64 `json:"one_hundred_day"`
	TwoHundredDay float64 `json:"two_hundred_day"`
	TwentyDay     float64 `json:"twenty_day"`
}

type TickerTimeseriesBySymbol map[string][]TickerDatum

type IexRequestor interface {
	GetHistoricalForexes(currency string, timeRange string, symbols []string) (ForexDataBySymbol, error)
	GetHistoricalPrices(timeRange string, symbols []string) (TickerTimeseriesBySymbol, error)
	GetTickerQuotes(symbols []string) (TickerQuotesBySymbol, error)
}

type IexClient struct {
	*http.Client
	baseUrl string
}

type ForexDatum struct {
	Date          string  `json:"date"`
	FiftyDay      float64 `json:"fifty_day"`
	OneHundredDay float64 `json:"one_hundred_day"`
	Rate          float64 `json:"rate"`
	TwentyDay     float64 `json:"twenty_day"`
	TwoHundredDay float64 `json:"two_hundred_day"`
}

type ForexDataByDate map[string]ForexDatum

type ForexDataBySymbol map[string]ForexDataByDate

type TickerQuote struct {
	Currency string `json:"currency"`
}

type TickerQuotesBySymbol map[string]TickerQuote

type ForexDataByConversionSymbol map[string][]ForexDatum
