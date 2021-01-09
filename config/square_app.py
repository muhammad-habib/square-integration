from decouple import config


class SquareApp:
    ACCESS_TOKEN: str = config('SQUARE_TOKEN')
    URL: str = "https://connect.squareup.com"
    VERSION: str = "2020-12-16"
    ENV: str = config('SQUARE_ENV')
    LOCATION_ID: str = 'LAAME2A4GAZ9Q'


SquareApp()
