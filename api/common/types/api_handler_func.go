package types

import (
	"net/http"
)

type APIHandlerFunc func(w http.ResponseWriter, r *http.Request) error
