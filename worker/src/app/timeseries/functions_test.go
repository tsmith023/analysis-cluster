package timeseries

import (
	"strconv"
	"testing"
	"time"
)

func Test_calculateCumulativeData(t *testing.T) {
	firstDate := time.Date(2022, time.Month(2), 2, 0, 0, 0, 0, time.UTC)
	trades := []Trade{
		{
			BuyOrSell: false,
			Cost:      1100,
			Date:      "2022-02-10",
			Shares:    10,
		},
		{
			BuyOrSell: true,
			Cost:      1000,
			Date:      "2022-01-05",
			Shares:    10,
		},
	}
	cumulativeData := calculateCumulativeData(firstDate, trades)
	if cumulativeData.cost != 1000 {
		t.Fatalf(`calculateCumulativeData: cumulativeCost = %q, want 1000, error`, strconv.FormatFloat(cumulativeData.cost, 'e', -1, 32))
	}
	if cumulativeData.shares != 10 {
		t.Fatalf(`calculateCumulativeData: cumulativeCost = %q, want 10, error`, strconv.FormatFloat(cumulativeData.shares, 'e', -1, 32))
	}
	if cumulativeData.firstTradeDate != time.Date(2022, time.Month(1), 5, 0, 0, 0, 0, time.UTC) {
		t.Fatalf(`calculateCumulativeData: firstTradeDate = %q, want "2022-01-05"`, cumulativeData.firstTradeDate)
	}
	if _, ok := cumulativeData.tradesByDate["2022-01-05"]; !ok {
		t.Fatalf(`calculateCumulativeData: tradesByDate["2022-01-05"] does not exist, error`)
	}
	if _, ok := cumulativeData.tradesByDate["2022-02-10"]; !ok {
		t.Fatalf(`calculateCumulativeData: tradesByDate["2022-02-10"] does not exist, error`)
	}
}

func Test_parseData(t *testing.T) {
	dateString := "2022-02-10"
	parsedDate := parseDate(dateString)
	expectedDate, err := time.Parse("2006-01-02", dateString)
	if err != nil {
		t.Fatalf(`parseDate: date = %q`, dateString)
	}
	if parsedDate != expectedDate {
		t.Fatalf(`parseDate: date = %q`, dateString)
	}
}
