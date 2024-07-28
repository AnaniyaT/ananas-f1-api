package repositories

import (
	"database/sql"
	"web-api/models"
)

type RaceRepository struct {
	DB        *sql.DB
	tableName string
}

func NewRaceRepository(db *sql.DB) RaceRepository {
	return RaceRepository{DB: db, tableName: "races"}
}

func getRacesFromRows(rows *sql.Rows) ([]models.Race, error) {
	defer rows.Close()

	races := []models.Race{}

	for rows.Next() {
		var id string
		var year int
		var round int
		var name string
		var location string
		var trackMap string
		var circuitId string

		err := rows.Scan(&year, &round, &name, &location, &trackMap, &circuitId, &id)

		if err != nil {
			return nil, err
		}

		race := models.NewRace(id, year, round, name, location, trackMap, circuitId)
		races = append(races, race)
	}

	return races, nil

}

func (r *RaceRepository) FindAll(filters ...map[string]string) ([]models.Race, error) {
	query := "SELECT * FROM " + r.tableName
	var values []interface{}

	if len(filters) > 0 && len(filters[0]) > 0 {
		query += " WHERE "
		queryFrag, v := FormatFilterQuery(filters[0])
		query += queryFrag
		values = v
	}

	rows, err := r.DB.Query(query, values...)

	if err != nil {
		return nil, err
	}

	return getRacesFromRows(rows)
}

func (r *RaceRepository) FindById(id string) (models.Race, error) {
	query := "SELECT * FROM " + r.tableName + " WHERE id_ = ?"
	row := r.DB.QueryRow(query, id)

	var year int
	var round int
	var name string
	var location string
	var trackMap string
	var circuitId string

	err := row.Scan(&year, &round, &name, &location, &trackMap, &circuitId, &id)

	if err != nil {
		return models.Race{}, err
	}

	return models.NewRace(id, year, round, name, location, trackMap, circuitId), nil
}

func (r *RaceRepository) FindByCircuitId(circuitId string) ([]models.Race, error) {
	query := "SELECT * FROM " + r.tableName + " WHERE circuitId = ?"
	rows, err := r.DB.Query(query, circuitId)

	if err != nil {
		return nil, err
	}

	return getRacesFromRows(rows)
}

func (r *RaceRepository) FindByYear(year int, filters ...map[string]string) ([]models.Race, error) {
	query := "SELECT * FROM " + r.tableName + " WHERE year = ?"
	values := []interface{}{year}

	if len(filters) > 0 && len(filters[0]) > 0 {
		query += " AND "
		queryFrag, v := FormatFilterQuery(filters[0])
		query += queryFrag
		values = append(values, v...)
	}

	rows, err := r.DB.Query(query, values...)

	if err != nil {
		return nil, err
	}

	return getRacesFromRows(rows)
}
