"""Application implementation - Ready controller."""
import logging
from datetime import datetime

import requests
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from redis import Redis
from rq import Queue
from starlette.responses import RedirectResponse

from yretain.app.exceptions import HTTPException
from yretain.config import redis as redis_conf

router = APIRouter(tags=["holidays"],
                   summary="API to Ingest Holiday data", )
# set up Redis Queue
redis_conn = Redis(host=redis_conf.REDIS_HOST,
                   port=redis_conf.REDIS_PORT)

queue = Queue(connection=redis_conn)
log = logging.getLogger(__name__)

# define the holiday data dictionary
holiday_data = {
    'ENG': [],
    'IND': [],
    'IRE': [],
}


# define the Holiday class
class Holiday:
    def __init__(self, name: str, date: str):
        self.name = name
        self.date = datetime.strptime(date, '%Y-%m-%d').date()


# define the process_holidays function
def process_holidays(data, country_code):
    print(f"Processing holiday data for {country_code}...")

    if country_code == 'ENG':
        for holiday in data['england-and-wales']['events']:
            name = holiday['title']
            date = holiday['date']
            holiday_data[country_code].append(Holiday(name, date))
    else:
        for holiday in data:
            name = holiday['name']
            date = holiday['date']
            holiday_data[country_code].append(Holiday(name, date))


# define the is_holiday endpoint
@router.get("/is_holiday/{country_code}/{date}")
async def is_holiday(country_code: str, date: str):
    try:
        holiday_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return {"error": f"Invalid date format: {date}"}

    # find the holiday with the matching date
    holidays = holiday_data.get(country_code)
    if holidays is None:
        return {"error": f"Invalid country code: {country_code}"}

    matching_holiday = next((h for h in holidays if h.date == holiday_date), None)

    if matching_holiday:
        return {"message": f"{matching_holiday.name} is a holiday in {country_code}"}
    else:
        return {"message": f"{date} is not a holiday in {country_code}"}


# define the ingest_holidays endpoint
@router.post("/ingest_holidays/{country_code}")
async def ingest_holidays(country_code: str):
    # check that country code is valid
    # Isle of Man - IM
    # Republic of Ireland - IE
    # England, Wales, Scotland, Northern Ireland - ENG
    # Italy - IT
    # Spain - ES
    if country_code not in ['GB', 'IM', 'IE', 'US', 'AU', 'IT', 'ES']:
        return {"error": f"Invalid country code: {country_code}"}

    # fetch holiday data from the appropriate API
    if country_code == 'ENG':
        url = 'https://www.gov.uk/bank-holidays.json'
    else:
        year = datetime.now().year
        url = f'https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"error": f"Error fetching holiday data for {country_code}: {e}"}

    # queue up the data for processing
    queue.enqueue(process_holidays, data, country_code)

    return {"message": f"Holiday data for {country_code} has been queued for processing"}


# define the ingest_holidays_multiple endpoint
@router.post("/ingest_holidays_all")
async def ingest_holidays_multiple(request: Request):
    # define the list of valid country codes
    valid_country_codes = ['GB', 'IM', 'IE', 'US', 'AU', 'IT', 'ES']

    # loop through the country codes and ingest the holiday data
    for country_code in valid_country_codes:
        url = router.url_path_for("ingest_holidays",
                                  country_code=country_code)
        base_url = str(request.url).split("/ingest_holidays_all")[0]
        full_url = base_url + url

        print(f"Calling {full_url}..")
        response = RedirectResponse(url=full_url)
        print(f"Response: {response} and status code: {response.status_code}")
        # Check the status code of the response
        if response.status_code == 307:
            print(f"Ingesting the data for {country_code}")
        else:
            raise HTTPException(status_code=500,
                                detail=f"Error ingesting holiday data for {country_code}")

    return {"message": "Holiday data has been queued for processing"}


@router.get("/holidays/{country_code}")
async def get_holidays(country_code: str):
    # check that country code is valid
    if country_code not in ['ENG', 'IND', 'IRE']:
        return {"error": f"Invalid country code: {country_code}"}

    # get the list of holidays for the country
    holidays = holiday_data.get(country_code, [])
    holiday_list = [{'name': h.name, 'date': str(h.date)} for h in holidays]

    return {"holidays": holiday_list}


@router.get("/holidays/{country_code}/{start_date}/{end_date}")
async def get_holidays_in_range(country_code: str, start_date: str, end_date: str):
    """
    Querying holidays within a date range
    To allow users to query holidays within a date range,
    we could create another endpoint that takes a start and
    end date as parameters and returns a list of holidays within that range.
    """
    # check that country code is valid
    if country_code not in ['ENG', 'IND', 'IRE']:
        return {"error": f"Invalid country code: {country_code}"}

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return {"error": f"Invalid date format"}

    # get the list of holidays for the country within the specified range
    holidays = holiday_data.get(country_code, [])
    holiday_list = [{'name': h.name, 'date': str(h.date)} for h in holidays if start_date <= h.date <= end_date]

    return {"holidays": holiday_list}


@router.get("/is_holiday/{country_code}/{date}")
async def is_holiday(country_code: str, date: str):
    """
    Check if a given date is a holiday in a given country.

    Parameters
    ----------
    country_code : str
        The ISO-3166 country code for the country to check.
    date : str
        The date to check in the format of "YYYY-MM-DD".

    Returns
    -------
    dict
        A dictionary with a message indicating whether or not the given date is a holiday.
        If the date is a holiday, the message will include the name of the holiday and the country code.
        If the date is not a holiday, the message will indicate that it is not a holiday in the given country.

    Raises
    ------
    None

    Examples
    --------
    >>> is_holiday("ENG", "2023-12-25")
    {"message": "Christmas Day is a holiday in ENG"}

    >>> is_holiday("IRE", "2023-06-05")
    {"message": "2023-06-05 is not a holiday in IRE"}
    """
    try:
        holiday_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return {"error": f"Invalid date format: {date}"}

    # find the holiday with the matching date
    holidays = holiday_data.get(country_code)
    if holidays is None:
        return {"error": f"Invalid country code: {country_code}"}

    matching_holiday = next((h for h in holidays if h.date == holiday_date), None)

    if matching_holiday:
        return {"message": f"{matching_holiday.name} is a holiday in {country_code}"}
    else:
        return {"message": f"{date} is not a holiday in {country_code}"}
