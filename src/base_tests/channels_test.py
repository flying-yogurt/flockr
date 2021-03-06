import src.base.auth as auth
import src.base.channels as channels
import pytest
import src.data.data as data
from src.base.error import InputError
import src.base.channel as channel
import random
from src.base.other import clear

def test_owner_from_token():
    clear()
    #create a user and take its  id and token
    user1 = auth.auth_register('12345@test.com', 'password', 'FirstN', 'LastN')
    u1_token = user1['token']
    token_tem = u1_token + ' '
    with pytest.raises(InputError):
        channels.owner_from_token(token_tem)

def test_channels_create():
    clear()

    #create a user and take its  id and token
    user1 = auth.auth_register('12345@test.com', 'password', 'FirstN', 'LastN')
    u1_id = user1['u_id']
    u1_token = user1['token']

    #check the error when the channelname is too long
    with pytest.raises(InputError):
        channels.channels_create(u1_token,'A_very_very_very_ver_long_name',True)

    #create a channel in channels and return its channel id
    channel_1_id = channels.channels_create(u1_token,'team',True).get('channel_id')
    #assert channel_1_id is int
    assert data.return_channels()[-1]['name'] == 'team'
    assert data.return_channels()[-1]['channel_id'] == channel_1_id
    assert data.return_channels()[-1]['is_public'] == True
    assert data.return_channels()[-1]['owner_members'][0]['u_id'] == u1_id
    assert data.return_channels()[-1]['owner_members'][0]['name_first'] == 'FirstN'
    assert data.return_channels()[-1]['owner_members'][0]['name_last'] == 'LastN'

    assert data.return_channels()[-1]['all_members'][0]['u_id'] == u1_id
    assert data.return_channels()[-1]['all_members'][0]['name_first'] == 'FirstN'
    assert data.return_channels()[-1]['all_members'][0]['name_last'] == 'LastN'


def test_channels_listall():
    clear()

    #create two user and take their id and token
    user1 = auth.auth_register('1234@test.com', 'password', 'FirstN', 'LastN')
    user1 = auth.auth_login('1234@test.com', 'password')
    u1_token = user1['token']

    user2 = auth.auth_register('2345@test.com', 'password', 'FirstN2', 'LastN2')
    user2 = auth.auth_login('2345@test.com', 'password')
    u2_token = user2['token']

    #create a channel by user1 in channels and return its channel id
    channel_1_id = channels.channels_create(u1_token,'team',True).get('channel_id')

    #create a channel by user2 in channels and return its channel id
    channel_2_id = channels.channels_create(u2_token,'team2',True).get('channel_id')

    #check if the function return them all
    l_test = channels.channels_listall(u1_token).get('channels')
    assert len(l_test) == 2
    assert l_test[0]['channel_id'] == channel_1_id
    assert l_test[1]['channel_id'] == channel_2_id
    assert l_test[0]['name'] == 'team'
    assert l_test[1]['name'] == 'team2'

def test_channels_list():
    '''
    channels_list rewritten by Joseph to make it match spec

    Needs to return all channels where user1 is a member
    '''
    clear()

    #create two user and take their id and token
    user1 = auth.auth_register('45@test.com', 'password', 'FirstN', 'LastN')
    token1 = user1.get('token')
    user2 = auth.auth_register('415@test.com', 'password2', 'FirstN21', 'LastN2')
    token2 = user2.get('token')
    user3 = auth.auth_register('425@test.com', 'password3', 'FirstN1', 'LastN3')
    token3 = user3.get('token')

    # create channels and invite users into each channel
    public_channels = [channels.channels_create(token3,'u3-1',True)]
    # create user1 and invite them to the public channel
    user1_channels = [channels.channels_create(token1,'u1-1',False)]
    channel.channel_invite(token3, public_channels[0].get('channel_id'), user1.get('u_id'))

    # create user2 and invite them to the public channel
    user2_channels = [channels.channels_create(token2,'u2-1',False), channels.channels_create(token2,'u2-2',False)]
    channel.channel_invite(token3, public_channels[0].get('channel_id'), user2.get('u_id'))

    # authorised channels for user1
    auth_channels1 = channels.channels_list(token1).get('channels')

    # user 1 should have 2 channels visible
    assert len(auth_channels1) == (len(user1_channels) + len(public_channels))

    # authorised channels for user2
    auth_channels2 = channels.channels_list(token2).get('channels')

    # user 2 should have 3 channels visible
    assert len(auth_channels2) == (len(user2_channels) + len(public_channels))

    # authorised channels for user3
    auth_channels3 = channels.channels_list(token3).get('channels')

    # user 3 should only have public channels visible
    assert len(auth_channels3) == len(public_channels)
