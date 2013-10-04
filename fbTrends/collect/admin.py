from django.contrib import admin
from collect.models import post, people, comment, like, friends

class collectAdmin(admin.ModelAdmin):
    pass

class postAdmin(admin.ModelAdmin):
    list_display = ('id', 'my_userid', 'full_name', 'created_time')
    list_display_links = ('id', 'my_userid')
    search_fields = ('id', 'my_userid', 'full_name', 'created_time')

    def my_userid(self, obj):
        return '<a href="%s%s">%s</a>' % ('/admin/collect/people/', obj.userid, obj.userid)
    my_userid.allow_tags = True

class peopleAdmin(admin.ModelAdmin):
    list_display = ('userid', 'username', 'full_name', 'gender')
    list_display_links = ('userid', 'username')
    search_fields = ('userid', 'username', 'full_name', 'gender')

class commentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'my_post_id', 'full_name','comment_by_full_name', 'created_time')
    list_display_links = ('comment_id', 'my_post_id',)
    search_fields = ('comment_id', 'post_id', 'full_name','comment_by_full_name', 'created_time')

    def my_post_id(self, obj):
        key = obj.post_id.split('_')
        link = key[0] + '_5F' +key[1]
        return '<a href="%s%s">%s</a>' % ('/admin/collect/post/', link, obj.post_id)
    my_post_id.allow_tags = True

class likeAdmin(admin.ModelAdmin):
    list_display = ('my_post_id', 'my_userid', 'like_by_userid', 'like_by_full_name',)
    list_display_links = ('my_post_id', 'my_userid',)
    search_fields = ('post_id', 'userid', 'like_by_userid', 'like_by_full_name',)

    def my_post_id(self, obj):
        key = obj.post_id.split('_')
        link = key[0] + '_5F' +key[1]
        return '<a href="%s%s">%s</a>' % ('/admin/collect/post/', link, obj.post_id)
    my_post_id.allow_tags = True

    def my_userid(self, obj):
        return '<a href="%s%s">%s</a>' % ('/admin/collect/people/', obj.userid, obj.userid)
    my_userid.allow_tags = True

class friendsAdmin(admin.ModelAdmin):
    list_display = ('friend_userid', 'friend_full_name', 'my_userid', 'full_name',)
    list_display_links = ('friend_userid', 'my_userid',)
    search_fields = ('friend_userid', 'friend_full_name', 'userid', 'full_name',)

    def my_userid(self, obj):
        return '<a href="%s%s">%s</a>' % ('/admin/collect/people/', obj.userid, obj.userid)
    my_userid.allow_tags = True

admin.site.register(post, postAdmin)
admin.site.register(people, peopleAdmin)
admin.site.register(comment, commentAdmin)
admin.site.register(like, likeAdmin)
admin.site.register(friends, friendsAdmin)