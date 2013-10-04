from django.db import IntegrityError
from collect.models import post, people, comment, like, friends
import requests

class collect:

    ACCESS_TOKEN = ''
    post_no = 0
    comment_no = 0
    like_no = 0
    friend_no = 0

    def api_call(self, **kwargs):
        '''
        Returns API call string as per given parameters
        '''
        source_id = kwargs.pop('source_id')
        stream = kwargs.pop('stream')
        call = 'https://graph.facebook.com/' + source_id + '/' + stream + '/?access_token=' + self.ACCESS_TOKEN + '&limit=500'
        return call

    def save_post(self, p):
        '''
        Recieves a post json and saves it into collect_post.
        Calls save_like and save_comment to save likes and comments respectively
        '''
        post_obj = post(
                    id = p['id'],
                    userid = p['from']['id'],
                    full_name = p['from']['name'],
                    created_time = p['created_time'],
                    post_json = p,
            )
        try:
            post_obj.save()
            self.post_no += 1
            print self.post_no, 'POST    ' + p['created_time'] , p['id'] , p['from']['name']
        except IntegrityError, e:
            pass

        if p.has_key('likes'):
            self.save_like(
                userid = p['from']['id'],
                post_id = p['id'],
                likes_json=p['likes']
            )
        if p.has_key('comments'):
            self.save_comment(
                userid=p['from']['id'],
                full_name=p['from']['name'],
                post_id=p['id'],
                comments_json = p['comments']
            )

    def save_comment(self, comments_json=None, **kwargs):
        '''
        Recieves comments_json and save it into collect_comment
        '''
        userid = kwargs.pop('userid')
        full_name = kwargs.pop('full_name')
        post_id = kwargs.pop('post_id')

        while comments_json['data']:
            for c in comments_json['data']:
                comment_obj = comment(
                    comment_id = c['id'],
                    userid = userid,
                    full_name = full_name,
                    post_id = post_id,
                    comment_by_userid = c['from']['id'],
                    comment_by_full_name = c['from']['name'],
                    created_time = c['created_time'],
                    comment_json = c,
                )
                try:
                    comment_obj.save()
                    self.comment_no += 1
                    print self.comment_no, 'COMMENT' , c['created_time'] , c['id'] , c['from']['name']

                except IntegrityError, e:
                    pass

            if comments_json['paging'].has_key('next'):
                comment_call = comments_json['paging']['next']
                comments_json = requests.get(comment_call).json()
            else:
                break

    def save_like(self, likes_json=None, **kwargs):
        '''
        Recieves likes_json and save it into collect_comment
        '''
        post_id = kwargs.pop('post_id')
        userid = kwargs.pop('userid')

        while likes_json['data']:
            for l in likes_json['data']:
                like_obj = like(
                    post_id = post_id,
                    userid = userid,
                    like_by_userid = l['id'],
                    like_by_full_name = l['name'],
                )
                try:
                    like_obj.save()
                    self.like_no += 1
                    print self.like_no, 'LIKE   ' , l['id'] , l['name']

                except IntegrityError, e:
                    pass
            if likes_json['paging'].has_key('next'):
                like_call = likes_json['paging']['next']
                likes_json = requests.get(like_call).json()
            else:
                break

    def save_friend_list(self, userid, full_name):
        '''
        Saves friend list info into collect_friends
        '''
        friends_call = self.api_call(source_id=userid, stream='friends')
        friends_json = requests.get(friends_call).json()

        while friends_json['data']:
            for f in friends_json['data']:
                friend_obj =  friends(
                    userid = userid,
                    full_name = full_name,
                    friend_userid = f['id'],
                    friend_full_name = f['name'],
                )
                try:
                    friend_obj.save()
                    self.friend_no += 1
                    print self.friend_no, 'FRIENDS' , f['id'] , f['name']
                except IntegrityError, e:
                    pass

            if friends_json['paging'].has_key('next'):
                friends_call = friends_json['paging']['next']
                friends_json = requests.get(friends_call).json()
            else:
                break

    def save_people(self, userid='me'):
        '''
        Saves user info into collect_people
        '''
        people_call = self.api_call(source_id=userid, stream='')
        people_json = requests.get(people_call).json()
        if userid == 'me':
            userid = people_json['id']
        people_obj = people(
                    userid = userid,
                    username = people_json['username'],
                    full_name = people_json['name'],
                    gender = people_json['gender'],
                    profile_json = people_json
        )
        people_obj.save()
        print 'PEOPLE ' , people_json['username'] , people_json['username']
        self.save_friend_list(userid, people_json['name'])

    def start(self):
        self.save_people()
        call_link = self.api_call(source_id='me', stream='feed')
        call = requests.get(call_link)
        posts_json = call.json()

        while posts_json['data']:
            for p in posts_json['data']:
                self.save_post(p)

            call_link = posts_json['paging']['next']
            call = requests.get(call_link)
            posts_json = call.json()

    def __init__(self, *args, **kwargs):
        self.ACCESS_TOKEN = kwargs.pop('access_token')