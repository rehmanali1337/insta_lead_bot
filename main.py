from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
from exts.event_handlers import EventHandlers
import json
import logging
import asyncio
import os


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.ERROR)

config = json.load(open('config.json'))

PHONE_NUMBER = config.get("TELEGRAM_PHONE_NUMBER")
BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN")

if not os.path.exists('sessionFiles'):
    os.mkdir('sessionFiles')
bot = TelegramClient('sessionFiles/bot',
                     config.get("TELEGRAM_API_ID"), config.get("TELEGRAM_API_HASH"))
client = TelegramClient('sessionFiles/client',
                        config.get("TELEGRAM_API_ID"), config.get("TELEGRAM_API_HASH"))


event_handlers = EventHandlers(bot)


async def setup_event_handlers():
    group_link = config.get("GROUP_LINK")
    admin_username = config.get("ADMIN_TELEGRAM_USERNAME")
    me = await bot.get_me()
    bot_id = me.id

    def not_self(event):
        if not isinstance(event.message.peer_id, PeerChannel):
            return event.message.peer_id.user_id != bot_id
        return False

    en = await client.get_entity(group_link)
    bot.add_event_handler(event_handlers.start_registration,
                          events.NewMessage(pattern='/start'))
    bot.add_event_handler(event_handlers.list_latest_links, events.NewMessage(
        chats=[en.id], pattern='/links'))
    bot.add_event_handler(event_handlers.new_group_message,
                          events.NewMessage(chats=[en.id], func=not_self))
    bot.add_event_handler(event_handlers.list_rules, events.NewMessage(
        pattern='/rules', chats=[en.id]))
    bot.add_event_handler(event_handlers.check_score,
                          events.CallbackQuery(data=b'check_score'))
    bot.add_event_handler(event_handlers.check_insta_verification,
                          events.CallbackQuery(data=b'check_inta_verification'))
    bot.add_event_handler(event_handlers.admin_menu,
                          events.NewMessage(pattern='/admin', chats=[admin_username]))
    bot.add_event_handler(event_handlers.add_new_link,
                          events.NewMessage(chats=[admin_username]))


async def on_ready():
    if not client.is_connected():
        await asyncio.sleep(1)
    if not bot.is_connected():
        await asyncio.sleep(1)
    if not await client.is_user_authorized():
        await asyncio.sleep(1)
    if not await bot.is_user_authorized():
        await asyncio.sleep(1)
    await setup_event_handlers()
    print('Bot and client is ready!')

try:
    client.start(phone=PHONE_NUMBER)
    bot.start(bot_token=BOT_TOKEN)
    bot.loop.create_task(on_ready())
    bot.run_until_disconnected()
except KeyboardInterrupt:
    print('Quiting bot ...')
    exit()
