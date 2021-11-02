# {'user': {'id': 'U1V0123AB'
# {'user': {'name': 'jdoe'
# {'user': {'real_name': 'John Doe'
# {'user': {'profile': {'real_name': 'John Doe'
# {'user': {'profile': {'real_name_normalized': 'John Doe'
# {'user': {'profile': {'display_name': 'johndoe'
# {'user': {'profile': {'display_name_normalized': 'johndoe'
def get_user_name(user_info):
    user = user_info['user']
    if exists_and_non_empty(user['profile'], 'display_name'):
        return user['profile']['display_name']
    elif exists_and_non_empty(user['profile'], 'display_name_normalized'):
        return user['profile']['display_name_normalized']
    elif exists_and_non_empty(user, 'name'):
        return user['name']
    elif exists_and_non_empty(user, 'real_name'):
        return user['real_name']
    elif exists_and_non_empty(user['profile'], 'real_name'):
        return user['profile']['real_name']
    elif exists_and_non_empty(user['profile'], 'real_name_normalized'):
        return user['profile']['real_name_normalized']
    else:
        return user['id']


def exists_and_non_empty(d, key):
    return key in d and d[key] is not None and d[key] != ''
