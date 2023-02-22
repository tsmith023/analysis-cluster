package iex

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"

	mapset "github.com/deckarep/golang-set/v2"
)

func (ic *IexClient) createPricesUrl(timeRange string, symbols []string) (string, error) {
	empty := struct{}{}
	allowedRanges := map[string]struct{}{"6m": empty, "ytd": empty, "1y": empty, "2y": empty, "5y": empty, "max": empty}
	if timeRange == "" {
		return timeRange, errors.New("No timeRange provided")
	}
	_, ok := allowedRanges[timeRange]
	if !ok {
		return "", errors.New("Invalid timeRange provided")
	}
	if len(symbols) == 0 {
		return "", errors.New("No symbols provided")
	}
	symbolsString := createSymbols(symbols)
	return fmt.Sprintf("%v/historical-prices?period=%v&symbols=%v", ic.baseUrl, timeRange, symbolsString), nil
}

func (ic *IexClient) createForexesUrl(timeRange string, symbols []string) (string, error) {
	empty := struct{}{}

	allowedRanges := map[string]struct{}{"6m": empty, "ytd": empty, "1y": empty, "2y": empty, "5y": empty, "max": empty}
	if timeRange == "" {
		return timeRange, errors.New("No timeRange provided")
	}
	_, ok := allowedRanges[timeRange]
	if !ok {
		return "", errors.New("Invalid timeRange provided")
	}
	if len(symbols) == 0 {
		return "", errors.New("No symbols provided")
	}

	symbolsString := createSymbols(symbols)
	return fmt.Sprintf("%v/historical-forexes?period=%v&symbols=%v", ic.baseUrl, timeRange, symbolsString), nil
}

func (ic *IexClient) createQuotesUrl(symbols []string) (string, error) {
	if len(symbols) == 0 {
		return "", errors.New("No symbols provided")
	}
	symbolsString := createSymbols(symbols)
	return fmt.Sprintf("%v/latest-quotes?symbols=%v", ic.baseUrl, symbolsString), nil
}

func (ic *IexClient) GetHistoricalPrices(timeRange string, symbols []string) (TickerTimeseriesBySymbol, error) {
	if ic == nil {
		panic("IexClient must be initialised to use its methods")
	}
	var err error
	url, err := ic.createPricesUrl(timeRange, symbols)
	if err != nil {
		return nil, errors.New("%w; Failed to create url string for retrieving historical prices")
	}

	res, err := http.Get(url)
	if err != nil {
		return nil, errors.New("%w; Failed to retrieve historical prices data from given host and port for given timeRange and symbols")
	}
	defer res.Body.Close()

	decoder := json.NewDecoder(res.Body)
	var data TickerTimeseriesBySymbol
	err = decoder.Decode(&data)

	if err != nil {
		return nil, errors.New("%w; Error decoding the JSON data returned from IEX provider")
	}

	return data, nil
}

func (ic *IexClient) GetHistoricalForexes(currency string, timeRange string, symbols []string) (ForexDataBySymbol, error) {
	if ic == nil {
		panic("IexClient must be initialised to use its methods")
	}

	empty := struct{}{}
	allowedCurrencies := map[string]struct{}{"USD": empty, "GBP": empty, "EUR": empty}
	if currency == "" {
		return nil, errors.New("No currency provided")
	}
	_, ok := allowedCurrencies[currency]
	if !ok {
		return nil, errors.New("Invalid currency provided")
	}
	if len(symbols) == 0 {
		return nil, errors.New("No symbols provided")
	}

	var err error
	tickerQuotesBySymbol, err := ic.GetTickerQuotes(symbols)
	if err != nil {
		return nil, err
	}
	tickerSymbolsByConversionSymbol := map[string][]string{}
	conversionsSet := mapset.NewSet[string]()
	for symbol, tickerQuote := range tickerQuotesBySymbol {
		conversionSymbol := fmt.Sprintf("%v%v", tickerQuote.Currency, currency)
		conversionsSet.Add(conversionSymbol)
		tickerSymbolsByConversionSymbol[conversionSymbol] = append(tickerSymbolsByConversionSymbol[conversionSymbol], symbol)
	}

	url, err := ic.createForexesUrl(timeRange, conversionsSet.ToSlice())
	if err != nil {
		return nil, errors.New("%w; Failed to create url string for retrieving historical prices")
	}

	res, err := http.Get(url)
	if err != nil {
		return nil, errors.New("%w; Failed to retrieve historical prices data from given host and port for given timeRange and symbols")
	}
	defer res.Body.Close()

	decoder := json.NewDecoder(res.Body)
	var forexDataByConversionSymbol ForexDataByConversionSymbol
	err = decoder.Decode(&forexDataByConversionSymbol)

	if err != nil {
		return nil, errors.New("%w; Error decoding the JSON data returned from IEX provider")
	}

	forexDataBySymbol := map[string]ForexDataByDate{}
	for symbol, data := range forexDataByConversionSymbol {
		forexDataByDate := map[string]ForexDatum{}
		for _, datum := range data {
			forexDataByDate[datum.Date] = datum
		}
		for _, tickerSymbol := range tickerSymbolsByConversionSymbol[symbol] {
			forexDataBySymbol[tickerSymbol] = forexDataByDate
		}
	}

	return forexDataBySymbol, nil
}

func (ic *IexClient) GetTickerQuotes(symbols []string) (TickerQuotesBySymbol, error) {
	if ic == nil {
		panic("IexClient must be initialised to use its methods")
	}
	var err error
	url, err := ic.createQuotesUrl(symbols)
	if err != nil {
		return nil, errors.New("%w; Failed to create url string for retrieving historical prices")
	}

	res, err := http.Get(url)
	if err != nil {
		return nil, errors.New("%w; Failed to retrieve historical prices data from given host and port for given timeRange and symbols")
	}
	defer res.Body.Close()

	decoder := json.NewDecoder(res.Body)
	var data TickerQuotesBySymbol
	err = decoder.Decode(&data)

	if err != nil {
		return nil, errors.New("%w; Error decoding the JSON data returned from IEX provider")
	}

	return data, nil
}
