package main

import (
	"os"
	"web-api/server"

	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	s := server.NewServer(port)
	s.RegisterMiddlewares()
	s.RegisterRoutes()
	s.Start()
}
