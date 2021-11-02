"""
To learn available listener arguments, visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
https://api.slack.com/events/message
"""
import configparser
import logging
import os
import sys
import time
import urllib.request
from threading import Thread
from typing import Callable

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from bot import bot_meta, client, handler, store
from util import message, user

logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config.read(sys.argv[1])
BOT_TOKEN = config["DEFAULT"]["SLACK_BOT_TOKEN"]
SIGNING_SECRET = config["DEFAULT"]["SLACK_SIGNING_SECRET"]

# Initializes your app with your bot token and socket mode handler
app = App(
    token=BOT_TOKEN,
    signing_secret=SIGNING_SECRET
)

store = store.Store(sys.argv[1].strip('dispense.conf'))
bot = bot_meta.BotMeta(store)
client = client.Client(app)
handler = handler.Handler(app, bot, client)


@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
    logger.debug(f'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ @app.middleware: {body}')
    return next()


@app.event({'type': 'app_mention'})
def event_app_mention(body, say, logger):
    logger.debug("BEGIN body #############################")
    logger.debug(body)
    logger.debug("END body ###############################")
    dispense_msg = message.create_msg(body, client)
    handler.event_app_mention(dispense_msg, say, logger)


@app.event({'type': 'file_shared'})
def handle_file_shared_events(body, say, logger):
    logger.debug("BEGIN body #############################")
    logger.debug(body)
    logger.debug("END body ###############################")
    dispense_msg = message.create_msg(body, client)
    store.publish_message(dispense_msg)
    handler.handle_file_shared_events(dispense_msg, say, logger)


@app.event({'type': 'message', 'subtype': 'message_deleted'})
def handle_message_deleted(body, say, logger):
    # TODO Future iteration
    return


@app.event({'type': 'message', 'subtype': 'message_changed'})
def handle_message_changed(body, say, logger):
    # TODO Future iteration
    return


@app.event({'type': 'message', 'subtype': None})
def handle_message_events(body, say, logger):
    logger.debug("BEGIN body #############################")
    logger.debug(body)
    logger.debug("END body ###############################")
    dispense_msg = message.create_msg(body, client)
    store.publish_message(dispense_msg)


def consumer():
    while True:
        try:
            offset = store.fetch_offset()
            dispense_messages = store.fetch_messages(offset, bot.team_id)
            for dispense_msg in dispense_messages:
                dispense_msg = adapt_message(dispense_msg)
                if dispense_msg.file_id is not None:
                    if handler.share_file(dispense_msg) == True:
                        store.acked_message(dispense_msg)
                elif dispense_msg.is_thread:
                    # TODO Future iteration
                    store.acked_message(dispense_msg)
                else:
                    if handler.share_message(dispense_msg) == True:
                        store.acked_message(dispense_msg)
        except Exception as e:
            print(e)
        time.sleep(1)


def adapt_message(dispense_msg):
    channel_id = store.fetch_channel_id(dispense_msg.channel_name)
    dispense_msg.channel_id = channel_id
    return dispense_msg


if __name__ == "__main__":
    t = Thread(target=consumer)
    t.daemon = True
    t.start()
    SocketModeHandler(app, config["DEFAULT"]["SLACK_APP_TOKEN"]).start()
