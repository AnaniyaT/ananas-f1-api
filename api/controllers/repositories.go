package controllers

import (
	"web-api/db"
	"web-api/repositories"
)

var database = db.GetDBInstance()
var raceRepository = repositories.NewRaceRepository(database)
var eventRepository = repositories.NewEventRepository(database)
