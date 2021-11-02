CREATE TABLE messages (
    offset INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id TEXT,
    channel_id TEXT,
    channel_name TEXT,
    user_id TEXT,
    user_name TEXT,
    message_id TEXT,
    message_text TEXT NULL,
    file_id TEXT NULL,
    is_bot INTEGER,
    is_thread INTEGER,
    created INTEGER
);