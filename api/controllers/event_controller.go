package controllers

import (
	"encoding/json"
	"net/http"
	"strings"
	"web-api/common/errors"
	"web-api/common/types"
	"web-api/controllers/common"

	"github.com/gorilla/mux"
)

type EventController struct{}

func NewEventController() EventController {
	return EventController{}
}

func (eventController *EventController) RegisterRoutes(router *mux.Router) {
	subRoute := router.PathPrefix("/events").Subrouter()

	routeHandlerMethod := []types.Triple[string, func(w http.ResponseWriter, r *http.Request) error, string]{
		types.NewTriple("", GetEventsHandler, http.MethodGet),
		types.NewTriple("/next", GetNextEventHandler, http.MethodGet),
		types.NewTriple("/{id}", GetEventHandler, http.MethodGet),
	}

	for _, rhm := range routeHandlerMethod {
		subRoute.Handle(rhm.First, common.MkHndlr(rhm.Second)).Methods(rhm.Third)
	}
}

func GetEventsHandler(w http.ResponseWriter, r *http.Request) error {
	queryParams := r.URL.Query()
	allowed := []string{"raceId", "type", "gmtOffset"}
	filter := common.CreateFilterMapFromQueryParams(queryParams, allowed)

	events, err := eventRepository.FindAll(filter)

	if err != nil {
		return errors.NewNotFoundError()
	}

	w.Header().Set("Content-Type", "application/json")
	if err = json.NewEncoder(w).Encode(events); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}

func GetEventHandler(w http.ResponseWriter, r *http.Request) error {
	params := mux.Vars(r)
	id := params["id"]
	var response interface{}

	splitId := strings.Split(id, "_")
	var err error = nil

	if len(splitId) == 2 {
		response, err = eventRepository.FindByRaceId(id)
	} else if len(splitId) >= 3 {
		response, err = eventRepository.FindById(id)
	} else {
		return errors.NewBadRequestError()
	}

	if err != nil {
		return errors.NewNotFoundError()
	}

	w.Header().Set("Content-Type", "application/json")
	if err = json.NewEncoder(w).Encode(response); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}

func GetNextEventHandler(w http.ResponseWriter, r *http.Request) error {
	nextEvent, err := eventRepository.NextEvent()

	if err != nil {
		return errors.NewNotFoundError()
	}

	w.Header().Set("Content-Type", "application/json")
	if err = json.NewEncoder(w).Encode(nextEvent); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}
