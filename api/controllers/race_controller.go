package controllers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"web-api/common/errors"
	"web-api/common/types"
	"web-api/controllers/common"

	"github.com/gorilla/mux"
)

type RaceController struct{}

func NewRaceController() RaceController {
	return RaceController{}
}

func (raceController *RaceController) RegisterRoutes(router *mux.Router) {
	subRoute := router.PathPrefix("/races").Subrouter()

	routeHandlerMethod := []types.Triple[string, func(w http.ResponseWriter, r *http.Request) error, string]{
		types.NewTriple("", GetRacesHandler, http.MethodGet),
		types.NewTriple("/next", GetNextRaceHandler, http.MethodGet),
		types.NewTriple("/{idOrYear}", GetRacesByIdOrYearHandler, http.MethodGet),
		types.NewTriple("/{raceId}/events", GetRaceEventsHandler, http.MethodGet),
		types.NewTriple("/{year}/{round}", GetRaceByYearAndRoundHandler, http.MethodGet),
	}

	for _, rhm := range routeHandlerMethod {
		subRoute.Handle(rhm.First, common.MkHndlr(rhm.Second)).Methods(rhm.Third)
	}

}

func GetRacesHandler(w http.ResponseWriter, r *http.Request) error {
	queryParams := r.URL.Query()
	allowed := []string{"circuitId", "location"}
	filter := common.CreateFilterMapFromQueryParams(queryParams, allowed)

	races, err := raceRepository.FindAll(filter)
	if err != nil {
		return errors.NewNotFoundError()
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(races)

	return nil
}

func GetRacesByIdOrYearHandler(w http.ResponseWriter, r *http.Request) error {
	params := mux.Vars(r)
	queryParams := r.URL.Query()
	idOrYear := params["idOrYear"]

	var response interface{}
	var err error = nil

	if len(idOrYear) == 4 {
		var id int
		id, err = strconv.Atoi(idOrYear)
		if err != nil {
			return errors.NewBadRequestError()
		}
		allowed := []string{"location", "circuitId"}
		filter := common.CreateFilterMapFromQueryParams(queryParams, allowed)
		response, err = raceRepository.FindByYear(id, filter)
	} else {
		response, err = raceRepository.FindById(idOrYear)
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

func GetRaceByYearAndRoundHandler(w http.ResponseWriter, r *http.Request) error {
	params := mux.Vars(r)
	year := params["year"]
	round := params["round"]

	raceId := year + "_" + round

	race, err := raceRepository.FindById(raceId)

	if err != nil {
		return errors.NewNotFoundError()
	}

	w.Header().Set("Content-Type", "application/json")
	if err = json.NewEncoder(w).Encode(race); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}

func GetRaceEventsHandler(w http.ResponseWriter, r *http.Request) error {
	params := mux.Vars(r)
	raceId := params["raceId"]

	raceEvents, err := eventRepository.FindByRaceId(raceId)

	if err != nil {
		return errors.NewNotFoundError()
	}

	w.Header().Set("Content-Type", "application/json")
	if err = json.NewEncoder(w).Encode(raceEvents); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}

func GetNextRaceHandler(w http.ResponseWriter, r *http.Request) error {
	nextEvent, err := eventRepository.NextEvent()
	if err != nil {
		return errors.NewNotFoundError()
	}

	raceId := nextEvent.RaceId

	nextRace, err := raceRepository.FindById(raceId)
	if err != nil {
		return errors.NewNotFoundError()
	}

	w.Header().Set("Content-Type", "application/json")
	if err = json.NewEncoder(w).Encode(nextRace); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}
