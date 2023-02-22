package app

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/nats-io/nats.go"
)

func returnEncodedNatsConnection() (*nats.EncodedConn, *nats.Conn) {
	var err error
	var nc *nats.Conn
	uri := os.Getenv("NATS_URI")
	for i := 0; i < 5; i++ {
		nc, err = nats.Connect(uri, nats.ErrorHandler(func(nc *nats.Conn, s *nats.Subscription, err error) {
			if s != nil {
				log.Printf("Async error in %q/%q: %v", s.Subject, s.Queue, err)
			} else {
				log.Printf("Async error outside subscription: %v", err)
			}
		}))
		if err == nil {
			break
		}

		fmt.Println("Waiting before connecting to NATS at:", uri)
		time.Sleep(1 * time.Second)
	}
	if err != nil {
		log.Fatal("Error establishing connection to NATS:", err)
	}
	fmt.Println("Connected to NATS at:", nc.ConnectedUrl())

	ec, err := nats.NewEncodedConn(nc, nats.JSON_ENCODER)
	if err != nil {
		log.Fatal("Error establishing encoded connection to NATS:", err)
	}
	fmt.Println("Encoded the connection to subscribe and publish JSON at:", nc.ConnectedUrl())
	return ec, nc
}

func returnUnencodedNatsConnection() *nats.Conn {
	var err error
	var nc *nats.Conn
	uri := os.Getenv("NATS_URI")
	for i := 0; i < 5; i++ {
		nc, err = nats.Connect(uri, nats.ErrorHandler(func(nc *nats.Conn, s *nats.Subscription, err error) {
			if s != nil {
				log.Printf("Async error in %q/%q: %v", s.Subject, s.Queue, err)
			} else {
				log.Printf("Async error outside subscription: %v", err)
			}
		}))
		if err == nil {
			break
		}

		fmt.Println("Waiting before connecting to NATS at:", uri)
		time.Sleep(1 * time.Second)
	}
	if err != nil {
		log.Fatal("Error establishing connection to NATS:", err)
	}
	fmt.Println("Connected to NATS at:", nc.ConnectedUrl())

	return nc
}
