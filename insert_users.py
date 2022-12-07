import datetime
import http.client
import json
import random
from pathlib import Path
from random import randint

import indian_names
import ray

ray.init()

headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjFkOTU2OGQtNjQ3ZS00NTM4LWI3NTgtZDk1NDUwZWNmMTk1IiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJleHAiOjE2NzA0MzI5Mjh9.j_Qx4-kRMC9xFVEg0egnsui8zSpE23VPLlBFDIJ0pPA',
    'Content-Type': 'application/json'
}


def random_with_N_digits(n, i):
    random.seed(randint(i, 101))
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def insert_customer(i):
    conn = http.client.HTTPConnection("127.0.0.1", 8001)
    first_name = indian_names.get_first_name()
    last_name = indian_names.get_last_name()
    phone = random_with_N_digits(10, i)
    cities = ["Armagh", "Belfast", "Derry" "Newry", "Lisburn", "Bath", "London",
              "Lancaster",
              "Leeds",
              "Leicester",
              "Lichfield",
              "Lincoln",
              "Liverpool",
              "City of London",
              "Manchester",
              "Milton Keynes",
              "Newcastle upon Tyne",
              "Norwich",
              "Nottingham",
              "Oxford", ]
    payload = json.dumps({
        "phone_number": f"{phone}",
        "name": f"{first_name} {last_name}",
        "email": f"{first_name}.{phone}@gmail.com",
        "city": random.choice(cities)
    })
    conn.request("POST", "/customers", payload, headers)
    res = conn.getresponse()
    if res.status != 200:
        data = res.read()
        print(f"Error on {payload} err- {data}")
    else:
        data = res.read()
        print(data.decode("utf-8"))
        conn.close()
        return data


def insert_customer_activity(user, i=1):
    now = datetime.datetime.now()

    updated = now - datetime.timedelta(days=randint(i, 20),
                                       minutes=randint(i, 15),
                                       seconds=randint(i, 10))
    updated = updated.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    payload = json.dumps({
        "phone_number": user,
        "updated": updated
    })

    conn = http.client.HTTPConnection("127.0.0.1", 8001)

    conn.request("POST", "/customers_activity", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    conn.close()


@ray.remote
def f(user, i):
    return insert_customer_activity(user, i)


def create_activity(user):
    # Better approach: parallelism because the tasks are executed in parallel.
    refs = []
    for i in range(10):
        refs.append(f.remote(user, i))

    parallel_returns = ray.get(refs)
    print(parallel_returns)


import pandas as pd
from gunicorn.util import getcwd

ROOT_DIR = Path(getcwd())
df = pd.read_json(f"{ROOT_DIR}/users.json", lines=True)
df.apply(lambda row: create_activity(row['phone_number']), axis=1)
