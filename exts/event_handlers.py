from exts.db import DB
from telethon import events
from telethon.tl.types import Message
from telethon.tl.custom import Button
from telethon.events import StopPropagation
from telethon import TelegramClient
from utils.utils import *
from models.global_vars import *
import json
from exts.db import DB
from exts.insta import Insta


class EventHandlers:
    def __init__(self, bot: TelegramClient):
        self.bot = bot
        self.config = json.load(open('config.json'))
        self.db = DB()
        self.insta = Insta()
        self.verification_post_link = self.config.get("VERIFICATION_POST_LINK")

    async def admin_menu(self, event):
        btns = [
            Button.text('Add Link')
        ]
        await event.respond('Admin Menu', buttons=btns)
        raise StopPropagation

    async def add_new_link(self, event):
        async with self.bot.conversation(event.message.peer_id) as conv:
            await conv.send_message('Please enter the new link?')
            resp = await conv.get_response()
            links = get_links(resp.text)
            self.db.add_link(links[0].replace(
                '?utm_source=ig_web_copy_link', ''))
            await conv.send_message('Link added to the database!')
            raise StopPropagation

    @user_registered
    @insta_verified
    async def list_latest_links(self, event):
        await event.reply('A list of links has been sent to you!\nPlease like/comment on them to get points!')
        links = self.db.get_links()[-15:]
        print(links)
        message = 'List of links to like/comment'
        for link in links:
            message = f'{message}\n{link}'
        message = f'{message}\nPress the "Check my score" button when you have liked/commented these links!'
        btns = [
            Button.inline('Check my score', b'check_score')
        ]
        from_id = event.message.from_id
        await self.bot.send_message(from_id, message, buttons=btns)
        raise StopPropagation

    @dm_only
    async def start_registration(self, event):
        async with self.bot.conversation(event.message.peer_id) as conv:
            await conv.send_message('Please enter your instagram username?')
            resp = await conv.get_response()
            username = resp.text
            await conv.send_message('Please wait while checking your username on instagram.')
            instagram_id = self.insta.get_user_id(username)
            if instagram_id is None:
                await conv.respond('Sorry! Your instagram username is Incorrect/Not Found!')
                raise StopPropagation
            await conv.send_message('Username found on instagram!')
            comment = random_string_generator(40)
            btns = [
                Button.inline('I have commented it.',
                              b'check_insta_verification')
            ]
            await conv.send_message(f'Please go to this --> {self.verification_post_link} instagram post and comment the following string using {username} instagram account to complete the verification of your account..\n\n{comment}', buttons=btns)
            tg_id = event.message.peer_id.user_id
            self.db.add_user(tg_id, username, instagram_id=instagram_id,
                             insta_verified=False,
                             verification_comment=comment)
        raise StopPropagation

    @user_registered
    @insta_verified
    async def new_group_message(self, event):
        tg_id = event.message.peer_id.user_id
        links = get_links(event.message.message)
        insta_links = 0
        for link in links:
            if 'instagram.com' in link:
                insta_links += 1
        if insta_links != 1:
            raise StopPropagation
        if len(links) == 0:
            raise StopPropagation
        if len(links) > 1:
            await event.delete()
            await event.respond('You can post only 1 link in 1 message.\nThank you!')
            raise StopPropagation
        points = int(self.db.get_user_points(tg_id))
        if points < ONE_LINK_POST_COST:
            await event.delete()
            await event.respond('You don\'t have points to post link!')
            raise StopPropagation
        self.db.add_link(links[0].replace('?utm_source=ig_web_copy_link', ''))
        self.db.remove_user_points(tg_id, ONE_LINK_POST_COST)
        raise StopPropagation

    async def list_rules(self, event):
        rules = open('rules.txt').read()
        await event.respond(rules)

    async def check_score(self, event):
        message = await self.bot.get_messages(event.query.peer, ids=[event.query.msg_id])
        await event.delete()
        await event.respond('Please wait while calculating your points..')
        links = get_links(message[0].message)
        user_tg_id = event.query.user_id
        user_insta_id = self.db.get_user_instagram_id(user_tg_id)
        total_score = 0
        for link in links:
            comments = self.insta.get_media_comments(link, user_insta_id)
            for comment in comments:
                score = get_score(comment)
                total_score += score
                if self.insta.has_liked(link, user_insta_id):
                    total_score += ONE_LIKE_REWARD
        self.db.add_user_points(user_tg_id, total_score)
        await event.respond(f'You have got {score} more points!')

    async def check_insta_verification(self, event):
        tg_id = event.query.user_id
        if self.db.is_istagram_verified(tg_id):
            await event.delete()
            await event.respond('Your instagram is already verified!')
            raise StopPropagation
        insta_id = int(self.db.get_user_instagram_id(tg_id))
        verification_comment = self.db.get_user_verification_comment(
            telegram_id=tg_id)
        comments = self.insta.get_media_comments(
            self.verification_post_link, insta_id)
        success = False
        for comment in comments:
            if comment == verification_comment:
                success = True
        if success:
            await event.delete()
            message = 'Your instagram has been verified successfully!\nNow you can post links to the group!'
            self.db.verify_instagram(telegram_id=tg_id)
        else:
            message = f'Could not verify your instagram account!\nPlease comment this\
--> {comment} verification code in comment section of this --> {self.verification_post_link} post.'
        await event.respond(message)
