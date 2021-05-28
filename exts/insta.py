from instagram_private_api import Client
from instagram_web_api import Client as WebClient, errors as weberrors
import json
import os
import requests
import shelve
from pprint import pprint


class Insta:
    def __init__(self):
        self.config = json.load(open('config.json'))
        USERNAME = self.config.get('INSTA_USERNAME')
        PASSWORD = self.config.get('INSTA_PASSWORD')
        settings_dir = './cache'
        if not os.path.exists(settings_dir):
            os.mkdir(settings_dir)
        self.settings_file = f'{settings_dir}/settings'
        if os.path.exists(f'{self.settings_file}.dat'):
            print('Settings files exists!\nRe-using the settings ..')
            with shelve.open(self.settings_file) as shelf:
                settings = shelf['settings']
            self.app_api = Client(USERNAME, PASSWORD, settings=settings)
            print(
                f'Successfully logged-in as {self.app_api.authenticated_user_name}')
        else:
            self.app_api = Client(USERNAME, PASSWORD,
                                  on_login=self.on_app_api_login)

        self.app_api.login()
        self.web_api = WebClient()

    def on_app_api_login(self, app_api):
        with shelve.open(self.settings_file) as shelf:
            shelf['settings'] = app_api.settings
            shelf.sync()
            shelf.close()
        print(
            f'Successfully logged-in as {app_api.authenticated_user_name}')
        print('Settings saved!')

    def get_user_id(self, username):
        try:
            info = self.web_api.user_info2(username)
            return info['id']
        except weberrors.ClientError:
            return None

    def code_to_media_id(self, short_code):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        media_id = 0
        for letter in short_code:
            media_id = (media_id*64) + alphabet.index(letter)

        return media_id

    def get_media_comments(self, post_url, user_id):
        if post_url[-1] == '/':
            post_url = post_url[:-1]
        code = post_url.split('/')[-1]
        media_id = self.code_to_media_id(code)
        comments = self.app_api.media_n_comments(
            media_id, n=10000, reverse=True)
        comments_list = list()
        for comment in comments['comments']:
            if comment['user']['pk'] == user_id:
                comments_list.append(comment['text'])
        return comments_list

    def has_liked(self, post_url, user_id):
        if post_url[-1] == '/':
            post_url = post_url[:-1]
        code = post_url.split('/')[-1]
        media_id = self.code_to_media_id(code)
        likers = self.app_api.media_likers(media_id)
        for user in likers['users']:
            if user['pk'] == user_id:
                return True
        return False
