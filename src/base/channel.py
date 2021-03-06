"""
channel.py written by Xingyu Tan, Yuhan Yan and Hao Ren.
"""

#import jwt, JWT_SECRET, AccessError
import src.data.data as data
from src.base.error import InputError
from src.base.auth import decode_token

################################################################################
################################################################################
##
##    Xingyu TAN's work:
##    2 October, 2020
##
##      - some helper functions;
##      - channel_invite(token, channel_id, u_id);
##      - channel_details(token, channel_id);
##      - channel_messages(token, channel_id, start);
##      - and all tests for these functions.
##
################################################################################
################################################################################


############################################################
#      Xingyu's Helper Functions
############################################################

def add_one_in_channel(channel_id, user):
    """Adding a member into the channel."""

    # get the channels
    channels = data.return_channels()

    # add user into memory
    for i in channels:
        if i['channel_id'] == channel_id:
            i['all_members'].append(user)
            if check_permission(user['u_id']) == 1:
                i['owner_members'].append(user)

    # add it to memory
    data.replace_channels(channels)

def token_into_user_id(token):
    """Transfer the token into the user id."""

    user = decode_token(token)
    if user is None:
        return -1
    au_id = user.get('u_id')

    return au_id

def find_channel(channel_id):
    """Interate the channels list by its id, return the channel we need."""
    answer = None
    for i in data.return_channels():
        if i['channel_id'] == channel_id:
            answer = i
            break
    return answer

def check_permission(user_id):
    """check if given u_id person is permission one"""
    permission_check = 1
    for i in data.return_users():
        if i['u_id'] == user_id:
            permission_check = i['permission_id']

    return permission_check

def find_user(user_id):
    """Find user's info by search one's id."""
    u_id = -1
    for i in data.return_users():
        if i['u_id'] == user_id:
            u_id = i
            break
    return u_id

def find_one_in_channel(channel, u_id):
    """Return a boolean variable to indicate if someone we want in the channel."""
    for i in channel['all_members']:
        if i['u_id'] == u_id:
            return True
    return False


############################################################
#       channel_invite(token, channel_id, u_id)
############################################################

def channel_invite(token, channel_id, u_id):
    """Invites a user (with user id u_id) to join a channel with ID channel_id.

    Args:
        token: the token of the invitee.
        channel_id: the channel which is the target of inviter.
        u_id: the user id of the inviter.

    Returns:
        None.

    Raises:
        1. InputError
            - the channel id is invalid;
            - the user id is invalid;
            - the user token is invalid.
        2. AccessError
            - the authorised user is not in this channel.
        3. Repeated Invite
            - Repeated invite one person who is already in.
    """
    auth_id = token_into_user_id(token)     # InputError 1: invalid token.
    if auth_id == -1:
        raise InputError('invalid token')

    channel_got = find_channel(channel_id)  # InputError 2: invalid channel_id.
    if channel_got is None:
        raise InputError('invalid channel_id')

    user = find_user(u_id)                  # InputError 3: invalid user_id.
    if user == -1:
        raise InputError('invalid user_id')

    if not find_one_in_channel(channel_got, auth_id):
        raise InputError('the auth not in channel')                   # AccessError 4: if the auth not in channel.

    if find_one_in_channel(channel_got, u_id):
        return                              # Case 5: if the member already in, skip it.

    user_struct = find_user(u_id)           # Case 6: no error, add the member.
    user = {                                # Create a new struct to store user's info.
        'u_id': u_id,
        'name_first': user_struct['name_first'],
        'name_last': user_struct['name_last'],
        'profile_img_url':''
    }
    add_one_in_channel(channel_id, user)     # Add the above struct into channel.


############################################################
#       channel_details(token, channel_id)
############################################################

def channel_details(token, channel_id):
    """Provide basic details about the channel by its id.

    Args:
        token: the token of authorised user.
        channel_id: the id of channel we need info.

    Returns:
        {'name': channel_got['name'],
        'owner_members':channel_got['owner_members'],
        'all_members': channel_got['all_members'],}

    Raises:
        1. InputError
            - the channel id is invalid;
            - the user token is invalid.
        2. AccessError
            - the authorised user is not in this channel.
    """
    auth_id = token_into_user_id(token)     # InputError 1: invalid token.
    if auth_id == -1:
        raise InputError('invalid token')

    channel_got = find_channel(channel_id)  # InputError 2: invalid channel_id.
    if channel_got is None:
        raise InputError('invalid channel_id')

    if not find_one_in_channel(channel_got, auth_id):
        raise InputError('the auth is not in channel')                   # AccessError 3: if the auth not in channel.

    return {                                # Case 4: all passed, return channel.
        'name': channel_got['name'],
        'owner_members':channel_got['owner_members'],
        'all_members': channel_got['all_members'],
    }


############################################################
#       channel_messages(token, channel_id, start)
############################################################

def channel_messages(token, channel_id, start):
    """Return 50 messages between `start` and `start + 50`.

    Args:
        token: the token of authorised user.
        channel_id: the id of channel we need info.
        start: the message we want to grab next 50 messages.

    Returns:
        -1: for no more message after start.
        50:
            1. exist messages after start and no more than 50 messages.
            2. the exist messages after start more than 50, just return the top 50 ones.
        { messages, start, end }

    Raises:
        1. InputError
            - the channel id is invalid;
            - start is greater than the total number of messages in the channel.
        2. AccessError
            - the authorised user is not in this channel.
    """
    end = -1

    auth_id = token_into_user_id(token)     # InputError 1: invalid token.
    if auth_id == -1:
        raise InputError('invalid token')

    channel_got = find_channel(channel_id)  # InputError 2: invalid channel_id.
    if channel_got is None:
        raise InputError('onvalid channel_id')

    if not find_one_in_channel(channel_got, auth_id):
        raise InputError('the auth is not in channel')                   # AccessError 3: if the auth not in channel.

    num_msgs = len(channel_got['message'])
    if num_msgs < start:                    # InputError 4: the start >= total messages.
        raise InputError(' the start >= total messages')

    return_msg = []                         # Case 6: messages is more than 50, get top.
    if num_msgs > (start + 50):
        return_msg = channel_got['message'][start: start + 51]
        end = start + 50
    else:                                  # Case 7: Get all messages which in (0, 50].
        return_msg = channel_got['message'][start:]

    for msg in return_msg:
        msg['reacts'][0]['is_this_user_reacted'] = False
        if auth_id in msg['reacts'][0]['u_ids']:
            msg['reacts'][0]['is_this_user_reacted'] = True

    return {                                # Return the struct.
        'messages': return_msg,
        'start': start,
        'end': end,
    }


################################################################################
################################################################################
##
##    Hao REN's work:
##    3 October, 2020
##
##      - some helper functions;
##      - channel_leave(token, channel_id);
##      - channel_join(token, channel_id);
##      - and all tests for these functions.
##      - Style improvements.
##
################################################################################
################################################################################


############################################################
#      Hao's Helper Functions
############################################################

def remove_a_member_in_channel(u_id, channel_id):
    """Remove the member by user if from the channel."""

    channels = data.return_channels()

    for users in channels:
        if users['channel_id'] == channel_id:
            for member in users['all_members']:
                if member['u_id'] == u_id:
                    users['all_members'].remove(member)


    data.replace_channels(channels)

def number_of_owners(channel_id):
    """Return the total number of owners."""

    test = None
    for chan in data.return_channels():
        if chan['channel_id'] == channel_id:
            test = chan


    return len(test['owner_members'])

def remove_whole_channel(channel_id):
    """If no owner exist, remove the whole channel."""

    channels = data.return_channels()

    for chan in channels:
        if chan['channel_id'] == channel_id:
            channels.remove(chan)

    data.replace_channels(channels)

def is_channel_public(channel_id):
    """To indicate if the channel is public."""
    is_public = False
    for channel in data.return_channels():
        if channel['channel_id'] == channel_id:
            is_public = channel['is_public']

    return is_public


############################################################
#       channel_leave(token, channel_id)
############################################################

def channel_leave(token, channel_id):
    """Given a channel ID, the user removed as a member of this channel.

    Args:
        token: the token of user who is leaving.
        channel_id: the channel which user is leaving.

    Returns:
        None.

    Raises:
        1. InputError
            - the channel id is invalid;
        2. AccessError
            - the authorised user is not in this channel.
    """
    target_channel = find_channel(channel_id)
    if target_channel is None:              # InputError 1: invalid channel_id.
        raise InputError('invalid channel_id')

    auth_id = token_into_user_id(token)
    if auth_id == -1:                       # InputError 2: invalid token.
        raise InputError('invalid token')

    if not find_one_in_channel(target_channel, auth_id):
        raise InputError('the auth not in channel')                  # AccessError 3: if the auth not in channel.

                                            # Case 4: the user is one of the owners.
    if find_current_owner(target_channel, auth_id) is True:
        if number_of_owners(channel_id) > 1:
            rm_owner_in_channel(channel_id, auth_id)
            remove_a_member_in_channel(auth_id, channel_id)
        else:                               # Case 5: close the non-owner channel.
            remove_whole_channel(channel_id)
                                            # Case 6: the user is not an owner.
    remove_a_member_in_channel(auth_id, channel_id)

    return {
    }

############################################################
#       channel_join(token, channel_id)
############################################################

def channel_join(token, channel_id):
    """Join the user by his/her token into a channel by channel_id.

    Args:
        token: the token of user who is leaving.
        channel_id: the channel which user is leaving.

    Returns:
        None.

    Raises:
        1. InputError
            - the channel id is invalid;
        2. AccessError
            - the channel is PRIVATE.
    """
    target_channel = find_channel(channel_id)
    if target_channel is None:              # InputError 1: invalid channel_id.
        raise InputError('invalid channel_id')

    if not is_channel_public(channel_id):
        raise InputError('channel is PRIVATE')                   # AccessError 2: channel is PRIVATE.

    auth_id = token_into_user_id(token)
    if auth_id == -1:
        raise InputError('invalid token')                    # InputError 3: invalid token.

    new_member_struct = find_user(auth_id)
    user = {                                # Case 4: add this user into member list.
        'u_id': auth_id,
        'name_first': new_member_struct['name_first'],
        'name_last': new_member_struct['name_last'],
        'profile_img_url':''
    }

    add_one_in_channel(channel_id, user)

    return {}
################################################################################
################################################################################
##
##    Yuhan YAN's work:
##    2 October, 2020
##
##      - some helper functions;
##      - channel_addowner(token, channel_id, u_id);
##      - channel_removeowner(token, channel_id, u_id);
##      - and all tests for these functions.
##
################################################################################
################################################################################


############################################################
#      Yuhan's Helper Functions
############################################################

def find_current_owner(channel, u_id):
    """Check if the user we input is the owner."""
    for owners in channel['owner_members']:
        if owners['u_id'] == u_id:
            return True
    return False

def add_owner_in_channel(channel_id, owners):
    """Add a member into the owner list."""

    channels = data.return_channels()

    for users in channels:
        if users['channel_id'] == channel_id:
            users['owner_members'].append(owners)

    data.replace_channels(channels)

def rm_owner_in_channel(channel_id, owners):
    """Remove a member from the owner list."""

    channels = data.return_channels()

    for users in channels:
        if users['channel_id'] == channel_id:
            for onrs in users['owner_members']:
                if onrs['u_id'] == owners:
                    users['owner_members'].remove(onrs)

    data.replace_channels(channels)


############################################################
#       channel_addowner(token, channel_id, u_id)
############################################################

def channel_addowner(token, channel_id, u_id):
    """Make user with user id u_id an owner of this channel.

    Args:
        token: the token of authorised user.
        channel_id: the channel which is adding a owner.
        u_id: the user who would be adding into the owner list.

    Returns:
        None.

    Raises:
        1. InputError
            - channel ID is not a valid channel;
            - when user with user id u_id is already an owner of the channel.
        2. AccessError
            - when the authorized user is not an owner of the flockr;
            - or an owner of this channel(won't focus on flockr this iteration).
    """
    this_channel = find_channel(channel_id)
    if this_channel is None:                # InputError 1: invalid channel_id.
        raise InputError('invalid channel_id')

    auth_id = token_into_user_id(token)
    if auth_id == -1:                       # InputError 2: invalid token.
        raise InputError('invalid token')

    # check whether the user is already an owner
    if find_current_owner(this_channel, u_id):
        raise InputError('user is already owner')                   # InputError 3: check whether user is owner.

    if not find_current_owner(this_channel, auth_id) and check_permission(auth_id) != 1:
        raise InputError('auth is not flockr owner or this channel owner') # AccessError 4: if the auth not in channel.

    owner_detail = find_user(u_id)
    owners = {                              # Case 5: if all passed, add user into owner.
        'u_id': u_id,
        'name_first': owner_detail['name_first'],
        'name_last': owner_detail['name_last'],
        'profile_img_url':''
    }
    add_owner_in_channel(channel_id, owners)
    return {
    }
############################################################
#       channel_removeowner(token, channel_id, u_id)
############################################################

def channel_removeowner(token, channel_id, u_id):
    """Remove user with user id u_id an owner of this channel.

    Args:
        token: the token of authorised user.
        channel_id: the channel which is removing a owner.
        u_id: the user who would be removed from the owner list.

    Returns:
        None.

    Raises:
        1. InputError
            - channel ID is not a valid channel;
            - when user with user id u_id is already an owner of the channel.
        2. AccessError
            - when the authorized user is not an owner of the flockr;
            - or an owner of this channel(won't focus on flockr this iteration).
    """
    this_channel = find_channel(channel_id)
    if this_channel is None:                # InputError 1: invalid channel_id.
        raise InputError('invalid channel_id')

    auth_id = token_into_user_id(token)
    if auth_id == -1:                       # InputError 2: invalid token.
        raise InputError('invalid token')

    if find_current_owner(this_channel, u_id) is False:
        raise InputError('user is not owner')                   # InputError 3: check whether user is owner.

    user = find_user(u_id)
    if user == -1:                          # InputError 4: check if the user_id valid.
        raise InputError('u_id is not valid')

    if find_current_owner(this_channel, auth_id) is False and check_permission(auth_id) != 1:
        raise InputError('auth is not flockr owner or this channel owner')                 # AccessError 5: if the auth not in channel.

    rm_owner_in_channel(channel_id, u_id)   # Case 6: if all passed, pop the user off.
    return {
    }