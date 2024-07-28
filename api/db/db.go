package db

import (
	"database/sql"
	"os"

	"github.com/joho/godotenv"
	_ "modernc.org/sqlite"
)

var db *sql.DB

func GetDBInstance() *sql.DB {
	if db == nil {
		godotenv.Load()
		dbPath := os.Getenv("DB_PATH")
		if dbPath == "" {
			dbPath = "./f1db.sqlite3"
		}

		db_, err := sql.Open("sqlite", dbPath)
		if err != nil {
			panic(err)
		}

		db = db_
	}

	return db
}
