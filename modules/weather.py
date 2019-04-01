from .base import Module
import requests
import os


class Weather(Module):
    DESCRIPTION = "Check the weather in everyone's favorite city"
    NY_COORDINATES = {
        "x": 40.8075,
        "y": -73.9626
    }

    def response(self, query, message):
        r = requests.get("https://api.weather.gov/points/{x},{y}/forecast".format(x=self.NY_COORDINATES["x"],
                                                                                  y=self.NY_COORDINATES["y"]))
        forecast = r.json()['properties']['periods'][0]['detailedForecast']
        return 'Current weather in New York City: ' + forecast
