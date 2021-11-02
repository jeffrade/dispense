import os.path
import sqlite3
import time

from util import message


def now_ms():
    return int(time.time_ns() / 1000)


class Store:

    def __init__(self, conf_dir):
        self.conf_dir = conf_dir
        self.db_file = f'{conf_dir}dispense.db'
        self.name = conf_dir.split('/')[-2]
        if not self.db_exists():
            self.initialize()

    def get_connection(self, file):
        return sqlite3.connect(file)

    def close_connection(self, con):
        con.commit()
        con.close()

    def initialize(self):
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE bot (name TEXT, team_id TEXT, user_id TEXT, created INTEGER)''')
        cur.execute(
            '''CREATE TABLE channels (channel_name TEXT, channel_id TEXT, created INTEGER)''')
        cur.execute(
            '''CREATE TABLE consumed (
                offset INTEGER,
                team_id TEXT,
                channel_id TEXT,
                channel_name TEXT,
                message_id TEXT,
                created INTEGER)''')
        self.close_connection(con)

    def db_exists(self):
        return os.path.isfile(self.db_file)

    def insert_bot(self, user_id, dispense_msg):
        if self.find_bot_user_id_by_conf_dir() is None:
            con = self.get_connection(self.db_file)
            cur = con.cursor()
            cur.execute("INSERT INTO bot VALUES (?, ?, ?, ?)",
                        (self.name, dispense_msg.team_id, user_id, now_ms()))
            self.close_connection(con)

    def insert_channel(self, dispense_msg):
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        cur.execute("INSERT INTO channels VALUES (?, ?, ?)",
                    (dispense_msg.channel_name, dispense_msg.channel_id, now_ms()))
        self.close_connection(con)

    def fetch_channel_id(self, channel_name):
        # TODO cache me
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        rs = cur.execute(
            "SELECT channel_id FROM channels WHERE channel_name=:channel_name LIMIT 1",
            {"channel_name": channel_name})
        for row in rs:
            self.close_connection(con)
            return row[0]
        self.close_connection(con)
        return None

    def find_bot_user_id_by_conf_dir(self):
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        rs = cur.execute(
            "SELECT user_id FROM bot WHERE name=:name LIMIT 1",
            {"name": self.name})
        for row in rs:
            self.close_connection(con)
            return row[0]
        self.close_connection(con)
        return None

    def find_bot_team_id_by_conf_dir(self):
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        rs = cur.execute(
            "SELECT team_id FROM bot WHERE name=:name LIMIT 1",
            {"name": self.name})
        for row in rs:
            self.close_connection(con)
            return row[0]
        self.close_connection(con)
        return None

    def fetch_offset(self):
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        rs = cur.execute(
            "SELECT offset FROM consumed ORDER BY offset DESC LIMIT 1")
        for row in rs:
            self.close_connection(con)
            return row[0]
        self.close_connection(con)
        return 1

    def fetch_offsets(self):
        offsets = []
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        rs = cur.execute(
            "SELECT offset FROM consumed ORDER BY offset ASC")
        for row in rs:
            offsets.append(row[0])
        self.close_connection(con)
        return offsets

    def acked_message(self, dispense_msg):
        con = self.get_connection(self.db_file)
        cur = con.cursor()
        cur.execute(
            """INSERT INTO consumed
                 (offset, team_id, channel_id, channel_name, message_id, created)
               VALUES
                 (?, ?, ?, ?, ?, ?)""",
            (
                dispense_msg.offset,
                dispense_msg.team_id,
                dispense_msg.channel_id,
                dispense_msg.channel_name,
                dispense_msg.message_id,
                now_ms()
            )
        )
        self.close_connection(con)

    def publish_message(self, dispense_msg):
        con = self.get_connection(f'{self.conf_dir}../global.db')
        cur = con.cursor()
        cur.execute(
            """INSERT INTO messages
                 (team_id, channel_id, channel_name, user_id, user_name, message_id, message_text, file_id, is_bot, is_thread, created)
               VALUES
                 (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dispense_msg.team_id,
                dispense_msg.channel_id,
                dispense_msg.channel_name,
                dispense_msg.user_id,
                dispense_msg.user_name,
                dispense_msg.message_id,
                dispense_msg.message_text,
                dispense_msg.file_id,
                dispense_msg.is_bot,
                dispense_msg.is_thread,
                now_ms()
            )
        )
        self.close_connection(con)

    def fetch_messages(self, offset, team_id):
        messages = []
        con = self.get_connection(f'{self.conf_dir}../global.db')
        cur = con.cursor()
        rs = cur.execute(
            """SELECT offset, team_id, channel_id, channel_name, user_id, user_name, message_id, message_text, file_id, is_bot, is_thread, created
               FROM messages
               WHERE team_id != :team_id
               AND offset > :offset""",
            {"team_id": team_id, "offset": offset}
        )
        for row in rs:
            messages.append(
                message.DispenseMsg(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                    row[10],
                    row[11]
                )
            )
        self.close_connection(con)
        return messages
