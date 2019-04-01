from .base import Module
import random


class Chose(Module):
    DESCRIPTION = "Sing our other favorite song"

    def response(self, query, message):
        return "Bum" + " bum" * random.randint(0, 30) + ", that's why I chose Col" + "um" * random.randint(0, 30) + "bia! https://www.youtube.com/watch?v=qpj6RP-KWkw"
