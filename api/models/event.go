package models

type Event struct {
	Id        string `json:"id"`
	RaceId    string `json:"raceId"`
	Title     string `json:"title"`
	Date      string `json:"date"`
	Type      string `json:"type"`
	Time      string `json:"time"`
	GmtOffset string `json:"gmtOffset"`
}

func NewEvent(id string, raceId string, title string, date string, eventType string, time string, gmtOffset string) Event {
	return Event{
		Id:        id,
		RaceId:    raceId,
		Title:     title,
		Date:      date,
		Type:      eventType,
		Time:      time,
		GmtOffset: gmtOffset,
	}
}
