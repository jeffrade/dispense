from util import user


class Client:

    def __init__(self, app):
        self.app = app

    def get_user_name(self, user_id):
        user_info = self.app.client.users_info(user=user_id)
        return user.get_user_name(user_info)

    def get_channel_name(self, channel_id):
        cn = self.app.client.conversations_info(channel=channel_id)
        return cn['channel'].get('name')

    def get_file_info(self, file_id):
        return self.app.client.files_info(file=file_id)
