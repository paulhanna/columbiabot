from .base import Module
import os
import praw
import random


class Funny(Module):
    DESCRIPTION = "Get a random meme from r/me_irl"
    responses = []

    def __init__(self):
        super().__init__()
        self.reddit = praw.Reddit(client_id=os.environ["REDDIT_CLIENT_ID"],
                                  client_secret=os.environ["REDDIT_SECRET"],
                                  user_agent="yalebot")

    def response(self, query, message):
        if len(self.responses) == 0:
            for submission in self.reddit.subreddit("me_irl").hot(limit=25):
                if not submission.stickied and "jpg" in submission.url:
                    self.responses.append(submission.url)
            random.shuffle(self.responses)
        return self.responses.pop()
