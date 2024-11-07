import re
from collections.abc import Iterable
from typing import Counter
from hamcrest import (
    has_entries,
    instance_of,
    ends_with,
    all_of,
    has_length,
    any_of,
    starts_with,
)

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description


class IsMatchingPattern(BaseMatcher):
    def __init__(self, pattern: str, message: str):
        self.regex = pattern
        self.message = message

    def _matches(self, string):
        return bool(re.match(self.regex, string))

    def describe_to(self, description):
        description.append_text(self.message)

    def describe_mismatch(self, item, description):
        description.append_text(f"was '{item}'")


class IsUnique(BaseMatcher):
    def __init__(self, key: str):
        self.key = key
        
    def _matches(self, sequence: Iterable[any]) -> bool:
        vals = [item[self.key] for item in sequence if item[self.key] != "NC"]
        return len(set(vals)) == len(vals)
    
    def describe_to(self, description: Description):
        description.append_text(f"items of the sequence having a unique value for the key {self.key}")
        
    def describe_match(self, item: any, description: Description) -> None:
        counts = Counter(i[self.key] for i in item)
        dups = [key for key in counts if counts[key] > 1]
        description.append_text(f"was found with duplicates {str(dups)}")


def is_valid_date():
    return IsMatchingPattern(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        message="a valid ISO 8601 date string ending with 'Z'"
    )
    

def has_unique_values(key: str):
    return IsUnique(key)


def is_circuit():
    return has_entries(
        {
            "name": instance_of(str),
            "firstGrandPrix": all_of(
                instance_of(str),
                has_length(4),
                any_of(starts_with("19"), starts_with("20")),
            ),
            "numberOfLaps": instance_of(str),
            "length": ends_with("km"),
            "raceDistance": ends_with("km"),
            "lapRecord": instance_of(str),
        }
    )


def is_event():
    return has_entries(
        {
            "title": instance_of(str),
            "startDate": is_valid_date(),
            "endDate": is_valid_date(),
            "resultLink": starts_with("https://www.formula1.com/en"),
        }
    )


def is_results_table():
    return all_of(
        IsUnique("position"),
        IsUnique("driverNumber"),
        IsUnique("driverName")
    )
