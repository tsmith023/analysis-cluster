package controller

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type ControllerRequestor interface {
	PostResult(id string, output interface{}) error
}

type ControllerClient struct {
	*http.Client
	baseUrl string
}

func NewControllerClient(endpoint string) *ControllerClient {
	baseUrl := fmt.Sprintf("http://%v:%v/%v", os.Getenv("CONTROLLER_HOST"), os.Getenv("CONTROLLER_PORT"), endpoint)
	return &ControllerClient{
		&http.Client{},
		baseUrl,
	}
}

func (cc *ControllerClient) PostResult(id string, output interface{}) error {
	b, err := json.Marshal(output)
	if err != nil {
		return fmt.Errorf("%w; Error occurred when marshalling result targetting %s into json for id %s", err, cc.baseUrl, id)
	}
	res, err := http.Post(cc.baseUrl, "application/json", bytes.NewBuffer(b))
	if err != nil {
		return fmt.Errorf("%w; Error occurred when posting results to Controller at %s for id %s", err, cc.baseUrl, id)
	}
	defer res.Body.Close()

	decoder := json.NewDecoder(res.Body)
	var data interface{}
	err = decoder.Decode(&data)

	if res.StatusCode != 200 {
		return fmt.Errorf("%w; Received unsuccessful error code from Controller: %+v", err, data)
	}
	return nil
}
