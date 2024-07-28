package types

// FilterOptions is a struct that contains the filter options for a query
// Can be used to filter, order and paginate the results
type FilterOptions struct {
	Filter map[string]string
	OrderBy string
	Limit int
	Page int
}