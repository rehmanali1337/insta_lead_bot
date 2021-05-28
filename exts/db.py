import sqlite3
from pymongo import MongoClient
from models.global_vars import LINKS_DOC_ID
from models.keys import UserKeys, LinksKeys

keys = UserKeys()
links_keys = LinksKeys()


class DB:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.db
        self.users = self.db.users
        self.links = self.db.links

    def user_exists(self, telegram_id):
        user = self.users.find_one({
            keys.telegram_id: telegram_id
        })
        return True if user else False

    def remove_user(self, telegram_id):
        self.users.delete_one({
            keys.telegram_id: telegram_id
        })

    def add_user(self, telegram_id, insta_username, instagram_id, insta_verified=False,
                 points=0, verification_comment=None):
        user = {
            keys.telegram_id: telegram_id,
            keys.instagram_username:  insta_username,
            keys.instagram_id: instagram_id,
            keys.instagram_verified: insta_verified,
            keys.points: points,
            keys.verification_comment: verification_comment,
            keys.user_links: []}
        self.users.insert_one(user)

    def get_user_verification_comment(self, telegram_id):
        user = self.users.find_one({
            keys.telegram_id: telegram_id
        })
        return user[keys.verification_comment]

    def get_user_points(self, telegram_id):
        user = self.users.find_one({
            keys.telegram_id: telegram_id
        })
        return user[keys.points]

    def add_user_points(self, telegram_id, points):
        self.users.find_one_and_update({
            keys.telegram_id: telegram_id
        }, {
            '$inc': {
                keys.points: points
            }
        })

    def remove_user_points(self, telegram_id, points):
        self.users.find_one_and_update({
            keys.telegram_id: telegram_id
        }, {
            '$inc': {
                keys.points: -points
            }
        })

    def get_user_instagram_id(self, telegram_id):
        user = self.users.find_one({
            keys.telegram_id: telegram_id
        })
        return user[keys.instagram_id]

    def is_istagram_verified(self, telegram_id) -> bool:
        return True

    def verify_instagram(self, telegram_id):
        self.users.find_one_and_update({
            keys.telegram_id: telegram_id
        }, {
            '$set': {
                keys.instagram_verified: True
            }
        }
        )

    def get_links(self):
        links = self.links.find_one({links_keys.doc_id: links_keys.doc_id})
        if links:
            return links[links_keys.links_list]
        return []

    def add_link(self, link):
        links = self.links.find_one({
            links_keys.doc_id: links_keys.doc_id})
        if not links:
            links = {
                links_keys.doc_id: links_keys.doc_id,
                links_keys.links_list: [link]
            }
            self.links.insert_one(links)
            return
        self.links.find_one_and_update({
            links_keys.doc_id: links_keys.doc_id
        }, {
            '$addToSet': {links_keys.links_list: link}
        })

    def update_user_links_list(self, telegram_id, new_list):
        self.users.find_one_and_update({
            keys.telegram_id: telegram_id
        }, {
            '$push': {keys.user_links: {'$each': []}}
        })
