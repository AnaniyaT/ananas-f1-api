package common

import (
	"net/url"
	"strings"
)

var queryToColumnMap = map[string]string{
	"id":   "id_",
	"type": "type_",
}

func getColumnName(query string) string {
	if val, ok := queryToColumnMap[query]; ok {
		return val
	}
	return query
}

func CreateFilterMapFromQueryParams(params url.Values, allowed []string) map[string]string {
	filterMap := make(map[string]string)

	for _, value := range allowed {
		if val, ok := params[value]; ok {
			columnName := getColumnName(value)
			filterMap[columnName] = val[0]
			if columnName == "type_" {
				filterMap[columnName] = strings.ToUpper(filterMap[columnName])
			} else if columnName == "gmtOffset" && filterMap[columnName][0] != '-' {
				filterMap[columnName] = "+" + strings.Replace(filterMap[columnName], " ", "", 1)
			}
		}
	}

	return filterMap
}
