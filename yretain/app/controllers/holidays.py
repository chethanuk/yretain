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
import io
import pandas as pd
import boto3
import sqlalchemy
from sqlalchemy.pool import QueuePool
import requests

ISTEMPMAIL_API_KEY = "53u2bN5W19qoQPp5k2jvNapQWAtgTwPA"
ISTEMPMAIL_API_URL = "https://www.istempmail.com/api/check"

# To get list of buckets present in AWS using S3 client
s3 = boto3.client('s3')
AWS_S3_BUCKET = "yathena"

# RDS database configuration
DB_USER = "admin"
DB_PASSWORD = "wi8NTq7yQ8DQCz8"
DB_NAME = "yretain"
DB_HOST = "database-1.cujnaavuyxu8.us-east-1.rds.amazonaws.com"
DB_PORT = 3306

# SQLAlchemy connection engine
db_engine = sqlalchemy.create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    poolclass=QueuePool,
    pool_recycle=3600,
    pool_size=10
)


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


def is_valid_email(email: str) -> bool:
    """
    Checks if an email address is valid using the istempmail.com API.

    Args:
        email (str): The email address to check.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    domain = email.split("@")[1]
    url = f"{ISTEMPMAIL_API_URL}/{ISTEMPMAIL_API_KEY}/{domain}"
    response = requests.get(url)
    response.raise_for_status()  # raise an exception if the request was unsuccessful
    data = response.json()
    return not data["blocked"]


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


@router.get("/gen_codes/{country_code}/{date}")
async def gen_codes(country_code: str, date: str):
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
        HOLIDAY_3 = "INSTANT_10_UPTO_100"
        HOLIDAY_5 = "INSTANT_20_UPTO_100"
        HOLIDAY_8 = "INSTANT_30_UPTO_100"
        HOLIDAY_10 = "INSTANT_40_UPTO_100"
    else:
        HOLIDAY_3 = "INSTANT_15_UPTO_100"
        HOLIDAY_5 = "INSTANT_25_UPTO_100"
        HOLIDAY_8 = "INSTANT_35_UPTO_100"
        HOLIDAY_10 = "INSTANT_45_UPTO_100"

    query = f"""
    WITH last_activity AS (
        select phone_number,
            MAX(updated) AS last_order_time,
            CURRENT_TIMESTAMP as now
        from yretain.customers_activity
        GROUP BY phone_number
    ),
    customer_inactive AS (
        SELECT *,
               datediff(now, last_order_time) as inactive_days
        FROM last_activity
    )
    SELECT *,
        CASE
            WHEN inactive_days < 3 THEN '{HOLIDAY_3}'
            WHEN inactive_days < 5 THEN '{HOLIDAY_5}'
            WHEN inactive_days < 8 THEN '{HOLIDAY_8}'
            WHEN inactive_days < 10 THEN '{HOLIDAY_10}'
        END AS DISCOUNTS
    FROM customer_inactive;
    """

    cus_discounts_df = pd.read_sql(query, db_engine)
    print(cus_discounts_df.head())

    full_s3_path = f"s3://{AWS_S3_BUCKET}/reports/customers/discounts_latest.csv"
    with io.StringIO() as csv_buffer:
        cus_discounts_df.to_csv(csv_buffer, index=False)

        response = s3.put_object(
            Bucket=AWS_S3_BUCKET,
            Key="reports/customers/discounts_latest.csv",
            Body=csv_buffer.getvalue()
        )

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            print(f"Successful S3 put_object response. Status - {status}")
        else:
            print(f"Unsuccessful S3 put_object response. Status - {status}")

    # TODO Convert dataframe to dict and call pdf API to generate pdf
    # TODO Upload pdf to S3
    email = "chethan.u7@gmail.com"
    if is_valid_email(email):
        print(f"{email} is a valid email address - Sending email")
        
        MAILGUN_URL = "https://api.mailgun.net/v3/sandbox65061d43c1e546649db73f3fbe845445.mailgun.org/messages"
        API_KEY = "730d843b3d6d0e352757a9d188471e1c-2cc48b29-b0f2dec9"
        FROM_EMAIL = "Mailgun Sandbox <postmaster@sandbox65061d43c1e546649db73f3fbe845445.mailgun.org>"
        TO_EMAIL = f"Chethan Umesha <{email}>"
        print(TO_EMAIL)
        SUBJECT = "Coupons report email"
        MESSAGE = f"Congratulations Chethan Umesha, new coupons is generated its in location: {full_s3_path}!"
        
        try:
            response = requests.post(MAILGUN_URL,
                auth=("api", API_KEY),
                data={
                    "from": FROM_EMAIL,
                    "to": TO_EMAIL,
                    "subject": SUBJECT,
                    "text": MESSAGE
                }
            )
            response.raise_for_status()  # raises an exception if the status code is not 2xx
            print(f"Email sent successfully: {response}")
            # return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending email: {e}")
            # return False
        
    else:
        print(f"{email} is not a valid email address - Can't send email")

    return full_s3_path
