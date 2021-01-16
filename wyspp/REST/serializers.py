from rest_framework import serializers
from .models import *


class PublicUserSerializer(serializers.ModelSerializer):
    badge = serializers.SerializerMethodField()
    need_password_change = serializers.SerializerMethodField()
    no_of_posts = serializers.SerializerMethodField()
    no_of_interactions = serializers.SerializerMethodField()
    creation_date = serializers.SerializerMethodField()
    is_private = serializers.SerializerMethodField()
    email_notify = serializers.SerializerMethodField()
    push_notify = serializers.SerializerMethodField()
    app_notify = serializers.SerializerMethodField()
    confirm_and_challenge_on_wysp = serializers.SerializerMethodField()
    wysp_become_news = serializers.SerializerMethodField()
    interaction_on_investigative_post = serializers.SerializerMethodField()
    comment_on_missing_post = serializers.SerializerMethodField()
    comment_on_translate_post = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'dob', 'avatar', 'badge', 'need_password_change',
                  'no_of_posts', 'no_of_interactions', 'creation_date', 'is_private', 'bio', 'active', 'email_notify', 'push_notify', 'app_notify',
                  'confirm_and_challenge_on_wysp', 'wysp_become_news', 'interaction_on_investigative_post', 'comment_on_missing_post', 'comment_on_translate_post')
    def get_badge(self, obj):
        badges = []
        if obj.badge:
            return [obj.badge]
        else:
            return badges
    def get_need_password_change(self, obj):
        if obj.need_password_change:
            return True
        return False

    def get_is_private(self, obj):
        if obj.is_private:
            return True
        return False
    def get_email_notify(self, obj):
        if obj.email_notify:
            return True
        return False
    def get_push_notify(self, obj):
        if obj.push_notify:
            return True
        return False
    def get_app_notify(self, obj):
        if obj.app_notify:
            return True
        return False

    def get_no_of_posts(self, obj):
        return Post.objects.filter(owner=obj).count()

    def get_no_of_interactions(self, obj):
        return UserInteractions.objects.filter(user=obj).count()

    def get_creation_date(self, obj):
        return str(obj.created_at)

    def get_confirm_and_challenge_on_wysp(self, obj):
        if obj.confirm_and_challenge_on_wysp:
            return True
        return False
    def get_wysp_become_news(self, obj):
        if obj.wysp_become_news:
            return True
        return False
    def get_interaction_on_investigative_post(self, obj):
        if obj.interaction_on_investigative_post:
            return True
        return False
    def get_comment_on_missing_post(self, obj):
        if obj.comment_on_missing_post:
            return True
        return False
    def get_comment_on_translate_post(self, obj):
        if obj.comment_on_translate_post:
            return True
        return False

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ('media_path', 'media_type')


class ownerSerializer(serializers.ModelSerializer):
    badge = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'badge', 'is_private')

    def get_badge(self, obj):
        badges = []
        if obj.badge:
            return [obj.badge]
        else:
            return badges


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    number_interactions = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    media_collection = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    no_of_confirms = serializers.SerializerMethodField()
    no_of_challenges = serializers.SerializerMethodField()
    is_confirm = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'type', 'is_trending', 'is_anonymous', 'country', 'address', 'url', 'distance', 'created_at', 'updated_at',
                  'owner', 'location', 'number_interactions', 'is_bookmarked', 'media_collection', 'comments', 'no_of_confirms', 'no_of_challenges', 'is_confirm')

    def get_owner(self, obj):
        if obj.is_anonymous:
            return None
        serializer = ownerSerializer(obj.owner)
        return serializer.data

    def get_location(self, obj):
        if(obj.lat and obj.lng):
            return [obj.lat, obj.lng]
        else:
            return []

    def get_number_interactions(self, obj):
        return UserInteractions.objects.filter(post__id=obj.id).count()

    def get_is_bookmarked(self, obj):
        try:
            UserBookmarks.objects.get(
                user__id=self.context.get("user"), post__id=obj.id)
            return True
        except:
            return False

    def get_media_collection(self, obj):
        return PostMediaSerializer(obj.media, many=True).data


    def get_no_of_confirms(self, obj):
        return UserInteractions.objects.filter(
            post__id=obj.id, action="Confirm").count()
        

    def get_no_of_challenges(self, obj):
        return UserInteractions.objects.filter(
            post__id=obj.id, action="Challenge").count()

    def get_is_confirm(self, obj):
        try:
            UserInteractions.objects.get(
                post__id=obj.id, user=self.context.get("user"),action="Confirm")
            return True
        except:
            pass
        try:
            UserInteractions.objects.get(
                post__id=obj.id, user=self.context.get("user"), action="Challenge")
            return False
        except:
            pass
        
        return None
    def get_comments(self, obj):
        if not self.context.get("comments"):
            return CommentSerializer(obj.comments.all().order_by('-created_at'), many=True).data

class AddCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ('id', 'created_at', 'updated_at', 'message', 'owner','post')

    def get_owner(self, obj):
        serializer = ownerSerializer(obj.user)
        return serializer.data

    def get_post(self,obj):
        return PostSerializer(obj.post,context={"comments":"No comments"}).data

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class UserStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserState
        fields = '__all__'


class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = '__all__'


class UserBookmarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookmarks
        fields = '__all__'


class CustomeCommenntSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'message', 'created_at')

class userFeedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'type')


class CustomePostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'type', 'comments')

    def get_comments(self, obj):
        return CustomeCommenntSerializer(obj.comments.all(), many=True).data


class UserInteractionsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = UserInteractions
        fields = ('id', 'created_at', 'updated_at', 'action', 'user', 'post')

    def get_post(self, obj):
        if obj.action=='Comment':
            return userFeedPostSerializer(obj.post).data
        else:
            return CustomePostSerializer(obj.post).data

            

    def get_user(self, obj):
        serializer = ownerSerializer(obj.user)
        return serializer.data


class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class SignUpSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'social_id', 'username')
    extra_kwargs = {
        'password': {'required': False},
    }


class userPostInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteractions
        fields = '__all__'


class UserCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class StatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('id', 'name')


class getCountriesSerializer(serializers.ModelSerializer):
    states = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ('id', 'name', 'states')

    def get_states(self, obj):
        state_ids = self.context.get("state_ids")
        states = StatesSerializer(obj.states.all(), many=True).data
        for state in states:
            if state['name'] != obj.name:
                state['name'] = state['name'] + ','+obj.name
            if state['id'] in state_ids:
                state['user_state'] = True
            else:
                state['user_state'] = False

        return states


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, max_length=50)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('bio', 'avatar', 'is_private', 'email_notify', 'push_notify', 'app_notify', 'fcm_token', 'active', 'confirm_and_challenge_on_wysp',
                  'wysp_become_news', 'interaction_on_investigative_post', 'comment_on_missing_post', 'comment_on_translate_post','web_fcm_token')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'message', 'type', 'time', 'is_seen')


class userFeedsPostSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    number_interactions = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    media_collection = serializers.SerializerMethodField()
    no_of_confirms = serializers.SerializerMethodField()
    no_of_challenges = serializers.SerializerMethodField()
    is_confirm = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'type', 'is_trending', 'is_anonymous', 'country', 'address', 'url', 'distance', 'created_at',
                  'updated_at', 'owner', 'location', 'number_interactions', 'is_bookmarked', 'media_collection', 'no_of_confirms', 'no_of_challenges', 'is_confirm')

    def get_owner(self, obj):
        serializer = ownerSerializer(obj.owner)
        return serializer.data

    def get_location(self, obj):
        if(obj.lat and obj.lng):
            return [obj.lat, obj.lng]
        else:
            return []

    def get_number_interactions(self, obj):
        return UserInteractions.objects.filter(post__id=obj.id).count()

    def get_is_bookmarked(self, obj):
        try:
            UserBookmarks.objects.get(
                user__id=self.context.get("user"), post__id=obj.id)
            return True
        except:
            return False

    def get_media_collection(self, obj):
        return PostMediaSerializer(obj.media, many=True).data

    def get_no_of_confirms(self, obj):
        return UserInteractions.objects.filter(
            post__id=obj.id, action="Confirm").count()
        

    def get_no_of_challenges(self, obj):
        return UserInteractions.objects.filter(
            post__id=obj.id, action="Challenge").count()
        

    def get_is_confirm(self, obj):
        try:
            UserInteractions.objects.get(
                post__id=obj.id, user=self.context.get("user"),action="Confirm")
            return True
        except:
            pass
        try:
            UserInteractions.objects.get(
                post__id=obj.id, user=self.context.get("user"), action="Challenge")
            return False
        except:
            pass
        
        return None


class PrivateUserSerializer(serializers.ModelSerializer):
    is_private = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'is_private')

    def get_is_private(self, obj):
        if obj.is_private:
            return True
        else:
            return False

# Admin Serializer
class AdminLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ('email','password',)

class AddAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = '__all__'

class AdminUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('active',)

class AdminPostSerializer(PostSerializer):

    number_of_reports = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = PostSerializer.Meta.fields + ('number_of_reports','is_deleted')
        
    def get_number_of_reports(self,obj):
        return obj.reported_posts.all().count()
    
    def get_is_deleted(self,obj):
        return obj.deleted
    
class SocialSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)
