import re


class BotMeta:

    def __init__(self, store):
        self.store = store
        self.team_id = self.fetch_team_id()
        self.user_id = self.fetch_user_id()
        self.help_pattern = self.get_help_pattern()
        self.init_pattern = self.get_init_pattern()
        self.at_pattern = self.get_at_pattern()

    def set_team_id(self, team_id):
        self.team_id = team_id

    def get_team_id(self):
        return self.team_id

    def fetch_team_id(self):
        return self.store.find_bot_team_id_by_conf_dir()

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

    def fetch_user_id(self):
        return self.store.find_bot_user_id_by_conf_dir()

    def set_help_pattern(self, pattern):
        self.help_pattern = pattern

    def get_help_pattern(self):
        if self.user_id is None:
            return None
        else:
            hp = re.compile(f'^\\<\\@{self.user_id}\\> help')
            self.set_help_pattern(hp)
            return hp

    def set_init_pattern(self, pattern):
        self.init_pattern = pattern

    def get_init_pattern(self):
        if self.user_id is None:
            return None
        else:
            ip = re.compile(f'^\\<\\@{self.user_id}\\> init')
            self.set_init_pattern(ip)
            return ip

    def set_at_pattern(self, pattern):
        self.at_pattern = pattern

    def get_at_pattern(self):
        if self.user_id is None:
            return None
        else:
            ap = re.compile(f'^\\<\\@{self.user_id}\\>')
            self.set_at_pattern(ap)
            return ap

    def initialize(self, text, dispense_msg):
        arr = text.split('<@')
        arr2 = arr[1].split('>')
        bot_user_id = arr2[0]
        self.set_team_id(dispense_msg.team_id)
        self.set_user_id(bot_user_id)
        self.set_help_pattern(re.compile(f'^\\<\\@{bot_user_id}\\> help'))
        self.set_init_pattern(re.compile(f'^\\<\\@{bot_user_id}\\> init'))
        self.set_at_pattern(re.compile(f'^\\<\\@{bot_user_id}\\>'))
        self.store.insert_bot(bot_user_id, dispense_msg)
        self.store.insert_channel(dispense_msg)
