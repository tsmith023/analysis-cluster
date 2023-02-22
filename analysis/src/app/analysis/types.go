package analysis

// type ChannelOutput struct {
// 	Symbol string
// 	Datum  HoldingDatum
// }

type Holding struct {
	Symbol     string  `json:"symbol"`
	Percentage float64 `json:"percentage"`
}

type AnalysisInput struct {
	Id       string    `json:"id"`
	Range    string    `json:"range"`
	Holdings []Holding `json:"holdings"`
}

type GenerateWeightedReturnsChanOut struct {
	returns float64
}

type AnalysisOutput struct {
	Id                     string  `json:"id"`
	Range                  string  `json:"range"`
	AnnualisedRateOfReturn float64 `json:"annualised_rate_of_return"`
	DownsideDeviation      float64 `json:"downside_deviation"`
	MeanSquaredError       float64 `json:"mean_squared_error"`
	SortinoRatio           float64 `json:"sortino_ratio"`
	UpsidePotential        float64 `json:"upside_ratio"`
	UpsideProbability      float64 `json:"upside_probability"`
}

type Analyser struct {
	Input  *AnalysisInput
	Output *AnalysisOutput
}

type Distribution struct {
	bins              []bin
	mean              float64
	standardDeviation float64
	weighting         float64
	Metrics           AnalysisOutput
}
