from django.db import models
from jsonfield import JSONField

class post(models.Model):
    def __unicode__(self):
        return self.id
    id = models.CharField(max_length=200, primary_key=True)
    userid = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    created_time = models.DateTimeField()
    post_json = JSONField()

class people(models.Model):
    def __unicode__(self):
        return self.username
    userid = models.CharField(max_length=200, primary_key=True)
    username = models.CharField(max_length=200, unique=True)
    full_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10)
    profile_json = JSONField()

class comment(models.Model):
    def __unicode__(self):
        return self.comment_id
    comment_id = models.CharField(max_length=200, primary_key=True)
    userid = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    post_id = models.CharField(max_length=200)
    comment_by_userid = models.CharField(max_length=200)
    comment_by_full_name = models.CharField(max_length=200)
    created_time = models.DateTimeField()
    comment_json = JSONField()

    class Meta:
        unique_together = (("post_id", "comment_id"),)


class like(models.Model):
    def __unicode__(self):
        return self.post_id
    post_id = models.CharField(max_length=200)
    userid = models.CharField(max_length=200)
    like_by_userid = models.CharField(max_length=200)
    like_by_full_name = models.CharField(max_length=200)

    class Meta:
        unique_together = (("post_id", "like_by_userid"),)


class friends(models.Model):
    def __unicode__(self):
        return self.full_name
    userid = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    friend_userid = models.CharField(max_length=200)
    friend_full_name = models.CharField(max_length=200)

    class Meta:
        unique_together = (("userid", "friend_userid"),)

