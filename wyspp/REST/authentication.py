from rest_framework_social_oauth2.authentication import SocialAuthentication

class CustomSocialAuthentication(SocialAuthentication):
    def authenticate(self, request):

        if request.data.get('secret_key') is not None:
            provider = request.path.split('/')[-2]
            if provider == 'google':
                provider= 'google-oauth2'
            request.META['HTTP_AUTHORIZATION'] = 'Bearer {} {}'.format(
                provider, request.data.get('secret_key') )
        authenticate_result = super().authenticate(request)

        if authenticate_result is not None:
            pass
            user, token = authenticate_result
            return user, token
        return None