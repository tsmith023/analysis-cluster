package app

// import (
// 	"analysis/src/app/analysis"
// 	"analysis/src/app/iex"
// 	"analysis/src/app/timeseries"
// 	"fmt"
// 	"log"
// 	"net/http"
// 	"os"

// 	"github.com/gin-gonic/gin"
// 	"github.com/meteran/gnext"
// )

// func portfolioAnalysisController(c *gin.Context) {
// 	var err error

// 	analyser := analysis.NewAnalyser()
// 	client := iex.NewIexClient()

// 	err = c.BindJSON(analyser.Input)
// 	if err != nil {
// 		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
// 		return
// 	}

// 	symbols := make([]string, len(analyser.Input.Holdings))
// 	for idx, holding := range analyser.Input.Holdings {
// 		symbols[idx] = holding.Symbol
// 	}

// 	tickerDataBySymbol, err := client.GetHistoricalPrices(analyser.Input.Range, symbols)
// 	if err != nil {
// 		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
// 		return
// 	}

// 	analyser, err = analyser.AnalysePortfolio(analyser.Input.Holdings, tickerDataBySymbol)
// 	if err != nil {
// 		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
// 		return
// 	}

// 	c.JSON(http.StatusOK, analyser.Output)
// }

// func portfolioTimeseriesController(c *gin.Context) {
// 	var err error

// 	timeseries := timeseries.NewTimeseries()
// 	client := iex.NewIexClient()

// 	err = c.BindJSON(timeseries.Input)
// 	if err != nil {
// 		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
// 		return
// 	}

// 	symbols := make([]string, len(timeseries.Input.Holdings))
// 	for idx, holding := range timeseries.Input.Holdings {
// 		symbols[idx] = holding.Symbol
// 	}

// 	tickerTimeseriesBySymbol, err := client.GetHistoricalPrices(timeseries.Input.Range, symbols)
// 	if err != nil {
// 		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
// 		return
// 	}

// 	timeseries, err = timeseries.CalculateTimeseries(timeseries.Input.Holdings, tickerTimeseriesBySymbol)
// 	if err != nil {
// 		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
// 		return
// 	}

// 	c.JSON(http.StatusOK, timeseries.Output)
// }

// func RunServer() {
// 	router := gnext.Router()

// 	router.POST("/portfolio-analysis", portfolioAnalysisController)
// 	router.POST("/portfolio-timeseries", portfolioTimeseriesController)

// 	port := fmt.Sprintf(":%s", os.Getenv("PORT"))
// 	if err := router.Run(port); err != nil {
// 		log.Fatal(err)
// 	}
// }
