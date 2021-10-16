from Config import MONGO_URI, DB, OWNER
from pymongo import MongoClient
import asyncio

client = MongoClient(MONGO_URI)
Database = client[DB]
Admins = Database['Admins']
Posts = Database['Posts']

def setupMongo():
    if not Admins.find_one({'_id':'admins'}):
        Admins.insert_one({
            '_id': 'admins',
            'users': [OWNER]
        })
    
    if not Admins.find_one({'_id': 'enable'}):
        Admins.insert_one({
            '_id': 'enable',
            'admins': []
        })

    if not Admins.find_one({'_id': 'pin'}):
        Admins.insert_one({
            '_id': 'pin',
            'true': True
        })

async def getDetails(client, msg):
    if msg.reply_to_message:
        id = msg.reply_to_message.from_user.id
        name = msg.reply_to_message.from_user.first_name
    else:
        username = msg.text.replace('/add','').replace('/remove','').replace('/enable','').replace('/disable','')
        if username:
            username = username.strip(' ')
            
            if (username.replace('@','').replace('_','')).isalpha():
                if not username.startswith('@'):
                    await msg.reply(f'"{username}"<b> is Inavlid Username.</b>')
            elif username.isnumeric() and len(username) > 8:
                pass
            else:
                await msg.reply(f'"{username}"<b> is a Invalid Input,\n Use a Username of User id.</b>')

            user = await client.get_chat(username)
            id = user.id
            name = user.first_name
        else:
            id = msg.from_user.id
            name = msg.from_user.first_name
            
    return id,name

async def addAdmin(client,msg):
    id,name = await getDetails(client,msg)
    if not (id in await getAdmins()):
        Admins.update_one({'_id':'admins'},{'$push':{'users':id}})
        return f'<b>Added</b> {name}<b> to Admins List.</b>'
    else: return f'{name} <b>is Already in Admin List.</b>'

async def removeAdmin(client,msg):
    id,name = await getDetails(client,msg)
    if (id in await getAdmins()):
        Admins.update_one({'_id':'admins'},{'$pull':{'users':id}})
        return f'<b>Removed</b> {name}<b> from Admin List.</b>'
    else: return f'{name}<b> is not in Admin List.</b>'

async def getAdmins():
    admins = Admins.find_one({'_id':'admins'})
    if admins: return admins['users']
    else: return []

async def enableAdmin(client, msg):
    id,name = await getDetails(client,msg)
    if (id in await getAdmins()):
        enable = Admins.find_one({'_id':'enable'})
        if not (id in enable['admins']):
            Admins.update_one({'_id':'enable'},{'$push':{'admins':id}})
            return f'<b>Enabled Like/Dislike Buttons for </b>{name}.'
        else: return f'<b>Like/Dislike is Already Enable for </b>{name}'
    else: return f'{name} <b>is not in Admin List!\n Use /add to add Them First.</b>'

async def disableAdmin(client, msg):
    id,name = await getDetails(client,msg)
    if (id in await getAdmins()):
        enable = Admins.find_one({'_id':'enable'})
        if (id in enable['admins']):
            Admins.update_one({'_id':'enable'},{'$pull':{'admins':id}})
            return f'<b>Disabled Like/Dislike Buttons for </b>{name}.'
        else: return f'<b>Like/Dislike is Already Disabled for </b>{name}'
    else: return f'{name} <b>is not in Admin List!\n Use /add to add Them First.</b>'

async def enabledList():
    enable = Admins.find_one({'_id':'enable'})
    if enable: return enable['admins']
    else: return []

async def getEnabled(client):
    admins = Admins.find_one({'_id':'enable'})
    admins = admins['admins']
    admins = await asyncio.gather(*[client.get_chat(id) for id in admins])
    admins = [f'<a href="tg://user?id={admin.id}">{admin.first_name}</a>' for admin in admins]

    text = f'''<b> <u>List of Enabled Admins</u> </b>\n\n• '''
    text += '\n• '.join(admins)
    return text

async def newPost(postId):
    Posts.insert_one({
        '_id':postId,
        'likes':[],
        'dislikes':[]
    })

async def likePost(userId, postId):
    post = Posts.find_one({'_id':postId})
    likes = post['likes'] 
    dislikes = post['dislikes']

    if not (userId in likes):
        if userId in dislikes:
            Posts.update_one({'_id':postId},{'$pull':{'dislikes':userId}})
            Posts.update_one({'_id':postId},{'$push':{'likes':userId}})
            return 'Liked the Post', len(likes) + 1, len(dislikes) - 1
        else:
            Posts.update_one({'_id':postId},{'$push':{'likes':userId}})
            return 'Liked the Post', len(likes) + 1, len(dislikes)
    else:
        Posts.update_one({'_id':postId},{'$pull':{'likes':userId}})
        return 'Reaction took Back', len(likes) - 1, len(dislikes)
    
async def dislikePost(userId, postId):
    post = Posts.find_one({'_id':postId})
    likes = post['likes'] 
    dislikes = post['dislikes']

    if not (userId in dislikes):
        if userId in likes:
            Posts.update_one({'_id':postId},{'$pull':{'likes':userId}})
            Posts.update_one({'_id':postId},{'$push':{'dislikes':userId}})
            return 'Disliked the Post', len(likes) - 1, len(dislikes) + 1
        else:
            Posts.update_one({'_id':postId},{'$push':{'dislikes':userId}})
            return 'Disliked the Post', len(likes), len(dislikes) + 1
    else:
        Posts.update_one({'_id':postId},{'$pull':{'dislikes':userId}})
        return 'Reaction took Back', len(likes), len(dislikes) - 1
    
async def disablePin():
    Admins.update_one({'_id':'pin'},{'$set':{'true':False}})
    return '<i>Pin Channel Posts Disabled.</i>'

async def enablePin():
    Admins.update_one({'_id':'pin'},{'$set':{'true':True}})
    return '<i>Pin Channel Posts Enabled.</i>'

async def pin():
    pin = Admins.find_one({'_id':'pin'})
    return pin['true']
