from pydantic import BaseSettings


class Calendarific(BaseSettings):
    """Define Calendarific API settings.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.
    """
    api_key: str = "92392e91378cea548d3812ab7519e6780c2a7df2"
    api_url: str = "https://calendarific.com/api/v2/holidays"

class Web3Storage(BaseSettings):
    """Define Calendarific API settings.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.
    """
    api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDk0NEYzNkM1N2U0NjI2MUE1ZmFmNTExY2ZEOWJFNjExNUU5NDkwNjciLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2ODA3MTY1ODQwMzEsIm5hbWUiOiJZUkVUQUlOIn0.sdKo4cDiwi6ovgPN5u61NDHaum9t3ez0xTqoWIcH-b0"
    api_url: str = "https://calendarific.com/api/v2/holidays"
