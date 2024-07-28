package controllers

import "github.com/gorilla/mux"

type ControllerInterface interface {
	RegisterRoutes(r *mux.Router)
}
