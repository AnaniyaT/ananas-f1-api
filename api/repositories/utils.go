package repositories

import (
	"strings"
)


func FormatFilterQuery(filters map[string]string) (string, []interface{}) {
	query := " "
	values := []interface{}{}

	if len(filters) > 0 {
		frags := []string{}
		for key, value := range filters {
			frags = append(frags, key + " = ? ")
			values = append(values, value)
		}

		query += strings.Join(frags, " AND ")
	}

	return query, values
}

