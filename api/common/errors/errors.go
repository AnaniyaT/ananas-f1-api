package errors

import (
	"net/http"
)

type APIError struct {
	Message    string `json:"message"`
	StatusCode int    `json:"status_code"`
}

func NewAPIError(message string, statusCode int) APIError {
	return APIError{Message: message, StatusCode: statusCode}
}

func (e APIError) Error() string {
	return e.Message
}

func NewNotFoundError() APIError {
	return NewAPIError("Requested resource not found.", http.StatusNotFound)
}

func NewNotFoundErrorWithMessage(message string) APIError {
	return NewAPIError(message, http.StatusNotFound)
}

func NewInternalServerError() APIError {
	return NewAPIError("Internal server error.", http.StatusInternalServerError)
}

func NewInternalServerErrorWithMessage(message string) APIError {
	return NewAPIError(message, http.StatusInternalServerError)
}

func NewBadRequestError() APIError {
	return NewAPIError("Bad Request!", http.StatusBadRequest)
}

func NewBadRequestErrorWithMessage(message string) APIError {
	return NewAPIError(message, http.StatusBadRequest)
}

func NewUnauthorizedError() APIError {
	return NewAPIError("Unauthorized", http.StatusUnauthorized)
}

func NewUnauthorizedErrorWithMessage(message string) APIError {
	return NewAPIError(message, http.StatusUnauthorized)
}
