package app

import (
	"analysis/src/app/controller"
	"analysis/src/app/iex"
	"fmt"
	"log"
	"net/http"
	"os"
)

func healthz(w http.ResponseWriter, r *http.Request) {
	fmt.Println(w, "OK")
}

func RunWorker() {
	analysisClient := controller.NewControllerClient(os.Getenv("ANALYSIS_PUBLICATION_ENDPOINT"))
	timeseriesClient := controller.NewControllerClient(os.Getenv("TIMESERIES_PUBLICATION_ENDPOINT"))
	iexClient := iex.NewIexClient()

	nc := returnUnencodedNatsConnection()
	defer nc.Close()

	portfolioAnalysisSubscriber(analysisClient, iexClient, nc)
	fmt.Println(fmt.Sprintf("Worker subscribed to %s for processing requests...", os.Getenv("ANALYSIS_SUBSCRIPTION_TASK")))

	portfolioTimeseriesSubscriber(timeseriesClient, iexClient, nc)
	fmt.Println(fmt.Sprintf("Worker subscribed to %s for processing requests...", os.Getenv("TIMESERIES_SUBSCRIPTION_TASK")))

	fmt.Println(fmt.Sprintf("Server listening on port %s...", os.Getenv("PORT")))
	http.HandleFunc("/healthz", healthz)
	port := fmt.Sprintf(":%s", os.Getenv("PORT"))
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatal(err)
	}
}
