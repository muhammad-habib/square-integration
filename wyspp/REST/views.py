import json
import random
import string
from ast import literal_eval

import requests
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.db import DatabaseError, connection, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from fcm_django.models import FCMDevice
from pyfcm import FCMNotification
from requests.exceptions import HTTPError
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import (AuthForbidden, AuthTokenError,
                                    MissingBackend)
from social_django.utils import load_backend, load_strategy
from wyspp import settings

from .models import *
from .serializers import *
from .utils.custom_response import CustomResponse
from .utils.gcs import uploadFile
from .utils.login_middleware import verify_jwt, verify_jwt_admin


def randomized_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@api_view(['POST', 'GET', 'DELETE'])
def bookmarks(request):
    if request.method == 'DELETE':
        token = request.headers.get('authorization')
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''DELETE FROM user_bookmarks WHERE user_id={}'''.format(
                            user_id)
                    )
                    cursor.close()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="No JWT found", status=status.HTTP_200_OK)
    elif request.method == 'POST':
        created_at = timezone.now()
        updated_at = timezone.now()
        post_id = request.data.get('post_id')
        token = request.headers.get('authorization')
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO user_bookmarks(post_id, created_at, updated_at, user_id) VALUES (%s, %s, %s, %s);", [post_id, created_at, updated_at, user_id])
                    cursor.execute(
                        '''select id from user_bookmarks order by created_at desc ''')
                    rows = cursor.fetchall()
                    bookmark_id = rows[0][0]
                    cursor.close()
                    result = CustomResponse(True, bookmark_id).toJSON()

                return Response(data=result, status=status.HTTP_201_CREATED)
            else:
                return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="No JWT found", status=status.HTTP_200_OK)
    elif request.method == 'GET':
        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 10)
        token = request.headers.get('authorization')
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
                bookmarks = []
                rows = []
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''SELECT p.id, p.type, p.title, p.description, p.lat, p.lng, p.country, p.address, p.created_at, p.is_trending, p.owner_id, ub.id, p.distance
                            FROM user_bookmarks ub, "user" u, post p
                            WHERE u.id = ub.user_id AND u.id = {} AND ub.post_id = p.id AND p.deleted=false
                            ORDER BY ub.id desc LIMIT {} OFFSET {}
                        '''.format(user_id, limit, offset)
                    )
                    rows = cursor.fetchall()
                    cursor.close()
                    for i in rows:
                        bookmark = dict()
                        bookmark['id'] = i[0]
                        bookmark['type'] = i[1]
                        bookmark['title'] = i[2]
                        bookmark['description'] = i[3]
                        bookmark['location'] = [i[4], i[5]]
                        bookmark['country'] = i[6]
                        bookmark['address'] = i[7]
                        bookmark['created_at'] = i[8]
                        bookmark['is_bookmarked'] = True
                        if i[9] == 0:
                            bookmark['is_trending'] = False
                        elif i[9] == 1:
                            bookmark['is_trending'] = True
                        bookmark['bookmark_id'] = i[11]
                        bookmark['distance'] = i[12]
                        with connection.cursor() as cur:
                            cur.execute(
                                '''SELECT id, username, avatar, badge FROM "user" WHERE id={}
                                '''.format(i[10])
                            )
                            r = cur.fetchone()
                            badges = []
                            badges.append(r[3])
                            owner = dict()
                            owner['id'] = r[0]
                            owner['username'] = r[1]
                            owner['avatar'] = r[2]
                            owner['badge'] = badges
                            bookmark['owner'] = owner
                            cur.close()
                        with connection.cursor() as cur:
                            cur.execute('''
                            select id, media_path, media_type from post_media where post_id = {}
                            '''.format(bookmark['id']))
                            med = cur.fetchall()
                            bookmark['media_collection'] = []
                            for j in med:
                                pm = dict()
                                pm['id'] = j[0]
                                pm['media_path'] = j[1]
                                pm['media_type'] = j[2]
                                bookmark['media_collection'] += [pm]
                            cur.close()
                        with connection.cursor() as cur:
                            cur.execute('''
                                select count(*) number_interactions from user_interactions where post_id = {}
                            '''.format(bookmark['id']))
                            bookmark['number_interactions'] = cur.fetchone()[0]
                            cur.close()
                        bookmarks += [bookmark]

                    result = CustomResponse(True, bookmarks).toJSON()
                    return Response(data=result, status=status.HTTP_200_OK)
            else:
                return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="No JWT found", status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_bookmark(request, id):
    token = request.headers.get('authorization')
    if token:
        user = verify_jwt(token)
        if user:
            user_id = user['id']
            with connection.cursor() as cursor:
                cursor.execute(
                    '''SELECT * FROM user_bookmarks WHERE user_id={} AND post_id={}'''.format(user_id, id))
                rows = cursor.fetchone()
                if rows == None:
                    cursor.close()
                    return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
                else:
                    cursor.execute(
                        '''DELETE FROM user_bookmarks WHERE post_id={}'''.format(
                            id)
                    )
                    cursor.close()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(data="No JWT found", status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def get_add_posts(request):
    if request.method == 'GET':
        country = request.GET.get('country', None)
        type = request.GET.get('type', '%')
        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 10)
        sort = request.GET.get('sort', 'date')
        search = request.GET.get('search', '%')
        search_key = "%"
        for word in search:
            if word != ' ':
                search_key += word
            elif word == ' ':
                search_key += "%"
                search_key += word
                search_key += "%"
        search_key += "%"

        if sort != 'date':
            sort = 'interaction_count'
        is_trending = request.GET.get('is_trending', None)
        posts = []
        rows = []
        token = request.headers.get('authorization')
        with connection.cursor() as cursor:
            user_id = None
            if token:
                user = verify_jwt(token)
                if user:
                    user_id = user['id']
                    user_countries = ''
                    user_c_list = []
                    user_states = UserState.objects.filter(user__id=user_id)
                    if not user_states:
                        result = CustomResponse(True, posts).toJSON()
                        return Response(data=result, status=status.HTTP_200_OK)
                    for state in user_states:
                        user_c_list.append(state.state.alpha2code)
                        user_countries += "'" + state.state.alpha2code + "'" + ','
                    user_obj = User.objects.get(pk=user_id)
                    if is_trending == None:
                        cursor.execute(
                            '''SELECT p.id, p.type, p.title, p.description, u.id, u.username, p.lat, p.lng, p.created_at, p.is_trending, u.avatar, u.badge, p.address, p.is_anonymous ,extract(epoch FROM p.created_at) as date, p.distance,u.is_private
                                , count(ui.id) as interaction_count
                                from post p
                                join 
                                "user" u on (u.id = p.owner_id) 
                                left join user_interactions ui on ( ui.post_id = p.id )   
                                where p.type like '{}' and (p.country in({}) or p.owner_id = {}) and p.deleted = False and (p.title like '{}' or p.description like '{}')
                                group by (p.id,u.id)
                                order by {} desc limit {} offset {}
                            '''.format(type, user_countries[:-1], user_id, search_key, search_key, sort, limit, offset)
                        )
                    else:
                        cursor.execute(
                            '''SELECT p.id, p.type, p.title, p.description, u.id, u.username, p.lat, p.lng, p.created_at, p.is_trending, u.avatar, u.badge, p.address, p.is_anonymous,extract(epoch FROM p.created_at) as date, p.distance,u.is_private
                                , count(ui.id) as interaction_count
                                from post p
                                join 
                                "user" u on (u.id = p.owner_id) 
                                left join user_interactions ui on ( ui.post_id = p.id ) 
                                where p.type like '{}' and (p.country in({}) or p.owner_id = {}) and p.is_trending = '{}' and p.deleted = False and (p.title like '{}' or p.description like '{}')
                                group by (p.id,u.id)
                                order by {} desc limit {} offset {}
                            '''.format(type, user_countries[:-1], user_id, is_trending, search_key, search_key, sort, limit, offset)
                        )
                    rows = cursor.fetchall()
                else:
                    return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
            else:
                if is_trending == None:
                    cursor.execute(
                        '''SELECT p.id, p.type, p.title, p.description, u.id, u.username, p.lat, p.lng, p.created_at, p.is_trending, u.avatar, u.badge, p.address, p.is_anonymous, extract(epoch FROM p.created_at) as date, p.distance,u.is_private
                            , count(ui.id) as interaction_count
                            from post p
                            join
                            "user" u on (u.id = p.owner_id)
                            left join user_interactions ui on ( ui.post_id = p.id ) 
                            where p.type like '{}' and p.country = '{}' and p.deleted = False and (p.title like '{}' or p.description like '{}')
                            group by (p.id,u.id)
                            order by {} desc limit {} offset {}
                        '''.format(type, country, search_key, search_key, sort, limit, offset)
                    )
                else:
                    cursor.execute(
                        '''SELECT p.id, p.type, p.title, p.description, u.id, u.username, p.lat, p.lng, p.created_at, p.is_trending, u.avatar, u.badge, p.address, p.is_anonymous, extract(epoch FROM p.created_at) as date, p.distance,u.is_private
                            , count(ui.id) as interaction_count
                            from post p
                            join 
                            "user" u on (u.id = p.owner_id) 
                            left join user_interactions ui on ( ui.post_id = p.id ) 
                            where p.type like '{}' and p.country = '{}' and p.is_trending = '{}' and p.deleted = False and (p.title like '{}' or p.description like '{}')
                            group by (p.id,u.id)
                            order by {} desc limit {} offset {}
                        '''.format(type, country, is_trending, search_key, search_key, sort, limit, offset)
                    )
                rows = cursor.fetchall()

            for i in rows:
                post = dict()
                post['id'] = i[0]
                post['type'] = i[1]
                post['title'] = i[2]
                post['description'] = i[3]
                is_private = False
                if i[4]:
                    badges = []
                    if i[11]:
                        badges.append(i[11])
                if not i[13]:
                    if i[16]:
                        is_private = True
                    owner = dict()
                    owner['id'] = i[4]
                    owner['username'] = i[5]
                    owner['avatar'] = i[10]
                    owner['badge'] = badges
                    owner['is_private'] = is_private
                    post['is_anonymous'] = False
                else:
                    owner = None
                    post['is_anonymous'] = True
                post['owner'] = owner
                if i[6] and i[7]:
                    post['location'] = [i[6], i[7]]
                else:
                    post['location'] = []
                post['created_at'] = i[8]
                if i[9] == 0:
                    post['is_trending'] = False
                elif i[9] == 1:
                    post['is_trending'] = True
                post['address'] = i[12]

                post['distance'] = i[15]
                cursor.close()
                with connection.cursor() as cur:
                    cur.execute('''
                        select count(*) number_interactions from user_interactions where post_id = {}
                    '''.format(i[0]))
                    post['number_interactions'] = cur.fetchone()[0]
                    cur.close()
                with connection.cursor() as cur:
                    cur.execute('''
                        select media_path , media_type from post_media where post_id = {}
                    '''.format(i[0]))
                    med = cur.fetchall()
                    post['media_collection'] = []
                    for j in med:
                        pm = dict()
                        pm['media_path'] = j[0]
                        pm['media_type'] = j[1]
                        post['media_collection'] += [pm]
                    cur.close()
                if user_id:
                    with connection.cursor() as cur:
                        cur.execute('''
                            select * from user_bookmarks where user_id = {} and post_id = {}
                        '''.format(user_id, post['id']))
                        row = cur.fetchone()
                        if row == None:
                            post['is_bookmarked'] = False
                        else:
                            post['is_bookmarked'] = True
                else:
                    post['is_bookmarked'] = None
                posts += [post]
        result = CustomResponse(True, posts).toJSON()
        return Response(data=result, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        title = request.data.get('title')
        description = request.data.get('description')
        type = request.data.get('type')
        lat = request.data.get('lat', None)
        lng = request.data.get('lng', None)
        post_media = request.data.get('post_media')
        country = request.data.get('country')
        address = request.data.get('address', None)
        is_anonymous = request.data.get('is_anonymous', False)
        distance = request.data.get('distance', None)

        created_at = timezone.now()
        updated_at = timezone.now()
        is_trending = False

        token = request.headers.get('authorization')
        if token:
            user = verify_jwt(token)
            if user:
                owner_id = user['id']
                connection.autocommit = False
                with connection.cursor() as cursor:
                    if is_anonymous == True:
                        is_anonymous = True
                    else:
                        is_anonymous = False
                    post_id = cursor.execute(
                        '''INSERT INTO post(
                            title,
                            description,
                            type,
                            created_at,
                            updated_at,
                            lat,
                            lng,
                            country,
                            address,
                            owner_id,
                            is_anonymous,
                            distance,
                            is_trending,
                            deleted
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s);''',
                        [
                            title,
                            description,
                            type,
                            created_at,
                            updated_at,
                            lat,
                            lng,
                            country,
                            address,
                            owner_id,
                            is_anonymous,
                            distance,
                            is_trending,
                            False
                        ]
                    )
                    cursor.execute(
                        '''select id from post order by created_at desc ''')
                    rows = cursor.fetchall()
                    post_id = rows[0][0]
                    if post_media is not None:
                        for i in post_media:
                            cursor.execute(
                                '''INSERT INTO post_media
                                (post_id, media_path, created_at, updated_at, media_type)
                                VALUES(%s, %s, %s, %s, %s)
                                ''', [post_id, i['media_path'], created_at, updated_at, i['media_type']])
                    cursor.close()
                    connection.commit()
                    connection.autocommit = True
                    result = CustomResponse(True, post_id).toJSON()
                return Response(data=result, status=status.HTTP_201_CREATED)
            else:
                return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="No JWT found", status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_file(request):
    fileUploaded = uploadFile(request.FILES.get('my_file'))
    print(fileUploaded)
    result = CustomResponse(True, fileUploaded).toJSON()
    return Response(data=result, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user_hashed_password = User.objects.get(email=email).password
    if check_password(request.data.get('password'), user_hashed_password):
        with connection.cursor() as cursor:
            cursor.execute('''SELECT id, name, username, email, dob, avatar, badge , is_private , need_password_change ,  active , email_notify,app_notify,push_notify , created_at , confirm_and_challenge_on_wysp ,wysp_become_news ,interaction_on_investigative_post , comment_on_missing_post,  comment_on_translate_post 
            FROM "user" WHERE email = %s AND password = %s;''', [
                           email, user_hashed_password])
            row = cursor.fetchone()
            cursor.close()
            user = dict()
            badges = []
            if(row[6]):
                badges.append(row[6])
            need_password_change = False
            is_private = False
            confirm_and_challenge_on_wysp = False
            wysp_become_news = False
            interaction_on_investigative_post = False
            comment_on_missing_post = False
            comment_on_translate_post = False
            email_notify = False
            app_notify = False
            push_notify = False

            if row[8]:
                need_password_change = True
            if row[7]:
                is_private = True
            if row[10]:
                email_notify = True
            if row[11]:
                app_notify = True
            if row[12]:
                push_notify = True
            if row[14]:
                confirm_and_challenge_on_wysp = True
            if row[15]:
                wysp_become_news = True
            if row[16]:
                interaction_on_investigative_post = True
            if row[17]:
                comment_on_missing_post = True
            if row[18]:
                comment_on_translate_post = True

            user['id'] = row[0]
            user['name'] = row[1]
            user['username'] = row[2]
            user['email'] = row[3]
            user['dob'] = row[4]
            user['avatar'] = row[5]
            user['badge'] = badges
            user['is_private'] = is_private
            user['need_password_change'] = need_password_change
            user['active'] = row[9]
            user['email_notify'] = email_notify
            user['push_notify'] = push_notify
            user['app_notify'] = app_notify
            user['creation_date'] = row[13]
            user['confirm_and_challenge_on_wysp'] = confirm_and_challenge_on_wysp
            user['wysp_become_news'] = wysp_become_news
            user['interaction_on_investigative_post'] = interaction_on_investigative_post
            user['comment_on_missing_post'] = comment_on_missing_post
            user['comment_on_translate_post'] = comment_on_translate_post

            payload = {
                'id': row[0],
                'name': row[1],
                'username': row[2],
                'email': row[3],
                'dob': row[4].__str__(),
                'avatar': row[5],
                'badge': badges,
                'is_private': is_private,
                'need_password_change': need_password_change,
                'active': row[9],
                'email_notify': email_notify,
                'push_notify': push_notify,
                'app_notify': app_notify,
                'creation_date': str(row[13]),
                'confirm_and_challenge_on_wysp': confirm_and_challenge_on_wysp,
                'wysp_become_news': wysp_become_news,
                'interaction_on_investigative_post': interaction_on_investigative_post,
                'comment_on_missing_post': comment_on_missing_post,
                'comment_on_translate_post': comment_on_translate_post,
                'password': user_hashed_password
            }
            token = jwt.encode(payload, 'xyz', algorithm='HS256')

            res = {}
            res['user'] = user
            res['token'] = token
            result = CustomResponse(True, res).toJSON()
            return Response(data=result, status=status.HTTP_200_OK)
    return Response({"error": "Wrong Password"}, status=status.HTTP_400_BAD_REQUEST)


class SignUPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        json_response = {}
        serializer = SingUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.password = make_password(request.data.get(
                'password'), salt=None, hasher='default')
            user.save()
            perefrence = str({'language': 'English', 'units': 'Metric'})
            prefernnce_data = {
                'json_object': perefrence,
                'user': user.id
            }
            pref_serializer = PreferencesSerializer(data=prefernnce_data)

            if pref_serializer.is_valid():
                pref_serializer.save()
            else:
                return Response(pref_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            json_response['success'] = True
            is_private = False
            need_password_change = False
            email_notify = False
            app_notify = False
            push_notify = False
            confirm_and_challenge_on_wysp = False
            wysp_become_news = False
            interaction_on_investigative_post = False
            comment_on_missing_post = False
            comment_on_translate_post = False
            if user.confirm_and_challenge_on_wysp:
                confirm_and_challenge_on_wysp = True
            if user.wysp_become_news:
                wysp_become_news = True
            if user.interaction_on_investigative_post:
                interaction_on_investigative_post = True
            if user.comment_on_missing_post:
                comment_on_missing_post = True
            if comment_on_translate_post:
                comment_on_translate_post = True
            if user.is_private:
                is_private = True
            if user.need_password_change:
                need_password_change = True
            if user.email_notify:
                email_notify = True
            if user.app_notify:
                app_notify = True
            if user.push_notify:
                push_notify = True
            badges = []
            if user.badge:
                badges.append(user.badge)
            payload = {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'dob': str(user.dob),
                'avatar': user.avatar,
                'badge': badges,
                'is_private': is_private,
                'need_password_change': need_password_change,
                'active': user.active,
                'email_notify': email_notify,
                'push_notify': push_notify,
                'app_notify': app_notify,
                'creation_date': str(user.created_at),
                'confirm_and_challenge_on_wysp': user.confirm_and_challenge_on_wysp,
                'wysp_become_news': user.wysp_become_news,
                'interaction_on_investigative_post': user.interaction_on_investigative_post,
                'comment_on_missing_post': user.comment_on_missing_post,
                'comment_on_translate_post': user.comment_on_translate_post,
                'password': user.password
            }
            token = jwt.encode(payload, 'xyz', algorithm='HS256')

            json_response['data'] = {"user": payload, "token": token}

            return Response(json_response, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class SocialLoginView(APIView):
    def post(self,request,type):

        user = request.user
        json_response = {}
        if type=='facebook':
            user, created = User.objects.get_or_create(
                password=user.password, social_id=type, username=user.username, name =f'{user.first_name} {user.last_name}' ,created_at=user.date_joined,active=True,email=f'{user.username}@facebook.com')
        elif type=='google' or type=='twitter':
            user, created = User.objects.get_or_create(
                password=user.password, social_id=type, username=user.username ,created_at=user.date_joined,active=True,email=user.email)

        if created :
            perefrence = str({'language': 'English', 'units': 'Metric'})
            prefernnce_data = {
                    'json_object': perefrence,
                    'user': user.id
            }
            pref_serializer = PreferencesSerializer(data=prefernnce_data)

            if pref_serializer.is_valid():
                pref_serializer.save()
            else:
                return Response(pref_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        is_private = False
        need_password_change = False
        email_notify = False
        app_notify = False
        confirm_and_challenge_on_wysp = False
        wysp_become_news = False
        interaction_on_investigative_post = False
        comment_on_missing_post = False
        comment_on_translate_post = False
        push_notify = False
        if user.is_private:
            is_private = True
        if user.need_password_change:
            need_password_change = True
        if user.email_notify:
            email_notify = True
        if user.app_notify:
            app_notify = True
        if user.push_notify:
            push_notify = True
        if user.confirm_and_challenge_on_wysp:
            confirm_and_challenge_on_wysp = True
        if user.wysp_become_news:
            wysp_become_news = True
        if user.interaction_on_investigative_post:
            interaction_on_investigative_post = True
        if user.comment_on_missing_post:
            comment_on_missing_post = True
        if comment_on_translate_post:
            comment_on_translate_post = True
        badges = []
        if user.badge:
            badges.append(user.badge)
        payload = {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'email': user.email,
            'dob': user.dob,
            'avatar': user.avatar,
            'badge': badges,
            'is_private': is_private,
            'need_password_change': need_password_change,
            'active': user.active,
            'email_notify': email_notify,
            'push_notify': push_notify,
            'app_notify': app_notify,
            'creation_date': str(user.created_at),
            'confirm_and_challenge_on_wysp': user.confirm_and_challenge_on_wysp,
            'wysp_become_news': user.wysp_become_news,
            'interaction_on_investigative_post': user.interaction_on_investigative_post,
            'comment_on_missing_post': user.comment_on_missing_post,
            'comment_on_translate_post': user.comment_on_translate_post,
            'password':user.password,
            'is_login':not created

        }
        token = jwt.encode(payload, 'xyz', algorithm='HS256')
        json_response['success'] = True
        json_response['data'] = {"user": payload, "token": token}

        return Response(json_response, status=status.HTTP_201_CREATED)


class userPostInteraction(APIView):
    def post(self, request, id, action):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        data = {"user": user_id, "action": action, "post": id}
        serializer = userPostInteractionSerializer(data=data)
        post = Post.objects.get(pk=id)

        if(action == 'Comment'):
            if serializer.is_valid():
                serializer.save()
                if post.owner.push_notify and (post.type == 'investigative' or post.type == 'missing'):
                    notification = Notification(
                        message=f'someone {action} your {post.type} {post.title}', user=post.owner, type=action)
                    notification.save()
                    push_new_notification(notification)

                if post.owner.email_notify and (post.type == 'investigative' or post.type == 'missing'):
                    notification = Notification(
                        message=f'someone {action} your {post.type} {post.title}', user=post.owner, type=action)
                    notification.save()
                    send_mail('Notification Email', f'someone {action} your {post.type} {post.title}',
                              'do-not-reply@wyspp.com',
                              [post.owner.email])
                return Response({"detail": "Successfully added"}, status=status.HTTP_201_CREATED)
        else:
            try:
                user_interaction = (UserInteractions.objects.filter(
                    user=user_id, post=id).exclude(action='Comment'))[0]
                user_interaction.action = action
                user_interaction.save()
                bool = False
                if post.owner.push_notify and post.type == 'wyspp':
                    notification = Notification(
                        message=f'someone {action} your {post.type} {post.title}', user=post.owner, type=action)
                    notification.save()
                    bool = True
                    push_new_notification(notification)
                if post.owner.email_notify and post.type == 'wyspp':
                    notification = Notification(
                        message=f'someone {action} your {post.type} {post.title}', user=post.owner, type=action)
                    if not bool:
                        notification.save()
                    send_mail('Notification Email', f'someone {action} your {post.type} {post.title}',
                              'do-not-reply@wyspp.com',
                              [post.owner.email])
                return Response({"detail": "Updated Successfully"}, status=status.HTTP_200_OK)
            except:
                if serializer.is_valid():
                    serializer.save()
                    return Response({"detail": "Successfully added"}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserCountryView(APIView):
    def post(self, request):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        countries_to_create = []
        countries_to_delete = []
        user = User.objects.get(id=user_id)
        user_states = UserState.objects.filter(user=user).delete()
        for i in request.data['countries']:
            state = State.objects.get(id=i)
            try:
                user_state = UserState.objects.get(user=user_id, state=i)
            except:
                countries_to_create.append(UserState(state=state, user=user))
        UserState.objects.bulk_create(countries_to_create)

        return Response({"detail": "Updated Successfully"}, status=status.HTTP_200_OK)

    def get(self, request):
        user_states_ids = []
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(id=user_id)
        countries = Country.objects.order_by('name')
        user_states = UserState.objects.filter(user=user)
        for state in user_states:
            user_states_ids.append(state.state.id)
        serializer = getCountriesSerializer(countries, many=True, context={
                                            "state_ids": user_states_ids})
        return Response({"list": serializer.data})


class ResetPassword(APIView):
    def post(self, request, format=None):
        try:
            user = User.objects.get(email=request.data['email'])
        except:
            return Response({"error": "No User With This Email"}, status=status.HTTP_401_UNAUTHORIZED)
        password_raw = randomized_code(10)
        user.password = make_password(password_raw)
        user.need_password_change = 1
        user.save()
        send_mail('Reset Password Email', f'your new password  is {password_raw}',
                  'do-not-reply@wyspp.com',
                  [user.email])
        return Response({"detail": ("Please Check Your Email.")}, status=status.HTTP_200_OK)


class CommentView(APIView):
    def post(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        request.data.update({"user": user_id, "post": id})
        serializer = AddCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            post = Post.objects.get(pk=id)
            bool = False
            if post.owner.push_notify and (post.type == 'missing' or post.type == 'investigative'):
                notification = Notification(
                    message=f'someone Comment on  your {post.type} {post.title}', user=post.owner, type='Comment')
                notification.save()
                bool = True
                push_new_notification(notification)
            if post.owner.email_notify and (post.type == 'missing' or post.type == 'investigative'):
                notification = Notification(
                    message=f'someone Comment on your {post.type} {post.title}', user=post.owner, type='Comment')
                if not bool:
                    notification.save()
                send_mail('Notification Email', f'someone Comment on your {post.type} {post.title}',
                          'do-not-reply@wyspp.com',
                          [post.owner.email])

            request.data.update({'action': 'Comment'})
            interactionserializer = userPostInteractionSerializer(
                data=request.data)
            if interactionserializer.is_valid():
                interactionserializer.save()
            return Response({"detail": "Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        comment = Comment.objects.get(pk=pk)
        if comment.user.id == user_id:
            comment.delete()
            return Response({"detail": "Deleted Successfully"}, status=status.HTTP_200_OK)
        return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)


class PostView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        password = make_password('123456', salt=None, hasher='default')
        print(password)
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        try:
            post = Post.objects.get(id=id, deleted=False)
        except:
            return Response({"error": "Sorry this attachment has been deleted"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PostSerializer(post, context={"user": user_id})
        json_response = {}
        json_response['success'] = True
        json_response['data'] = serializer.data
        return Response(json_response, status=status.HTTP_200_OK)

    def put(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        try:
            post = Post.objects.get(pk=id, owner__id=user_id)
            post.deleted = True
            post.save()
            return Response({"detail": "Updated Successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "This action is forbidden for this user"}, status=status.HTTP_401_UNAUTHORIZED)


class userPereference(APIView):
    def post(self, request, pk):
        data = {}
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        data['json_object'] = str(request.data)
        try:
            user_preference = Preferences.objects.get(user__id=user_id)
            serializer = PreferencesSerializer(
                user_preference, data=data, partial=True)
        except:
            data['user'] = user_id
            serializer = PreferencesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Success"}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        user_preference = Preferences.objects.get(user__id=user_id)
        serializer = PreferencesSerializer(user_preference)
        json_object = literal_eval(serializer.data['json_object'])
        res = {}
        res['language'] = json_object["language"]
        res['units'] = json_object["units"]
        return Response(res, status=status.HTTP_200_OK)


class userFeeds(APIView):
    def get(self, request, pk, type):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        res = {}
        feeds = []
        posts = ''
        posts_ids = []
        if type == 'post' or type == 'all':
            try:
                posts = Post.objects.filter(
                    owner__id=pk, deleted=False).order_by('created_at')
                for post in posts:
                    serializer = userFeedsPostSerializer(
                        post, context={"user": pk})
                    feeds.append({"type": "post", "data": serializer.data})
            except:
                None
        if type == 'comment' or type == 'all':
            try:
                comments = Comment.objects.filter(
                    user__id=pk).order_by('created_at')
                for comment in comments:
                    serializer = CommentSerializer(comment)
                    feeds.append({"type": "Comment", "data": serializer.data})
            except:
                None
        if type == 'interaction' or type == 'all':
            try:
                user_interactions = UserInteractions.objects.filter(
                    user__id=pk).order_by('created_at')
                for interaction in user_interactions:
                    serializer = UserInteractionsSerializer(interaction)
                    json_response = {}
                    json_response = serializer.data
                    if(interaction.action == 'Comment'):
                        comment = Comment.objects.get(
                            created_at=interaction.created_at, post=interaction.post, user=interaction.user)
                        serializer = CommentSerializer(comment)
                        json_response['comment'] = serializer.data

                    feeds.append(
                        {"type": "interaction", "data": json_response})
            except:
                None
            for post in posts:
                posts_ids.append(post.id)
            try:
                posts_interactions = UserInteractions.objects.filter(
                    post__id__in=posts_ids, post__deleted=False).order_by('created_at')
                for interaction in posts_interactions:
                    json_response = {}
                    serializer = UserInteractionsSerializer(interaction)
                    json_response = serializer.data
                    if(interaction.action == 'Comment'):
                        comment = Comment.objects.get(
                            created_at=interaction.created_at, post=interaction.post, user=interaction.user)
                        serializer = CommentSerializer(comment)
                        json_response['comment'] = serializer.data
                    feeds.append(
                        {"type": "interaction", "data": json_response})
            except:
                None
        res['feeds'] = feeds
        return Response(res, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    def post(self, request):
        json_response = {}
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user_id = jwt.decode(token[4:], 'xyz', algorithm='HS256')['id']
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(pk=user_id)
            user.password = make_password(serializer.data['new_password'])
            user.need_password_change = 0
            user.save()
            json_response['success'] = True
            is_private = False
            need_password_change = False
            email_notify = False
            app_notify = False
            push_notify = False
            if user.is_private:
                is_private = True
            if user.need_password_change:
                need_password_change = True
            if user.email_notify:
                email_notify = True
            if user.app_notify:
                app_notify = True
            if user.push_notify:
                push_notify = True
            if user.is_private:
                is_private = True
            if user.need_password_change:
                need_password_change = True
            badges = []
            badges.append(user.badge)
            payload = {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'dob': str(user.dob),
                'avatar': user.avatar,
                'badge': badges,
                'is_private': is_private,
                'need_password_change': need_password_change,
                'active': user.active,
                'email_notify': email_notify,
                'push_notify': push_notify,
                'app_notify': app_notify,
                'creation_date': str(user.created_at),
                'password': user.password
            }
            token = jwt.encode(payload, 'xyz', algorithm='HS256')
            json_response['data'] = {"user": payload, "token": token}

            return Response(json_response, status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    def put(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(pk=id)
        serializer = UpdateUserSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Updated Successfully"}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(pk=id)
        json_response = {}
        json_response['success'] = True
        if user_id == int(id) or not user.is_private:
            serializer = PublicUserSerializer(user)
            json_response['data'] = serializer.data
            return Response(json_response, status=status.HTTP_200_OK)
        else:
            json_response['data'] = PrivateUserSerializer(user).data
            return Response(json_response, status=status.HTTP_200_OK)


def push_new_notification(notification):
    try:
        token = User.objects.get(pk=notification.user.id).fcm_token
        push_service = FCMNotification(api_key=settings.FIREBASE_API_KEY)

        data_message = {
            "message": notification.message,
            "time": str(notification.time),
            "type": notification.type,
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
        result = push_service.notify_single_device(
            registration_id=token, message_body=notification.message, data_message=data_message)

        print("RESULT", result)
        return
    except Exception as e:
        print(e)
        pass


class HidePostView(APIView):
    def post(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(pk=user_id)
            post = Post.objects.get(pk=id)
            user.hidden_posts.add(post)
            user.save()
            return Response({"detail": ("Post Added To Hidden")})
        except Post.DoesNotExist:
            return Response({"error": ("No Post")}, status=status.HTTP_400_BAD_REQUEST)


class SharePostView(APIView):
    def post(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(pk=user_id)
            post = Post.objects.get(pk=id)
            user.shared_posts.add(post)
            user.save()
            return Response({"detail": ("Post Shared Successfully")})
        except Post.DoesNotExist:
            return Response({"error": ("No Post")}, status=status.HTTP_400_BAD_REQUEST)


class ReportPostView(APIView):
    def post(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = Post.objects.get(pk=id, owner__id=user_id)
            return Response({"error": ("Sorry you cannot report this post")}, status=status.HTTP_400_BAD_REQUEST)
        except:
            try:
                user = User.objects.get(pk=user_id)
                print(user_id)
                post = Post.objects.get(pk=id)
                user.reported_posts.add(post)
                user.save()
                return Response({"detail": ("Post Reported Successfully")})
            except Post.DoesNotExist:
                return Response({"error": ("No post")}, status=status.HTTP_400_BAD_REQUEST)


class ReportComment(APIView):
    def post(self, request, id):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        try:
            comment = Comment.objects.get(pk=id, user__id=user_id)
            return Response({"error": ("Sorry you cannot report your comment")}, status=status.HTTP_400_BAD_REQUEST)
        except:
            try:
                user = User.objects.get(pk=user_id)
                comment = Comment.objects.get(pk=id)
                user.reported_comments.add(comment)
                user.save()
                return Response({"detail": ("Comment Reported Successfully")})
            except Comment.DoesNotExist:
                return Response({"error": ("No comment")}, status=status.HTTP_400_BAD_REQUEST)


class GetAllNotifications(APIView):
    def get(self, request):
        token = request.headers.get('authorization')
        user_id = None
        if token:
            user = verify_jwt(token)
            if user:
                user_id = user['id']
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(pk=user_id)
        notifications = Notification.objects.filter(
            user=user).order_by('-time')
        if user.last_notification:
            seen_notifications = notifications.filter(
                time__lte=user.last_notification)
            for notification in seen_notifications:
                notification.is_seen = True
                notification.save()
        if len(notifications) != 0:
            user.last_notification = notifications[0].time
            user.save()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

# Admin Apis


class AdminLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        json_response = {}
        password = make_password(request.data['password'])
        try:
            admin = AdminUser.objects.get(email=request.data['email'])
        except:
            return Response(data='Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        payload = {
            'id': admin.id,
            'email': admin.email,
            'type': 'admin',
            'password': admin.password
        }
        token = jwt.encode(payload, 'xyz', algorithm='HS256')
        json_response['success'] = True
        json_response['data'] = {"admin": payload, "token": token}
        return Response({"detail": json_response})


class AdminUserView(APIView):
    def get(self, request):
        token = request.headers.get('authorization')
        if token:
            admin = verify_jwt_admin(token)
            if not admin:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            users = User.objects.all()
            serializer = PublicUserSerializer(users, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, id):
        user = User.objects.get(pk=id)
        serializer = AdminUpdateUserSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Updated Successfully"}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AddAdmin(APIView):
    def post(self, request):
        token = request.headers.get('authorization')
        if token:
            admin = verify_jwt_admin(token)
            if not admin:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            serializer = AddAdminSerializer(data=request.data)
            if serializer.is_valid():
                admin = serializer.save()
                admin.password = make_password(request.data['password'])
                admin.save()
                return Response({"detail": "Added Successfully"})
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ReportedPosts(APIView):
    def get(self, request):
        json_response = {}
        token = request.headers.get('authorization')
        if token:
            admin = verify_jwt_admin(token)
            if not admin:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            users = User.objects.all()
            count = 0
            posts = []
            for user in users:
                if user.reported_posts.all().count() != 0:
                    for reported_post in user.reported_posts.all():
                        if reported_post not in posts:
                            posts.append(reported_post)
            serializer = AdminPostSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class DeletePost(APIView):
    def delete(self, request, id):
        token = request.headers.get('authorization')
        if token:
            admin = verify_jwt_admin(token)
            if admin:
                try:
                    post = Post.objects.get(pk=id).delete()
                    return Response({"detail": "Deleted Successfully"}, status=status.HTTP_200_OK)
                except:
                    return Response({"error": "NO Post with this id"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
