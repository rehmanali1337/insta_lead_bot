import re
from exts.db import DB
import random
import string
from telethon.events import StopPropagation
from telethon.tl.types import PeerChannel

db = DB()


def get_score(comment: str):
    words = comment.split(' ')
    if len(words) >= 4:
        return 4
    elif len(words) < 4:
        return 2


def get_links(text):
    url_regex = re.compile(r'(https?:\/\/[^\s]+)')
    return url_regex.findall(text)


def user_registered(func):
    async def wrapper(_, event):
        tg_id = event.message.from_id.user_id
        if not db.user_exists(tg_id):
            await event.delete()
            await event.respond('Sorry! You are not registered yet!')
            raise StopPropagation
        await func(_, event)
    return wrapper


def insta_verified(func):
    async def inner(_, event):
        tg_id = event.message.from_id.user_id
        if not db.is_istagram_verified(tg_id):
            await event.delete()
            await event.respond('You must verify your instagram account before posting links')
            raise StopPropagation
        await func(_, event)

    return inner


def dm_only(func):
    async def wrapper(_, event):
        if isinstance(event.message.peer_id, PeerChannel):
            print('Channel message')
            raise StopPropagation
        await func(_, event)
    return wrapper


def random_string_generator(str_size):
    allowed_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(allowed_chars) for x in range(str_size))


if __name__ == '__main__':
    text1 = 'Find me at http://www.example.com and also at http://stackoverflow.com'
    text2 = 'Hello there'
    get_links(text2)
