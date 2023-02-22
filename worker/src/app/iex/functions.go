package iex

import (
	"fmt"
	"net/http"
	"os"
	"strings"
)

func NewIexClient() *IexClient {
	baseUrl := fmt.Sprintf("http://%v:%v", os.Getenv("IEX_HOST"), os.Getenv("IEX_PORT"))
	return &IexClient{
		&http.Client{},
		baseUrl,
	}
}

func createSymbols(symbols []string) string {
	return strings.Join(symbols[:], "&symbols=")
}
