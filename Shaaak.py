from Config import SUDO, ADMINCHAT, CHANNEL, GROUP, LINK, BOT_USERNAME 
from Config import API_ID, API_HASH, BOT_TOKEN
from pyrogram import Client, filters
from pyrogram.types import *
from MongoDB import *
import asyncio

bot = Client(
    'Shaaak',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

@bot.on_message(filters.command(['start', f'start@{BOT_USERNAME}']))
async def start(client:Client,msg:Message):
    await msg.reply_text('<b>This shaaak says Hello to you,' + \
            'Have a Nice Day.</b>\n<i>Now Shu~Shu go away---</i>')

@bot.on_message(filters.command(['add',f'add@{BOT_USERNAME}']))
async def addMain(client:Client, msg:Message):
    if not (msg.chat.type == 'private') and (msg.chat.id != ADMINCHAT):
        return await msg.reply('<i>I won\'t Listen to You, shu~shu...</i>')
    if not msg.from_user.id in SUDO:
        return await msg.reply('<i>Boo! You aren\'t a Sudo User.</i>')

    await msg.reply(await addAdmin(client,msg))
            
@bot.on_message(filters.command(['remove',f'remove@{BOT_USERNAME}']))
async def removeMain(client:Client, msg:Message):
    if not (msg.chat.type == 'private') and (msg.chat.id != ADMINCHAT):
        return await msg.reply('<i>I won\'t Listen to You, shu~shu...</i>')
    if not msg.from_user.id in SUDO:
        return await msg.reply('<i>Boo! You aren\'t a Sudo User.</i>')

    await msg.reply(await removeAdmin(client,msg))

@bot.on_message(filters.command(['enable',f'enable@{BOT_USERNAME}']))
async def enableMain(client:Client, msg:Message):
    if not (msg.chat.type == 'private') and (msg.chat.id != ADMINCHAT):
        return await msg.reply('<i>I won\'t Listen to You, shu~shu...</i>')
    
    await msg.reply(await enableAdmin(client,msg))

@bot.on_message(filters.command(['disable',f'disable@{BOT_USERNAME}']))
async def disableMain(client:Client, msg:Message):
    if not (msg.chat.type == 'private') and (msg.chat.id != ADMINCHAT):
        return await msg.reply('<i>I won\'t Listen to You, shu~shu...</i>')
    await msg.reply(await disableAdmin(client,msg))

@bot.on_message(filters.command(['getList',f'getList@{BOT_USERNAME}']))
async def getListMain(client:Client, msg:Message):
    if not (msg.chat.type == 'private') and (msg.chat.id != ADMINCHAT):
        return await msg.reply('<i>I won\'t Listen to You, shu~shu...</i>')
    await msg.reply(await getEnabled(client))

async def addButtons(client:Client, msgId:int, postId:int):
    buttons = [
        [InlineKeyboardButton('👍',callback_data=f'like|{msgId}|{postId}'),
        InlineKeyboardButton('👎',callback_data=f'dislike|{msgId}|{postId}')],
        [InlineKeyboardButton('💬 Comments',url=LINK.format(msgId,msgId))]
    ]
    markup = InlineKeyboardMarkup(buttons)
    await newPost(postId)
    await client.edit_message_reply_markup(chat_id=CHANNEL,message_id=postId,reply_markup=markup)

@bot.on_message(filters.command(['enablepin',f'enablepin@{BOT_USERNAME}','disablepin',f'disablepin@{BOT_USERNAME}']))
async def pinHandler(client:Client,msg:Message):
    user = await client.get_chat_member(GROUP,msg.from_user.id)
    if not user.status in ['creator','administrator']:
        return await msg.reply('<i>Only Admemes Please.</i>')

    if msg.text.startswith('/enablepin'):
        text = await enablePin()
    elif msg.text.startswith('/disablepin'):
        text = await disablePin()
    await msg.reply(text)

@bot.on_callback_query(filters.create(lambda _,__,query: query.data.startswith('like') or query.data.startswith('dislike')))
async def reactCallbacks(client:Client, query: CallbackQuery):
    reaction = query.data.split('|')[0]
    msgId = int(query.data.split('|')[1])
    postId = int(query.data.split('|')[2])
    userId = query.from_user.id 

    if reaction == 'like':
        msg, likes, dislikes = await likePost(userId,postId)
    elif reaction == 'dislike':
        msg, likes, dislikes = await dislikePost(userId,postId)
    
    buttons = [
        [InlineKeyboardButton(f'👍 {likes}',callback_data=f'like|{msgId}|{postId}'),
        InlineKeyboardButton(f'👎 {dislikes}',callback_data=f'dislike|{msgId}|{postId}')],
        [InlineKeyboardButton('💬 Comments',url=LINK.format(msgId,msgId))]
    ]
    markup = InlineKeyboardMarkup(buttons)
    await query.answer(msg)
    await client.edit_message_reply_markup(chat_id=CHANNEL,message_id=postId,reply_markup=markup)
    
    
@bot.on_message(filters.chat([GROUP]))
async def listenGroup(client:Client, msg:Message):
    if not msg.forward_from_chat:
        return

    if msg.forward_from_chat.id == CHANNEL:
        if not await pin():
            await msg.unpin()

        admins = await enabledList()
        names = await asyncio.gather(*[client.get_chat(admin) for admin in admins])
        names = [f'{name.first_name}{f" {name.last_name}" if name.last_name != None else ""}' for name in names]

        if msg.forward_signature in names:
            msgId = msg.message_id
            postId = msg.forward_from_message_id   
            await addButtons(client, msgId, postId)   

if __name__ == '__main__':
    setupMongo()
    bot.run()
