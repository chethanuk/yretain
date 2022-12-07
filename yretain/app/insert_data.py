import datetime
import http.client
import json
import random
from pathlib import Path
from random import randint

headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjFkOTU2OGQtNjQ3ZS00NTM4LWI3NTgtZDk1NDUwZWNmMTk1IiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJleHAiOjE2NzA0MzI5Mjh9.j_Qx4-kRMC9xFVEg0egnsui8zSpE23VPLlBFDIJ0pPA',
    'Content-Type': 'application/json'
}


# INSERT Coupons
def insert_coupons():
    for i in [3, 5, 7, 10, 15, 25]:
        for amount in [100, 200, 300, 400, 500]:
            payload = json.dumps({
                "code": f"INSTANT_{i}_UPTO_{amount}",
                "message": f"Get Instant {i}% Discount upto {amount} euros",
                "expiry_days": round(20 / i)
            })
            conn = http.client.HTTPConnection("127.0.0.1", 8001)
            conn.request("POST", "/coupons", payload, headers)
            res = conn.getresponse()
            data = res.read()
            print(data.decode("utf-8"))


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def insert_customers(num_customers=100):
    # pip install indian-names
    import indian_names
    for i in range(1, num_customers):
        conn = http.client.HTTPConnection("127.0.0.1", 8001)
        first_name = indian_names.get_first_name()
        last_name = indian_names.get_last_name()
        phone = random_with_N_digits(10)
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
        data = res.read()
        print(data.decode("utf-8"))
        conn.close()


# insert_coupons()
# insert_customers(4000)

def insert_customer_activity(i=1):
    import pandas as pd
    from gunicorn.util import getcwd

    ROOT_DIR = Path(getcwd()).parent.parent
    df = pd.read_json(f"{ROOT_DIR}/users.json", lines=True)

    now = datetime.datetime.now()

    updated = now - datetime.timedelta(days=random.seed(randint(i, 20)),
                                       minutes=random.seed(randint(i, 15)),
                                       seconds=random.seed(randint(i, 10)))
    updated = updated.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    payload = json.dumps({
        "phone_number": "4076709883",
        "updated": updated
    })

    conn = http.client.HTTPConnection("127.0.0.1", 8001)

    conn.request("POST", "/customers_activity", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    conn.close()


insert_customer_activity()
