import csv
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Callable
from logging import getLogger

from dateutil import tz
from dateutil.parser import parse
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import requests

from swapi.models import CsvFile

logger = getLogger(__file__)

@dataclass
class SwapiCharacter:
    name: str
    height: Optional[int]
    mass: Optional[int]
    hair_color: str
    skin_color: str
    eye_color: str
    birth_year: str
    gender: str
    homeworld: str
    edited: datetime


def _try_parse_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


def _fetch_swapi_characters(
        homeworld_resolver: Callable[[str], str],
        character_processor: Callable[[SwapiCharacter], None]
    ):
    url = settings.SWAPI_SETTINGS.EXTERNAL_URL
    response = requests.get(url)
    data = response.json()
    count = data.get("count", 0)
    if count <= 0:
        logger.info("Fetched [%s] characters from SWAPI.", count)
        return result

    logger.info("Fetching [%s] characters from SWAPI.", count)
    counter = 0
    while True:
        local_results = data["results"]
        counter += len(local_results)
        for swapi_character in local_results:
            homeworld = homeworld_resolver(swapi_character["homeworld"])
            edited_at = parse(swapi_character["edited"])
            character = SwapiCharacter(
                swapi_character.get("name") or '',
                _try_parse_int(swapi_character["height"]),
                _try_parse_int(swapi_character["mass"]),
                swapi_character.get("hair_color") or '',
                swapi_character.get("skin_color") or '',
                swapi_character.get("eye_color") or '',
                swapi_character.get("birth_year") or '',
                swapi_character.get("gender") or '',
                homeworld or '',
                edited_at)
            character_processor(character)
        logger.info("Processed [%s] call. Converted [%s] characters in total.", url, counter)
        url = data.get("next")
        if not url:
            break
        response = requests.get(url)
        data = response.json()
        if data.get("count", 0) <= 0:
            break


@require_http_methods(["POST"])
def fetch(request):
    homeworlds = {}
    def _homeworld_resolver(homeworld_url: str) -> str:
        logger.info("Trying to retrieve [%s] from cache.", homeworld_url)
        homeworld = homeworlds.get(homeworld_url)
        if homeworld:
            logger.info("Found cached value for [%s].", homeworld_url)
            return homeworld
        logger.info("Fetching homeworld from SWAPI: [%s]", homeworld_url)
        response = requests.get(homeworld_url)
        data = response.json()
        homeworld = data["name"]
        homeworlds[homeworld_url] = homeworld
        return homeworld

    filename = 'f' + uuid.uuid4().hex + '.csv'
    now = datetime.utcnow()
    folder = settings.SWAPI_SETTINGS.CSV_DIR
    with open(folder / filename, "w") as fo:
        writer = csv.writer(fo)
        def _character_processor(character: SwapiCharacter):
            writer.writerow([
                character.name,
                character.height or '',
                character.mass or '',
                character.hair_color,
                character.skin_color,
                character.eye_color,
                character.birth_year,
                character.gender,
                character.homeworld,
                character.edited.timestamp(),
            ])

        _fetch_swapi_characters(_homeworld_resolver, _character_processor)

    csv_file = CsvFile(filename=filename, created_at=now)
    csv_file.save()
    return HttpResponse()
