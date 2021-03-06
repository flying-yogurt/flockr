"""
messages.py written by Xingyu Tan.
"""

from datetime import timezone, datetime
import time
import src.data.data as data
from src.base.auth import decode_token
from src.base.error import InputError, AccessError


################################################################################
################################################################################
##
##    Xingyu TAN's work:
##    22 October, 2020
##
##      - some helper functions;
##      - message_send(token, channel_id, message);
##      - message_remove(token, message_id);
##      - message_edit(token, message_id, message);
##      - and all tests for these functions.
##
##    Xingyu TAN's work:
##    05 November, 2020
##
##      - some helper functions;
##      - message_sendlater
##      - message_pin
##      - message_unpin
##      - and all tests, http file and http tests for these functions.
##
################################################################################
################################################################################


############################################################
#      Helper Functions
############################################################
def edit_msg_in_list(msg, text):
    """Interate the messages list by its id, return the message after edit."""
    # get the channels
    channels = data.return_channels()
    messages = data.return_messages()

    # deleting message from memory
    for i in channels:
        if i['channel_id'] == msg['channel_id']:
            for temp in i['message']:
                if temp['message_id'] == msg['message_id']:
                    temp['message'] = text

    for temp in messages:
        if temp['message_id'] == msg['message_id']:
            temp['message'] = text

    # add it to memory
    data.replace_channels(channels)
    data.replace_messages(messages)

def change_msg_pin(msg, sign):
    """Interate the messages list by its id, return the message after edit."""
    # get the channels
    channels = data.return_channels()
    messages = data.return_messages()

    # deleting message from memory
    for i in channels:
        if i['channel_id'] == msg['channel_id']:
            for temp in i['message']:
                if temp['message_id'] == msg['message_id']:
                    temp['is_pinned'] = sign

    for temp in messages:
        if temp['message_id'] == msg['message_id']:
            temp['is_pinned'] = sign

    # add it to memory
    data.replace_channels(channels)
    data.replace_messages(messages)

def if_auth_owner(u_id, channel_id):
    """check if the u_id is the owner of the channel or the owner of flockr."""
    test = False
    # check if it is the owener of flocker
    if check_permission(u_id) == 1:
        test = True
        return test
    # check if it is the owener of channel
    channel_got = find_channel(channel_id)
    for i in channel_got['owner_members']:
        if i['u_id'] == u_id:
            test = True

    return test

def if_auth_is_message_channel_owner(u_id, channel_id):
    """Check if the u_id is the owner of the channel."""
    test = False
    # check if it is the owener of channel
    channel_got = find_channel(channel_id)
    for i in channel_got['owner_members']:
        if i['u_id'] == u_id:
            test = True

    return test

def delete_msg_in_list(msg):
    """Interate the messages list by its id, return the message we need."""

    # get the channels
    channels = data.return_channels()
    messages = data.return_messages()

    # deleting message from memory
    for i in channels:
        if i['channel_id'] == msg['channel_id']:
            i['message'].remove(msg)

    messages.remove(msg)
    # add it to memory
    data.replace_channels(channels)
    data.replace_messages(messages)

def adding_message(return_message, channel_id):
    """Adding given return_message in the whole list."""
    # get the channels
    channels = data.return_channels()
    # add user into memory
    for i in channels:
        if i['channel_id'] == channel_id:
            i['message'].insert(0, return_message)

    # add it to memory
    data.replace_channels(channels)
    data.insert_messages(return_message)

def find_message(msg_id):
    """Interate the messages list by its id, return the message we need."""
    return_message = None
    for i in data.return_messages():
        if i['message_id'] == msg_id:
            return_message = i
            break
    return return_message

def token_into_user_id(token):
    """Transfer the token into the user id."""

    user = decode_token(token)
    if user is None:
        return -1

    au_id = user.get('u_id')

    return au_id

def check_permission(user_id):
    """Check if given u_id person is permission one."""
    permission_check = 2
    for i in data.return_users():
        if i['u_id'] == user_id:
            permission_check = i['permission_id']

    return permission_check

def find_channel(channel_id):
    """Interate the channels list by its id, return the channel we need."""
    answer = None
    for i in data.return_channels():
        if i['channel_id'] == channel_id:
            answer = i
            break
    return answer

def find_one_in_channel(channel, u_id):
    """Return a boolean variable to indicate if someone we want in the channel."""
    for i in channel['all_members']:
        if i['u_id'] == u_id:
            return True
    return False

def find_one_in_message(message, u_id):
    reacts = message["reacts"][0]
    if u_id in reacts['u_ids']:
        return True
    return False

def edit_msg_react_in_list(msg, uid, method):
    """Interate the messages list by its id, return the message after edit."""
    # get the channels
    channels = data.return_channels()
    messages = data.return_messages()

    # modify in channel
    for i in channels:
        if i['channel_id'] == msg['channel_id']:
            for temp in i['message']:
                if temp['message_id'] == msg['message_id']:
                    if method == 'add':
                        temp['reacts'][0]["u_ids"].append(int(uid))
                    elif method == 'delete':
                        temp['reacts'][0]["u_ids"].remove(int(uid))
    # modify in msg.json
    for temp in messages:
        if temp['message_id'] == msg['message_id']:
            if method == 'add':
                temp['reacts'][0]["u_ids"].append(int(uid))
            elif method == 'delete':
                temp['reacts'][0]["u_ids"].remove(int(uid))

    # add it to memory
    data.replace_channels(channels)
    data.replace_messages(messages)


############################################################
#       message_send(token, channel_id, message)
#       written by Xingyu TAN
############################################################
def message_send(token, channel_id, message):
    """Send a message from authorised_user to the channel specified by channel_id.

    Args:
        token: the token of the sender.
        channel_id: the channel which is the target of message.
        message: the message we send.

    RETURNS:
        {message_id}

    THEREFORE, TEST EVERYTHING BELOW:
    1. inputError
      - Message is more than 1000 characters.
    2. accessError
      - The authorised user has not joined the channel they are trying to post to.
      - Cannot find the channel_id.
    """

    # InputError 1: invalid token.
    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError(description='invalid token.')

    # InputError 2: Message is more than 1000 characters.
    if len(message) > 1000:
        raise InputError(description='Message is more than 1000 characters.')

    # AccessError 3: invalid channel_id.
    channel_got = find_channel(channel_id)
    if channel_got is None:
        raise AccessError(description='invalid channel_id.')

    # AccessError 4: if the auth not in channel.
    if not find_one_in_channel(channel_got, auth_id):
        raise AccessError(description='auth not in channel')

    # Case 5: no error, add the message
    new_msg_id = 1
    if len(data.return_messages()) != 0:
        new_msg_id = data.return_messages()[0]['message_id'] + 1

    # record the time rightnow
    now = datetime.utcnow()
    timestamp = int(now.replace(tzinfo=timezone.utc).timestamp())

    # create the message struct
    return_message = {
        'message_id': new_msg_id,
        'channel_id': channel_id,
        'u_id': auth_id,
        'message': message,
        'time_created': timestamp,
        'reacts': [{
            'react_id': 1,
            'u_ids':[],
            'is_this_user_reacted': False}],
        'is_pinned': False
    }

    # insert the message in the top of messages in the channel.
    adding_message(return_message, channel_id)

    return {
        'message_id': new_msg_id,
    }


############################################################
#       message_remove(token, message_id)
#       written by Xingyu TAN
############################################################
def message_remove(token, message_id):
    """Given a message_id for a message, this message is removed from the channel.

    Args:
        token: the token of the people who authority.
        channel_id: the channel which is the target of message.

    RETURNS:
        {}

    THEREFORE, TEST EVERYTHING BELOW:
    1. inputError
      - Message id is not exist.
    2. accessError excluding
      - Message with message_id was sent by the authorised user making this reques.
      - The authorised user is an owner of this channel or the flockr.
    """

    # InputError 1: invalid token.
    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError(description='invalid token.')

    # InputError 2: Message id is not exist
    message_using = find_message(message_id)
    if message_using is None:
        raise InputError(description='invalid message id.')

    # AccessError 3: excluding message sender and channel_owner
    test_owener = if_auth_owner(auth_id, message_using['channel_id'])
    # if it is neither channel owner nor messager sender
    # raise for access error
    if test_owener is False and message_using['u_id'] != auth_id:
        raise AccessError(description='neither message sender nor channel_owner.')

    # Case 4: no error, delete the message
    delete_msg_in_list(message_using)
    return {}


############################################################
#       message_edit(token, message_id, message)
#       written by Xingyu TAN
############################################################
def message_edit(token, message_id, message):
    """Given a message, update it's text with new text.

    If the new message is an empty string, the message is deleted.

    Args:
        token: the token of the people who edit it.
        channel_id: the channel which is the target of message.
        message: the new message.

    RETURNS:
        {}

    THEREFORE, TEST EVERYTHING BELOW:
    1. InputError
      - None
    2. AccessError
      - The authorised user is the message sender.
      - The authorised user is the owener of flockr or channel.
    3. If the new message is empty
      - Delete the message.
    """
    # AccessError 1: excluding message sender and channel_owner
    auth_id = token_into_user_id(token)
    message_using = find_message(message_id)
    test_owener = if_auth_owner(auth_id, message_using['channel_id'])
    # if it is neither channel owner nor messager sender
    # raise for access error
    if test_owener == False and message_using['u_id'] != auth_id:
        raise AccessError(description='neither message sender nor channel_owner.')
    # case 2: if empty msg, delete it
    if len(message) == 0:
        delete_msg_in_list(message_using)

    # Case 3: no error, edit the message
    else:
        edit_msg_in_list(message_using, message)
    return {}


############################################################
#       message_sendlater(token, channel_id, message, time_sent)
#       written by Xingyu TAN
############################################################
def message_sendlater(token, channel_id, message, time_sent):
    """Send a message from authorised_user to the channel specified by channel_id automatically at a specified time in the future.

    Args:
        token: the token of the people who edit it.
        channel_id: the channel which is the target of message.
        message: the new message.
        time_sent: when the msg would be sent

    RETURNS:
        return {
            'message_id': new_msg_id,
        }

    THEREFORE, TEST EVERYTHING BELOW:
    1. InputError
      - Channel ID is not a valid channel
      - Message is more than 1000 characters
      - Time sent is a time in the past
    2. AccessError
      - when the authorised user has not joined the channel they are trying to post to.
    """
    # InputError 1: invalid token.
    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError(description='invalid token.')

    # InputError 2: Message is more than 1000 characters.
    if len(message) > 1000:
        raise InputError(description='Message is more than 1000 characters.')

    # AccessError 3: invalid channel_id.
    channel_got = find_channel(channel_id)
    if channel_got is None:
        raise AccessError(description='invalid channel_id.')

    # AccessError 4: if the auth not in channel.
    if not find_one_in_channel(channel_got, auth_id):
        raise AccessError(description='auth not in channel')

    #Input error 5: the time is in the past
    # record the time rightnow
    now = datetime.utcnow()
    timestamp = int(now.replace(tzinfo=timezone.utc).timestamp())
    if (time_sent < timestamp):
        raise InputError(description='The time is in the past')

    # Case 5: no error, add the message
    new_msg_id = 1
    if len(data.return_messages()) != 0:
        new_msg_id = data.return_messages()[0]['message_id'] + 1

    # create the message struct
    return_message = {
        'message_id': new_msg_id,
        'channel_id': channel_id,
        'u_id': auth_id,
        'message': message,
        'time_created': time_sent,
        'reacts': [{
            'react_id': 1,
            'u_ids':[],
            'is_this_user_reacted': False}],
        'is_pinned': False

    }

    # insert the message in the top of messages in the channel.
    time.sleep(time_sent - timestamp)
    adding_message(return_message, channel_id)
    return {
        'message_id': new_msg_id,
    }


############################################################
#       message_react(token, message_id, react_id)
#       written by Yuhan Yan
############################################################
def message_react(token, message_id, react_id):
    """Given a message within a channel the authorised user is part of, add a "react" to that particular message.

    Args:
        token: the token of the people who edit it.
        channel_id: the channel which is the target of message.
        message_id: the specific message.
        react_id: the react_id is always 1 for thumbs up

    RETURNS:
        {}

    THEREFORE, TEST EVERYTHING BELOW:
    1. inputError
      - Message_id is not a valid message within a channel that the authorised user has joined.
      - React_id is not a valid React ID. The only valid react ID the frontend has is 1.
      - Message with ID message_id already contains an active React with ID react_id from the authorised user.
    """
    # InputError 1: invalid token.
    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError(description='invalid token.')

    if react_id !=1:
        raise InputError(description='invalid react_id.')

    # AccessError 3: invalid channel_id.
    message_got = find_message(message_id)
    if message_got is None:
        raise InputError(description='invalid message_id.')

    if find_one_in_message(message_got, auth_id):
        raise AccessError(description='the auth already exist.')

    edit_msg_react_in_list(message_got, auth_id, 'add')
    return {}


############################################################
#       message_react(token, message_id, react_id)
#       written by Yuhan Yan
############################################################
def message_unreact(token, message_id, react_id):
    """Given a message within a channel the authorised user is part of, remove a "react" to that particular message.

    Args:
        token: the token of the people who edit it.
        channel_id: the channel which is the target of message.
        message_id: the specific message.
        react_id: the react_id is always 1 for thumbs up
    RETURNS:
        {}

    THEREFORE, TEST EVERYTHING BELOW:
    1. InputError
      - Message_id is not a valid message within a channel that the authorised user has joined.
      - react_id is not a valid React ID. The only valid react ID the frontend has is 1.
      - Message with ID message_id does not contain an active React with ID react_id.
    """
    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError(description='invalid token.')

    if react_id != 1:
        raise InputError(description='invalid react_id.')

    # AccessError 3: invalid channel_id.
    message_got = find_message(message_id)
    if message_got is None:
        raise InputError(description='invalid message_id.')

    if not find_one_in_message(message_got, auth_id):
        raise AccessError(description='the auth already exist.')

    edit_msg_react_in_list(message_got, auth_id, 'delete')
    return {}


############################################################
#       message_pin(token, message_id)
#       written by Xingyu TAN
############################################################
def message_pin(token, message_id):
    """Given a message within a channel, mark it as "pinned" to be given special display treatment by the frontend.

    Args:
        token: the token of the people who edit it.
        message_id: the new message.

    RETURNS:
        {}

    THEREFORE, TEST EVERYTHING BELOW:
    1. InputError
      - Message_id is not a valid message.
      - Message is already pinned.
      - Token invalid.
    2. AccessError
      - The authorised user is not a member of the channel that the message is within.
      - The authorised user is not an owner.
    """
    # InputError 1: invalid token.
    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError(description='invalid token.')

    # InputError 2: Message id is not exist
    message_using = find_message(message_id)
    if message_using is None:
        raise InputError(description='invalid message id.')

    # InputError 3: Message already pin
    message_using = find_message(message_id)
    if message_using['is_pinned']:
        raise InputError(description='Message already pin')

    # AccessError 4: token peroson is not owner
    test_owener = if_auth_is_message_channel_owner(auth_id, message_using['channel_id'])
    # if it is neither channel owner nor messager sender
    # raise for access error
    if test_owener is False:
        raise AccessError(description='token peroson is not owner.')

    # Case 5: no error, change the message pin
    change_msg_pin(message_using, True)
    return {}


############################################################
#       message_unpin(token, message_id)
#       written by Xingyu TAN
############################################################
def message_unpin(token, message_id):
    """Given a message within a channel, remove it's mark as unpinned.

    Args:
        token: the token of the people who edit it.
        message_id: the new message.

    RETURNS:
        {}

    THEREFORE, TEST EVERYTHING BELOW:
    1. InputError
      - Message_id is not a valid message.
      - Message is already unpinned.
    2. AccessError
      - The authorised user is not a member of the channel that the message is within.
      - The authorised user is not an owner.
    """
    # InputError 1: invalid token.
    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError(description='invalid token.')

    # InputError 2: Message id is not exist
    message_using = find_message(message_id)
    if message_using is None:
        raise InputError(description='invalid message id.')

    # InputError 3: Message already pin
    message_using = find_message(message_id)
    if message_using['is_pinned'] is False:
        raise InputError(description='Message already unpin')

    # AccessError 4: token peroson is not owner
    test_owener = if_auth_is_message_channel_owner(auth_id, message_using['channel_id'])
    # if it is neither channel owner nor messager sender
    # raise for access error
    if test_owener is False:
        raise AccessError(description='token peroson is not owner.')

    # Case 5: no error, change the message pin to
    change_msg_pin(message_using, False)
    return {}
