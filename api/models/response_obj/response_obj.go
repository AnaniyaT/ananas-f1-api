package responseobj

import (
	"encoding/json"
	"net/http"
	"web-api/common/errors"
)

type SingleResponse struct {
	Data interface{} `json:"data"`
}

func NewSingleResponse(data interface{}) SingleResponse {
	return SingleResponse{Data: data}
}

func SendSingleResponse(w http.ResponseWriter, data interface{}) error {
	w.Header().Set("Content-Type", "application/json")

	response := NewSingleResponse(data)
	if err := json.NewEncoder(w).Encode(response); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}

type PaginatedResponse struct {
	Data            []interface{} `json:"data"`
	PreviousPageKey string        `json:"previousPageKey"`
	NextPageKey     string        `json:"nextPageKey"`
}

func NewPaginatedResponse(data []interface{}, previousPageKey string, nextPageKey string) PaginatedResponse {
	return PaginatedResponse{Data: data, PreviousPageKey: previousPageKey, NextPageKey: nextPageKey}
}

func SendPaginatedResponse(w http.ResponseWriter, data []interface{}, previousPageKey string, nextPageKey string) error {
	w.Header().Set("Content-Type", "application/json")

	response := NewPaginatedResponse(data, previousPageKey, nextPageKey)
	if err := json.NewEncoder(w).Encode(response); err != nil {
		return errors.NewInternalServerError()
	}

	return nil
}
