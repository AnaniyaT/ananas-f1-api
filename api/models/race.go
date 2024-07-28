package models

type Race struct {
	Id        string `json:"id"`
	Year      int    `json:"year"`
	Round     int    `json:"round"`
	Name      string `json:"name"`
	Location  string `json:"location"`
	TrackMap  string `json:"trackMap"`
	CircuitId string `json:"circuitId"`
}

func NewRace(
	id string,
	year int,
	round int,
	name string,
	location string,
	trackMap string,
	circuitId string,
) Race {
	return Race{
		Id:        id,
		Year:      year,
		Round:     round,
		Name:      name,
		Location:  location,
		TrackMap:  trackMap,
		CircuitId: circuitId,
	}
}
