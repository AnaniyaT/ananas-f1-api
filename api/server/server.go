package server

import (
	"fmt"
	"net/http"
	"web-api/controllers"
	"web-api/middlewares"

	"github.com/gorilla/mux"
)

type Server struct {
	Port        string
	Router      *mux.Router
	Controllers []controllers.ControllerInterface
}

func NewServer(port string) Server {
	raceController := controllers.NewRaceController()
	eventController := controllers.NewEventController()
	controllers_ := []controllers.ControllerInterface{
		&raceController,
		&eventController,
	}

	return Server{Port: port, Router: mux.NewRouter(), Controllers: controllers_}
}

func (s *Server) RegisterRoutes() {
	for _, controller := range s.Controllers {
		controller.RegisterRoutes(s.Router)
	}
}

func (s *Server) RegisterMiddlewares() {
	s.Router.Use(middlewares.LoggingMiddleware)
}

func (s *Server) Start() {
	fmt.Printf("Server running on port %v\n", s.Port)
	err := http.ListenAndServe(
		fmt.Sprintf("0.0.0.0:%v", s.Port),
		middlewares.RemoveTrailingSlashMiddleware(s.Router),
	)
	if err != nil {
		panic(err)
	}
}
