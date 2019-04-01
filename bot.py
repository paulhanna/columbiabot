import modules
import os
import re
import requests
import json
import difflib
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
db = SQLAlchemy(app)

MAX_MESSAGE_LENGTH = 1000
PREFIX = "!"

static_commands = {
    "ping": "Pong!",
    "essays": "Submit your essays here, or read your classmates'! https://drive.google.com/open?id=1IUG1cNxmxBHhv1sSemi92fYO6y5lG6of",
    "boyspreadsheet": "https://docs.google.com/spreadsheets/d/1FZIMVvtcOZhzKldIBCz4G2ldd30GzG-lsZP4-h5I3iw/edit?fbclid=IwAR2MmmF8rShsivimJUiTv8bQ2_FQQRnEnjpXt6ADZRnfPbZ0c8J_MdEUtUM#gid=0",
    "girlspreadsheet": "https://docs.google.com/spreadsheets/d/1qo8QuKiY43fRalr5nQwde5COJVKv1FV11a4fIeu14ms/edit?fbclid=IwAR1ZLStCOyuJoeBufgndLj0Mf_AxJrEToyQ-ag6CVhfPdMZy03FfgTh9Xnw#gid=0",
	"quack": "quack",
    "dislike": "👎😬👎\n 🦵🦵",
    "shrug": r"¯\_(ツ)_/¯",
    "snort": "😤",
    "roarlion": "Roar, Lion, Roar!\nAnd wake the echoes of the Hudson Valley!\nFight on to victory everymore,\nWhile the sons of Knickerbocker rally round\nColumbia! Columbia!\nShouting her name Forever!\n\nRoar, Lion, Roar!\nFor Alma Mater on the Hudson Shore!",
    "discord": "If you must: https://discord.gg/QDBpxY3",
}

commands = {
    "zalgo": modules.Zalgo(),
    "flip": modules.Flip(),
    "countdown": modules.Countdown(),
    "about": modules.About(),
    "xkcd": modules.XKCD(),
    "applause": modules.Applause(),
    "spaces": modules.Spaces(),
    "chat": modules.Chat(),
    "weather": modules.Weather(),
    "eightball": modules.EightBall(),
    "analytics": modules.Analytics(),
    "youtube": modules.YouTube(),
    "pick": modules.Pick(),
    "chose": modules.Chose(),
    "meme": modules.Meme(),
    "love": modules.Love(),
    "price": modules.Price(),
    "minion": modules.Minion(),
    "house": modules.House(),
    "location": modules.Location(),
    "twitter": modules.Twitter(),
    "tea": modules.Tea(),
    "lyrics": modules.Lyrics(),
    "nasa": modules.NASA(),
    "conversationstarter": modules.ConversationStarter(),
    "quote": modules.Quote(),
    "dog": modules.Dog(),
    "funfact": modules.FunFact(),
    "funny": modules.Funny(),
    "boink": modules.Boink(),
}
system_responses = {
    "welcome": modules.Welcome(),
}

F_PATTERN = re.compile("can i get an? (.+) in the chat", flags=re.IGNORECASE | re.MULTILINE)
H_PATTERN = re.compile("(harvard)", flags=re.IGNORECASE)


@app.route("/", methods=["POST"])
def webhook():
    """
    Receive callback to URL when message is sent in the group.
    """
    # Retrieve data on that single GroupMe message.
    message = request.get_json()
    group_id = message["group_id"]
    text = message["text"]
    name = message["name"]
    forename = name.split(" ", 1)[0]
    print("Message received: %s" % message)
    matches = F_PATTERN.search(text)
    if matches is not None and len(matches.groups()):
        reply(matches.groups()[0] + " ❤", group_id)
    if message["sender_type"] != "bot":
        if text.startswith(PREFIX):
            instructions = text[len(PREFIX):].strip().split(" ", 1)
            command = instructions.pop(0).lower()
            query = instructions[0] if len(instructions) > 0 else ""
            # Check if there's an automatic response for this command
            if command in static_commands:
                reply(static_commands[command], group_id)
            # If not, query appropriate module for a response
            elif command in commands:
                # Make sure there are enough arguments
                if len(list(filter(None, query.split("\n")))) < commands[command].ARGC:
                    reply("Not enough arguments!", group_id)
                else:
                    response = commands[command].response(query, message)
                    if response is not None:
                        reply(response, group_id)
            elif command == "help":
                if query:
                    query = query.strip(PREFIX)
                    if query in static_commands:
                        reply(PREFIX + query + ": static response.", group_id)
                    elif query in commands:
                        reply(PREFIX + query + ": " + commands[query].DESCRIPTION + f". Requires {commands[query].ARGC} argument(s).", group_id)
                    elif query in meme_commands:
                        reply(PREFIX + query + ": meme command; provide captions separated by newlines.", group_id)
                    else:
                        reply("No such command.", group_id)
                else:
                    help_string = "--- Help ---"
                    help_string += "\nStatic commands: " + ", ".join([PREFIX + title for title in static_commands])
                    help_string += "\nTools: " + ", ".join([PREFIX + title for title in commands])
                    help_string += f"\n(Run `{PREFIX}help commandname` for in-depth explanations.)"
                    reply(help_string, group_id)
            else:
                try:
                    closest = difflib.get_close_matches(command, list(static_commands.keys()) + list(commands.keys()), 1)[0]
                    advice = f"Perhaps you meant {PREFIX}{closest}? "
                except IndexError:
                    advice = ""
                reply(f"Command not found. {advice}Use !help to view a list of commands.", group_id)

        if H_PATTERN.search(text) is not None:
            reply(forename + ", did you mean \"" + H_PATTERN.sub("H******", text) + "\"?", group_id)
        if "thank" in text.lower() and "columbiabot" in text.lower():
            reply("You're welcome, " + forename + "! :)", group_id)
        if "dad" in text.lower():
            new_text = text.strip().replace("dad", "dyd").replace("Dad", "Dyd").replace("DAD", "DYD")
            reply("Hey " + forename + ", did you mean \"" + new_text + "\"?", group_id)
    if message["system"]:
        for option in system_responses:
            if system_responses[option].RE.match(text):
                reply(system_responses[option].response(text, message), group_id)
        """
        if system_responses["welcome"].RE.match(text):
            check_names = system_responses["welcome"].get_names(text)
            for check_name in check_names:
                reply(commands["vet"].check_user(check_name), group_id)
        """
    return "ok", 200


def reply(message, group_id):
    """
    Reply in chat.
    :param message: text of message to send. May be a tuple with further data, or a list of messages.
    :param group_id: ID of group in which to send message.
    """
    # Recurse to send a list of messages.
    # This is useful when a module must respond with multiple messages.
    # TODO: This feels sort of clunky.
    if isinstance(message, list):
        for item in message:
            reply(item, group_id)
        return
    this_bot = Bot.query.get(group_id)
    data = {
        "bot_id": this_bot.bot_id,
    }
    if isinstance(message, tuple):
        text, image = message
    else:
        text = message
        image = None
    if len(text) > MAX_MESSAGE_LENGTH:
        # If text is too long for one message, split it up over several
        for block in [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]:
            reply(block, group_id)
        data["text"] = ""
    else:
        data["text"] = text
    if image is not None:
        data["picture_url"] = image
    # Prevent sending message if there's no content
    # It would be rejected anyway
    if data["text"] or data["picture_url"]:
        response = requests.post("https://api.groupme.com/v3/bots/post", data=data)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


def in_group(group_id):
    return db.session.query(db.exists().where(Bot.group_id == group_id)).scalar()


@app.route("/manager", methods=["GET", "POST"])
def manager():
    access_token = request.args["access_token"]
    if request.method == "POST":
        # Build and send bot data
        bot = {
            "name": request.form["name"] or "Columbiabot",
            "group_id": request.form["group_id"],
            "avatar_url": request.form["avatar_url"] or "https://images-na.ssl-images-amazon.com/images/I/61IWspKT-JL._SX425_.jpg",
            "callback_url": "https://columbiabotgroupme.herokuapp.com",
            "dm_notification": False,
        }
        me = requests.get(f"https://api.groupme.com/v3/users/me?token={access_token}").json()["response"]
        result = requests.post(f"https://api.groupme.com/v3/bots?token={access_token}",
                               json={"bot": bot}).json()["response"]["bot"]

        # Store in database
        registrant = Bot(result["group_id"], result["bot_id"], me["user_id"])
        db.session.add(registrant)
        db.session.commit()
    groups = requests.get(f"https://api.groupme.com/v3/groups?token={access_token}").json()["response"]
    bots = requests.get(f"https://api.groupme.com/v3/bots?token={access_token}").json()["response"]
    if os.environ.get("DATABASE_URL") is not None:
        groups = [group for group in groups if not Bot.query.get(group["group_id"])]
        bots = [bot for bot in bots if Bot.query.get(bot["group_id"])]
    return render_template("manager.html", access_token=access_token, groups=groups, bots=bots)


class Bot(db.Model):
    __tablename__ = "bots"
    # TODO: store owner also
    group_id = db.Column(db.String(16), unique=True, primary_key=True)
    bot_id = db.Column(db.String(26), unique=True)
    owner_id = db.Column(db.String(16))

    def __init__(self, group_id, bot_id, owner_id):
        self.group_id = group_id
        self.bot_id = bot_id
        self.owner_id = owner_id


@app.route("/delete", methods=["POST"])
def delete_bot():
    data = request.get_json()
    access_token = data["access_token"]
    bot = Bot.query.get(data["group_id"])
    req = requests.post(f"https://api.groupme.com/v3/bots/destroy?token={access_token}", json={"bot_id": bot.bot_id})
    if req.ok:
        db.session.delete(bot)
        db.session.commit()
        return "ok", 200
