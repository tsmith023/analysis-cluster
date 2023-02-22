package timeseries

import "testing"

func Test_sumHoldingDatumPortfolioDatumNil(t *testing.T) {
	movingAverages := MovingAverages{
		FiftyDay:      50,
		OneHundredDay: 100,
		TwoHundredDay: 200,
		TwentyDay:     20,
	}
	holdingDatum := HoldingDatum{
		Cost:           80,
		Date:           "2022-08-08",
		MovingAverages: movingAverages,
		Shares:         10,
		Value:          500,
	}
	var portfolioDatum *PortfolioDatum
	portfolioDatum = portfolioDatum.sumHoldingDatum(&holdingDatum)
	if portfolioDatum.Cost != 80 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.Cost != holdingDatum.Cost, %v!=%v`, portfolioDatum.Cost, 80)
	}
	if portfolioDatum.Date != holdingDatum.Date {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.Date != holdingDatum.Date, %q!=%q`, portfolioDatum.Date, holdingDatum.Date)
	}
	if portfolioDatum.Value != 500 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.Value != holdingDatum.Value, %v!=%v`, portfolioDatum.Value, 500)
	}
	if portfolioDatum.MovingAverages.FiftyDay != 50 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.FiftyDay != holdingDatum.MovingAverages.FiftyDay, %v!=%v`, portfolioDatum.MovingAverages.FiftyDay, 50)
	}
	if portfolioDatum.MovingAverages.OneHundredDay != 100 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.OneHundredDay != holdingDatum.MovingAverages.OneHundredDay, %v!=%v`, portfolioDatum.MovingAverages.OneHundredDay, 100)
	}
	if portfolioDatum.MovingAverages.TwoHundredDay != 200 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.TwoHundredDay != holdingDatum.MovingAverages.TwoHundredDay, %v!=%v`, portfolioDatum.MovingAverages.TwoHundredDay, 200)
	}
	if portfolioDatum.MovingAverages.TwentyDay != 20 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.TwentyDay != holdingDatum.MovingAverages.TwentyDay, %v!=%v`, portfolioDatum.MovingAverages.TwentyDay, 20)
	}
}

func Test_sumHoldingDatumPortfolioDatumNonNil(t *testing.T) {
	movingAverages := MovingAverages{
		FiftyDay:      50,
		OneHundredDay: 100,
		TwoHundredDay: 200,
		TwentyDay:     20,
	}
	holdingDatum := HoldingDatum{
		Cost:           80,
		Date:           "2022-08-08",
		MovingAverages: movingAverages,
		Shares:         10,
		Value:          500,
	}
	portfolioDatum := &PortfolioDatum{
		Cost:           10,
		Date:           "2022-08-08",
		MovingAverages: movingAverages,
		Value:          100,
	}
	portfolioDatum = portfolioDatum.sumHoldingDatum(&holdingDatum)
	if portfolioDatum.Cost != 90 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.Cost != holdingDatum.Cost, %v!=%v`, portfolioDatum.Cost, 90)
	}
	if portfolioDatum.Date != holdingDatum.Date {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.Date != holdingDatum.Date, %q!=%q`, portfolioDatum.Date, holdingDatum.Date)
	}
	if portfolioDatum.Value != 600 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.Cost != holdingDatum.Value, %v!=%v`, portfolioDatum.Value, 600)
	}
	if portfolioDatum.MovingAverages.FiftyDay != 100 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.FiftyDay != holdingDatum.MovingAverages.FiftyDay, %v!=%v`, portfolioDatum.MovingAverages.FiftyDay, 100)
	}
	if portfolioDatum.MovingAverages.OneHundredDay != 200 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.OneHundredDay != holdingDatum.MovingAverages.OneHundredDay, %v!=%v`, portfolioDatum.MovingAverages.OneHundredDay, 200)
	}
	if portfolioDatum.MovingAverages.TwoHundredDay != 400 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.TwoHundredDay != holdingDatum.MovingAverages.TwoHundredDay, %v!=%v`, portfolioDatum.MovingAverages.TwoHundredDay, 400)
	}
	if portfolioDatum.MovingAverages.TwentyDay != 40 {
		t.Fatalf(`SumHoldingDatum: portfolioDatum.MovingAverages.TwentyDay != holdingDatum.MovingAverages.TwentyDay, %v!=%v`, portfolioDatum.MovingAverages.TwentyDay, 40)
	}
}

func Test_sumMovingAveragesSuccess(t *testing.T) {
	movingAverages := MovingAverages{
		FiftyDay:      50,
		OneHundredDay: 100,
		TwoHundredDay: 200,
		TwentyDay:     20,
	}
	newMovingAverages := MovingAverages{
		FiftyDay:      50,
		OneHundredDay: 100,
		TwoHundredDay: 200,
		TwentyDay:     20,
	}
	movingAverages = movingAverages.sumMovingAverages(newMovingAverages)
	if movingAverages.FiftyDay != 2*newMovingAverages.FiftyDay {
		t.Fatalf(`SumMovingMaverages: movingAverages.FiftyDay != 2*newMovingAverages.FiftyDay, %v!=%v`, movingAverages.FiftyDay, 2*newMovingAverages.FiftyDay)
	}
	if movingAverages.OneHundredDay != 2*newMovingAverages.OneHundredDay {
		t.Fatalf(`SumMovingMaverages: movingAverages.OneHundredDay != 2*newMovingAverages.OneHundredDay, %v!=%v`, movingAverages.OneHundredDay, 2*newMovingAverages.OneHundredDay)
	}
	if movingAverages.TwoHundredDay != 2*newMovingAverages.TwoHundredDay {
		t.Fatalf(`SumMovingMaverages: movingAverages.TwoHundredDay != 2*newMovingAverages.TwoHundredDay, %v!=%v`, movingAverages.TwoHundredDay, 2*newMovingAverages.TwoHundredDay)
	}
	if movingAverages.TwentyDay != 2*newMovingAverages.TwentyDay {
		t.Fatalf(`SumMovingMaverages: movingAverages.TwentyDay != 2*newMovingAverages.TwentyDay, %v!=%v`, movingAverages.TwentyDay, 2*newMovingAverages.TwentyDay)
	}
}
