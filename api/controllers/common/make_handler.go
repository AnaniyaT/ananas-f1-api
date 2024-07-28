package common

import (
	"net/http"
	"web-api/middlewares"
	"web-api/common/types"
)

// MkHndlr is a function that returns an http.Handler from
// a function that takes an http.ResponseWriter and an http.Request as arguments
// and returns an error
func MkHndlr(f types.APIHandlerFunc) http.Handler {
	return middlewares.ErrorHandlerMiddleware(f)
}
