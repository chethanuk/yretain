Technical Software Specification - Holiday API Endpoint
Objective

The objective of this project is to create two API endpoints in Python using FastAPI framework. The first endpoint will ingest holiday data from public APIs for England, Scotland, India, Ireland and other UK countries, and use Redis Queue to perform the task asynchronously. The second endpoint will allow users to check if today is a holiday in a given country.

Technologies
Python 3.x
FastAPI framework
Redis Queue
Requests library for making HTTP requests
API Endpoints
Endpoint 1 - Ingest Holiday Data

This endpoint will ingest holiday data from public APIs for England, Scotland, India, Ireland and other UK countries, and use Redis Queue to perform the task asynchronously.

HTTP Method

POST

Endpoint URL
arduino
Copy code
http://<hostname>/ingest_holidays

Request Parameters

None

Response
HTTP status code 200 if the task is successfully added to Redis Queue.
HTTP status code 500 if there is an error adding the task to Redis Queue.
Endpoint Logic
The endpoint will receive the HTTP POST request.
The endpoint will start an asynchronous task to ingest holiday data from the public APIs for England, Scotland, India, Ireland and other UK countries.
The holiday data will be stored in a Redis Queue.
The asynchronous task will continue running in the background.
The endpoint will return a HTTP status code 200 response indicating that the task has been successfully added to Redis Queue.
If there is an error adding the task to Redis Queue, the endpoint will return a HTTP status code 500 response indicating that there was an error.
Endpoint 2 - Check if Today is a Holiday

This endpoint will allow users to check if today is a holiday in a given country.

HTTP Method

GET

Endpoint URL
arduino
Copy code
http://<hostname>/is_today_holiday

Request Parameters
country: The country for which the user wants to check if today is a holiday. The country name should be URL encoded.
Response
HTTP status code 200 if the request is successful.
HTTP status code 400 if the country parameter is missing or invalid.
HTTP status code 404 if there is no holiday data available for the specified country.
HTTP status code 500 if there is an error processing the request.
Endpoint Logic
The endpoint will receive the HTTP GET request.
The endpoint will check if the country parameter is present and valid. If not, it will return a HTTP status code 400 response indicating that the country parameter is missing or invalid.
The endpoint will retrieve the holiday data for the specified country from Redis Queue.
If there is no holiday data available for the specified country, the endpoint will return a HTTP status code 404 response indicating that there is no holiday data available for the specified country.
The endpoint will check if today is a holiday in the specified country.
The endpoint will return a HTTP status code 200 response with a JSON object indicating whether today is a holiday or not.
Redis Queue

We will use Redis Queue to perform the task of ingesting holiday data from public APIs asynchronously. Redis Queue is a simple, lightweight message queue for Python that uses Redis as its message broker. It allows you to perform background tasks in a scalable and reliable way.

Holiday APIs

We will use the following public APIs to ingest holiday data:

- British Holidays API
- Indian Holidays API

Implementation Steps

Install Python 3.x and the required libraries: FastAPI, Redis Queue, and Requests.

Create a new FastAPI application with two endpoints: /ingest_holidays and /is_today_holiday.

Create a Redis Queue instance and configure it to use a Redis server.

Define a task function to ingest holiday data from the public APIs for England, Scotland, India, Ireland and other UK countries. This function should use the Requests library to make HTTP requests to the holiday APIs, retrieve the holiday data, and store it in Redis Queue.

Define a background worker function to process tasks in Redis Queue. This function should use Redis Queue to retrieve tasks from the queue and execute them in the background.

In the /ingest_holidays endpoint, start a new asynchronous task to ingest holiday data by calling the task function and adding it to Redis Queue.

In the /is_today_holiday endpoint, retrieve the holiday data for the specified country from Redis Queue, check if today is a holiday, and return the result in a JSON object.

Deploy the FastAPI application and the Redis server to a cloud platform such as AWS or GCP.

Future Improvements
Implement caching of holiday data to improve performance and reduce the number of HTTP requests to the public APIs.
Implement authentication and authorization to restrict access to the endpoints.
Implement rate limiting to prevent abuse of the API.
Add support for more countries and regions.