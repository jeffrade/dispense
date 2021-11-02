import logging
import os
import urllib.request

from bot import bot_meta
from util import user


class Handler:
    app = None
    bot = None
    client = None

    def __init__(self, app, bot, client):
        self.app = app
        self.bot = bot
        self.client = client

    def event_app_mention(self, dispense_msg, say, logger):
        app_mention_text = dispense_msg.message_text
        if self.bot.get_user_id() is None:
            self.bot.initialize(app_mention_text, dispense_msg)
            say(f"Thanks <@{dispense_msg.user_id}>! I am now initialized. Add me to other channels with 'init'")
        elif self.bot.get_init_pattern().match(app_mention_text):
            self.bot.store.insert_channel(dispense_msg)
            say(f"I will now relay messages for {dispense_msg.channel_name}")
        elif self.bot.get_help_pattern().match(app_mention_text):
            say(f"Hi <@{dispense_msg.user_id}>! Ask your admin to install me in two or more Slack organizations and I will bidirectionally relay messages and files for public channels that share a name.")
        else:
            say(f"Sorry <@{dispense_msg.user_id}>, I don't understand. Refer to my docs for help.")

    def handle_file_shared_events(self, dispense_msg, say, logger):
        user_id = dispense_msg.user_id
        if user_id == self.bot.get_user_id() or self.bot.get_user_id() is None:
            return
        else:
            resp = self.client.get_file_info(dispense_msg.file_id)
            file_name = resp['file']['name']
            url = resp['file']['url_private_download']
            req = urllib.request.Request(
                url, headers={'Authorization': 'Bearer %s' % self.app._token})
            local_file_dir = f'./tmp/{dispense_msg.team_id}_{dispense_msg.message_id}'
            os.mkdir(local_file_dir)
            local_file_name = f'{local_file_dir}/{file_name}'
            # https://stackoverflow.com/a/7244263
            with urllib.request.urlopen(req) as r, open(local_file_name, 'wb') as f:
                d = r.read()  # bytes object
                f.write(d)

    def share_file(self, dispense_msg):
        local_file_dir = f'./tmp/{dispense_msg.team_id}_{dispense_msg.message_id}'
        local_file_name = os.listdir(local_file_dir)[0]
        in_file = open(f'{local_file_dir}/{local_file_name}', "rb")
        fbytes = in_file.read()
        in_file.close()
        resp = self.app.client.files_upload(
            channels=dispense_msg.channel_id,
            initial_comment=f'{dispense_msg.user_name}:',
            file_name=local_file_name,
            file=fbytes)
        if resp['ok']:
            logging.info('Upload complete!')
        else:
            logging.warn(f'Upload may have failed! %s', resp)
        # TODO Remove file and dir by after 1+ hour(s) to give consumers a chance to read.
        # os.remove(f'{local_file_dir}/{local_file_name}')
        # os.rmdir(local_file_dir)
        return True

    def share_message(self, dispense_msg):
        user_id = dispense_msg.user_id
        if user_id == self.bot.get_user_id() or self.bot.get_user_id() is None:
            return
        elif dispense_msg.message_text == '':
            return
        elif self.bot.get_at_pattern().match(dispense_msg.message_text):
            return
        else:
            resp = self.app.client.chat_postMessage(
                channel=dispense_msg.channel_id,
                text=f"{dispense_msg.user_name}: {dispense_msg.message_text}"
            )
            return resp['ok']
