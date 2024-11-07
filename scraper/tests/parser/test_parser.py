import unittest
from unittest.mock import patch
from hamcrest import (
    assert_that,
    equal_to,
    starts_with,
    contains_exactly,
    has_entries,
    instance_of,
    all_of,
    has_length,
)

from scraper.Parser import Parser
from tests.infrastructure.mocks import MockRequests
from tests.infrastructure.matchers import (
    is_circuit,
    is_event,
    is_results_table,
    has_unique_values,
)
import asyncio


mockRequests = MockRequests(config="tests/test_data/config/2023_config.json")


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = Parser()
        self.year = 2023

    @patch("requests.get", new=mockRequests.get)
    def test_get_race_should_return_all_race_urls(self):
        urls = asyncio.run(self.parser.getRaceUrls(self.year, use_cache=False))

        assert_that(len(urls), equal_to(23))
        assert_that(
            urls,
            contains_exactly(
                *(
                    starts_with("https://www.formula1.com/en/racing/2023")
                    for _ in range(23)
                )
            ),
        )

    @patch("requests.get", new=mockRequests.get)
    def test_get_circuit_should_return_circuit_info(self):
        url = "https://www.formula1.com/en/racing/2023/brazil"
        circuit = asyncio.run(self.parser.getCircuit(url))

        assert_that(circuit, is_circuit())

    @patch("requests.get", new=mockRequests.get)
    def test_get_race_should_return_race_info(self):
        url = "https://www.formula1.com/en/racing/2023/brazil"
        round_ = 4
        race = asyncio.run(self.parser.getRace(url, round_))

        assert_that(
            race,
            has_entries(
                {
                    "f1Id": instance_of(str),
                    "year": 2023,
                    "round_": 4,
                    "name": "FORMULA 1 STC SAUDI ARABIAN GRAND PRIX 2023",
                    "location": "Jeddah, Saudi Arabia",
                    "trackMap": starts_with("https://media.formula1.com"),
                    "circuit": is_circuit(),
                    "events": contains_exactly(*(is_event() for _ in range(5))),
                }
            ),
        )

    @patch("requests.get", new=mockRequests.get)
    def test_get_practice_1_event_results_should_return_full_standings(self):
        url = "https://www.formula1.com/en/results/2023/races/1224/brazil/practice/1"
        eventId = "2024_10_PRACTICE_1"
        results = asyncio.run(self.parser.getEventResults(url, eventId))

        assert_that(
            results,
            all_of(
                is_results_table(),
                contains_exactly(
                    *(
                        has_entries(
                            {
                                "eventId": eventId,
                                "eventTitle": "Practice 1",
                                "position": instance_of(str),
                                "driverNumber": instance_of(str),
                                "driverName": instance_of(str),
                                "constructorName": instance_of(str),
                                "time": instance_of(str),
                                "gap": instance_of(str),
                                "laps": instance_of(str),
                            }
                        )
                        for _ in range(20)
                    )
                ),
            ),
        )

    @patch("requests.get", new=mockRequests.get)
    def test_get_qualifying_event_results_should_return_full_standings(self):
        url = "https://www.formula1.com/en/results/2023/races/1224/brazil/qualifying"
        eventId = "2024_10_QUALIFYING"
        results = asyncio.run(self.parser.getEventResults(url, eventId))

        assert_that(
            results,
            all_of(
                is_results_table(),
                contains_exactly(
                    *(
                        has_entries(
                            {
                                "eventId": eventId,
                                "eventTitle": "QUALIFYING",
                                "position": instance_of(str),
                                "driverNumber": instance_of(str),
                                "driverName": instance_of(str),
                                "constructorName": instance_of(str),
                                "q1": instance_of(str),
                                "q2": instance_of(str),
                                "q3": instance_of(str),
                                "laps": instance_of(str),
                            }
                        )
                        for _ in range(20)
                    )
                ),
            ),
        )

    @patch("requests.get", new=mockRequests.get)
    def test_get_race_event_results_should_return_full_standings(self):
        url = "https://www.formula1.com/en/results/2023/races/1224/brazil/race-result"
        eventId = "2024_10_RACE"
        results = asyncio.run(self.parser.getEventResults(url, eventId))

        assert_that(
            results,
            all_of(
                is_results_table(),
                contains_exactly(
                    *(
                        has_entries(
                            {
                                "eventId": eventId,
                                "eventTitle": "RACE",
                                "position": instance_of(str),
                                "driverNumber": instance_of(str),
                                "driverName": instance_of(str),
                                "constructorName": instance_of(str),
                                "time": instance_of(str),
                                "points": instance_of(str),
                                "laps": instance_of(str),
                            }
                        )
                        for _ in range(20)
                    )
                ),
            ),
        )

    def test_get_driver_standings_should_return_full_standings(self):
        standings = asyncio.run(self.parser.getDriverStandings(2023))

        assert_that(
            standings,
            all_of(
                has_unique_values("position"),
                has_unique_values("driverName"),
                contains_exactly(
                    *(
                        has_entries(
                            {
                                "position": instance_of(str),
                                "driverName": instance_of(str),
                                "nationality": all_of(instance_of(str), has_length(3)),
                                "constructorName": instance_of(str),
                                "points": instance_of(str),
                            }
                        )
                        for _ in range(22)
                    )
                ),
            ),
        )

    def test_get_constructor_standings_should_return_full_standings(self):
        standings = asyncio.run(self.parser.getConstructorStandings(2023))

        assert_that(
            standings,
            all_of(
                has_unique_values("position"),
                contains_exactly(
                    *(
                        has_entries(
                            {
                                "position": instance_of(str),
                                "constructorName": instance_of(str),
                                "points": instance_of(str),
                            }
                        )
                        for _ in range(10)
                    )
                ),
            ),
        )
