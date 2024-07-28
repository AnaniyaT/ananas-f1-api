package middlewares

import (
	"fmt"
	"net/http"
	"web-api/common/types"
	"web-api/common/errors"
)

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		println(r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

func RemoveTrailingSlashMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if len(r.URL.Path) > 1 && r.URL.Path[len(r.URL.Path)-1] == '/' {
			fmt.Print("Redirecting to ", r.URL.Path[:len(r.URL.Path)-1], "\n")
			http.Redirect(w, r, r.URL.Path[:len(r.URL.Path)-1], http.StatusMovedPermanently)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func ErrorHandlerMiddleware(handler types.APIHandlerFunc) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		err := handler(w, r)
		if err != nil {
			if apiError, ok := err.(errors.APIError); ok {
				http.Error(w, err.Error(), apiError.StatusCode)
			} else {
				http.Error(w, err.Error(), http.StatusInternalServerError)
			}
		}
	})
}
