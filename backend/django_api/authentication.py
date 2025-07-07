from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from .database import get_user_by_id

class SupabaseJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        # Get user from Supabase
        user_data = get_user_by_id(user_id)
        if user_data is None:
            raise InvalidToken('User not found')

        # Create a mock user object
        class SupabaseUser:
            def __init__(self, user_data):
                self.id = user_data['id']
                self.username = user_data['username']
                self.email = user_data.get('email', '')
                self.is_active = True
                self.is_staff = user_data.get('role') == 'admin'
                self.is_superuser = user_data.get('role') == 'admin'
                self.role = user_data.get('role', 'user')
                self._user_data = user_data

            @property
            def pk(self):
                return self.id

            def is_authenticated(self):
                return True

            def __str__(self):
                return self.username

        return SupabaseUser(user_data)