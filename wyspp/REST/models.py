from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import  AbstractUser


ActionChoices = (
    ("Like", "Like"),
    ("Comment", "Comment"),
    ("Confirm", "Confirm"),
    ("Challenge", "Challenge"),
    ("Helpful", "Helpful"),
)

PostChoices = (
    ("wyspp", "wyspp"),
    ("news", "news"),
    ("investigative", "investigative"),
    ("missing", "missing"),
    ("translation", "translation")
)
NotificationType = (
    ("confirm", "confirm"),
    ("challenge", "challenge"),
    ("interact", "interact"),
    
)

class User(models.Model):
    class Meta:
        db_table = 'user'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    username = models.CharField(max_length=1000,unique=True)
    password = models.CharField(max_length=1000,null=True)
    email = models.EmailField(max_length=1000,unique=True)
    dob = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.CharField(max_length=1000, default="https://wprdea.org/image/img_avatar.png")
    badge = models.CharField(max_length=1000, null=True)
    social_id=models.CharField(max_length=1000,null=True)
    need_password_change=models.BooleanField(default=False)
    is_private=models.BooleanField(default=True)
    bio=models.CharField(max_length=1000,null=True)
    active = models.BooleanField(null=True)
    email_notify = models.BooleanField(default=False)
    push_notify = models.BooleanField(default=False)
    app_notify = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=1000,null=True)
    confirm_and_challenge_on_wysp = models.BooleanField(default=False)
    wysp_become_news=models.BooleanField(default=False)
    interaction_on_investigative_post=models.BooleanField(default=False)
    comment_on_missing_post=models.BooleanField(default=False)
    comment_on_translate_post=models.BooleanField(default=False)
    hidden_posts = models.ManyToManyField('Post',related_name='hidden_posts')
    reported_posts = models.ManyToManyField('Post',related_name='reported_posts')
    shared_posts = models.ManyToManyField('Post',related_name='shared_posts')
    reported_comments = models.ManyToManyField('Comment',related_name='reported_comments')
    web_fcm_token = models.CharField(max_length=1000,null=True)
    last_notification = models.DateTimeField(null=True)

    def __repr__(self):
        return '<User %s>' % self.name

    def __str__(self):
        return self.username


class Preferences(models.Model):
    class Meta:
        db_table = 'preferences'
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    json_object = models.CharField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<Preferences %s>' % self.json_object

    def __str__(self):
        return self.json_object


class Language(models.Model):
    class Meta:
        db_table = 'language'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    abbreviation = models.CharField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<Language %s>' % self.name

    def __str__(self):
        return 'Language record is added.'


class Post(models.Model):
    class Meta:
        db_table = 'post'
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=1000, choices=PostChoices)
    is_trending = models.BooleanField(null=False, default=0)
    is_anonymous = models.BooleanField(null=False, default=0)
    country = models.CharField(max_length=1000, null=True)
    address = models.CharField(max_length=1000, null=True)
    url = models.CharField(max_length=1000, null=True)
    distance = models.FloatField(null=True)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __repr__(self):
        return '<Post %s>' % self.title

    def __str__(self):
        return self.title


class PostMedia(models.Model):
    class Meta:
        db_table = 'post_media'
    
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True,related_name='media')
    media_path = models.CharField(max_length=1000, default="")
    media_type = models.CharField(max_length=1000, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<PostMedia %s>' % self.media_path

    def __str__(self):
        return 'PostMedia record is added.'


class Comment(models.Model):
    class Meta:
        db_table = 'comment'
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True,related_name='comments')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=1000,blank=True)

    def __repr__(self):
        return '<Comment %s>' % self.id

    def __str__(self):
        return self.message


class Country(models.Model):
    class Meta:
        db_table = 'country'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    logo = models.CharField(max_length=1000)
    alpha2code = models.CharField(max_length=1000, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<Country %s>' % self.name

    def __str__(self):
        return self.name


class State(models.Model):
    class Meta:
        db_table = 'state'
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True,related_name='states')
    alpha2code = models.CharField(max_length=1000, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<State %s>' % self.name

    def __str__(self):
        return self.name


class UserState(models.Model):
    class Meta:
        db_table = 'user_state'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<UserState %s>' % self.id

    def __str__(self):
        return self.state.name


class UserHistory(models.Model):
    class Meta:
        db_table = 'user_history'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=1000, choices=ActionChoices)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<UserHistory %s>' % self.id

    def __str__(self):
        return 'UserHistory record is added.'


class UserBookmarks(models.Model):
    class Meta:
        db_table = 'user_bookmarks'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<UserBookmarks %s>' % self.id

    def __str__(self):
        return 'UserBookmarks record is added.'


class UserInteractions(models.Model):
    class Meta:
        db_table = 'user_interactions'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=1000, choices=ActionChoices)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<UserInteractions %s>' % self.id

    def __str__(self):
        return self.user.id

class Notification(models.Model):

    id = models.AutoField(primary_key=True)
    message = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=NotificationType,max_length=1000)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.message

class AdminUser(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=255,unique=True)
    password = models.CharField(max_length=1000)