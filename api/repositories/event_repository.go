package repositories

import (
	"database/sql"
	"sort"
	"time"
	"web-api/models"
)

type EventRepository struct {
	DB        *sql.DB
	tableName string
}

func NewEventRepository(db *sql.DB) EventRepository {
	return EventRepository{DB: db, tableName: "events"}
}

func getEventsFromRows(rows *sql.Rows) ([]models.Event, error) {
	defer rows.Close()

	events := []models.Event{}

	for rows.Next() {
		var id string
		var raceId string
		var title string
		var date string
		var eventType string
		var time string
		var gmtOffset string

		err := rows.Scan(&raceId, &title, &date, &eventType, &time, &gmtOffset, &id)

		if err != nil {
			return nil, err
		}

		event := models.NewEvent(id, raceId, title, date, eventType, time, gmtOffset)
		events = append(events, event)
	}

	return events, nil

}

func (r *EventRepository) FindAll(filters ...map[string]string) ([]models.Event, error) {
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

	return getEventsFromRows(rows)
}

func (r *EventRepository) FindById(id string) (models.Event, error) {
	query := "SELECT * FROM " + r.tableName + " WHERE id_ = ?"
	row := r.DB.QueryRow(query, id)

	var raceId string
	var title string
	var date string
	var eventType string
	var time string
	var gmtOffset string

	err := row.Scan(&raceId, &title, &date, &eventType, &time, &gmtOffset, &id)

	if err != nil {
		return models.Event{}, err
	}

	return models.NewEvent(id, raceId, title, date, eventType, time, gmtOffset), nil
}

func (r *EventRepository) FindByRaceId(raceId string, filters ...map[string]string) ([]models.Event, error) {
	query := "SELECT * FROM " + r.tableName + " WHERE raceId = ?"
	values := []interface{}{raceId}

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

	return getEventsFromRows(rows)
}

func (r *EventRepository) NextEvent() (models.Event, error) {
	curTime := time.Now().UTC()
	formattedDate := curTime.Format("2006-01-02")
	timeLayout := "2006-01-02 15:04:05"

	query := "SELECT * FROM " + r.tableName + " WHERE date >= ? ORDER BY date ASC LIMIT 3"

	rows, err := r.DB.Query(query, formattedDate)

	if err != nil {
		return models.Event{}, err
	}

	events, err := getEventsFromRows(rows)

	if err != nil {
		return models.Event{}, err
	}

	sort.Slice(events, func(i, j int) bool {
		return events[i].Time < events[j].Time
	})

	for _, event := range events {
		formattedDateTime := event.Date + " " + event.Time
		eventTime, err := time.Parse(timeLayout, formattedDateTime)

		if err != nil {
			return models.Event{}, err
		}

		if eventTime.After(curTime.Add(time.Hour * -2)) {
			return event, nil
		}
	}

	return models.Event{}, nil
}
