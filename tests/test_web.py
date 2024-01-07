"""The file is for tests, required by the initial statement of work (SoW)

  - работа с сетью: обработка ссылок (GET-запросы) и анализ полученного результата;
"""

from configparser import ConfigParser
from functools import partial
from json import dump as json_dump
from pathlib import Path

from pytest import fixture

from external.client import YandexWeatherAPI
from job import Job
from logger import logger
from scheduler import Scheduler

config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])
TMP = Path(config['tests']['tmp_folder'])
"""
TMP = pytest.TMP
TICK = pytest.TICK
"""
CITIES = {
    "SPETERSBURG": "https://code.s3.yandex.net/async-module/spetersburg-response.json",
    "BEIJING": "https://code.s3.yandex.net/async-module/beijing-response.json",
    "KAZAN": "https://code.s3.yandex.net/async-module/kazan-response.json",
    "NOVOSIBIRSK": "https://code.s3.yandex.net/async-module/novosibirsk-response.json",
    "ABUDHABI": "https://code.s3.yandex.net/async-module/abudhabi-response.json",
    "BUCHAREST": "https://code.s3.yandex.net/async-module/bucharest-response.json",
    "CAIRO": "https://code.s3.yandex.net/async-module/cairo-response.json",

    "GIZA": "https://code.s3.yandex.net/async-module/giza-response.json",
    "MADRID": "https://code.s3.yandex.net/async-module/madrid-response.json",
    "TORONTO": "https://code.s3.yandex.net/async-module/toronto-response.json"
}


def get_url_by_city_name(city_name):
    try:
        return CITIES[city_name]
    except KeyError:
        raise Exception("Please check that city {} exists".format(city_name))


@fixture
def cities_fixture():
    tuple_ = (
        "SPETERSBURG",
        "BEIJING",
        "ABUDHABI",
        "GIZA",
        "MADRID",
        "TORONTO",
    )
    return tuple_


def job_request_weather(city):  # web_job
    """
    This could be a fixture (a function which returns an inner function),
    but in this case we get an error
    "Can't pickle local object 'request_weather.<locals>._request_weather'"
    """
    url = get_url_by_city_name(city)

    try:
        response = YandexWeatherAPI.get_forecasting(url)
        if 'forecasts' not in response:
            raise Exception("Response does not have the forecast data")
    except Exception as e:
        warning = f"city {city} is skipped because of exception: {e}"
        raise Exception(warning)
    else:
        if not TMP.exists():
            TMP.mkdir(parents=True)

        raw_json_path = TMP / f'{city}.json'
        with open(raw_json_path, 'w+') as raw_json:
            json_dump(response, raw_json)
        result = f"Request is written in the file {raw_json_path.stem}"
        logger.debug(result)

        return(result)


def test_web_job1():
    job = Job(
        [partial(job_request_weather, "SPETERSBURG")],
    )
    scheduler = Scheduler(pool_size=6)
    scheduler.schedule(job)
    scheduler.run()
    scheduler.join()


def test_web_job(cities_fixture):
    cities = cities_fixture
    scheduler = Scheduler(pool_size=6)
    for city in cities:
        job = Job(
            [partial(job_request_weather, city)],
        )
        scheduler.schedule(job)
    scheduler.run()
    scheduler.join()
