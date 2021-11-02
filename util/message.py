def create_msg(body, client):
    msg = DispenseMsg(
        None,
        body['team_id'],
        body['event'].get('channel') or body['event']['channel_id'],
        None,
        body['event'].get('user') or body['event']['user_id'],
        None,
        body['event_id'],
        body['event'].get('text'),
        body['event'].get('file_id'),
        False,
        body['event'].get('thread_ts') is not None,
        body['event_time']
    )
    msg = get_user_name(msg, client)
    msg = get_channel_name(msg, client)
    msg = get_bot_info(msg, body)
    return msg


def get_user_name(msg, client):
    # TODO cache me
    name = client.get_user_name(msg.user_id)
    msg.user_name = name
    return msg


def get_channel_name(msg, client):
    # TODO cache me
    name = client.get_channel_name(msg.channel_id)
    msg.channel_name = name
    return msg


def get_bot_info(msg, body):
    if body['event'].get('bot_profile') is not None:
        msg.is_bot = True
        bot_name = body['event']['bot_profile']['name']
        url = "Could not find image url"
        if body['event'].get('attachments') is not None:
            url = body['event']['attachments'][0]['image_url']
        elif body['event'].get('blocks') is not None:
            for b in body['event']['blocks']:
                if b['type'] == "image":
                    url = b['image_url']
                    break
        msg.message_text = f"(via {bot_name}) {url}"
    return msg


class DispenseMsg:

    def __init__(self, offset, team_id, ch_id, ch_name, u_id,
                 u_name, m_id, m_text, f_id, is_bot, is_thread, created):
        self.offset = offset
        self.team_id = team_id
        self.channel_id = ch_id
        self.channel_name = ch_name
        self.user_id = u_id
        self.user_name = u_name
        self.message_id = m_id
        self.message_text = m_text
        self.file_id = f_id
        self.is_bot = is_bot
        self.is_thread = is_thread
        self.created = created
