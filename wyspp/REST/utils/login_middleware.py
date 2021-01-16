from rest_framework_jwt.utils import jwt
from REST.models import User , AdminUser

def verify_jwt(token):
  try:
      token = jwt.decode(token[4:], 'xyz', algorithm='HS256')
      user = User.objects.get(pk=token['id'])      
      if user.password !=token['password']:
          return False
      return token
  except:
      return False

def verify_jwt_admin(token):
  try:
      token = jwt.decode(token[4:], 'xyz', algorithm='HS256')
      admin = AdminUser.objects.get(pk=token['id'])      
      if admin.password !=token['password']:
          return False
      return token
  except:
      return False