import enum


class UserKeys:
    def __init__(self):
        self.telegram_id = 'telegram_id'
        self.instagram_verified = 'instagram_verified'
        self.instagram_username = 'instagram_username'
        self.points = 'points'
        self.verification_comment = 'verification_comments'
        self.user_links = 'user_links'
        self.instagram_id = 'instagram_id'


class LinksKeys:
    def __init__(self):
        self.doc_id = 'links_id'
        self.links_list = 'links_list'
