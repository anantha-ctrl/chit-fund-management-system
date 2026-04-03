from django.contrib.auth.backends import ModelBackend
from .models import User

class RawPasswordBackend(ModelBackend):
    """
    Custom Authentication Backend to support Raw (Plain Text) passwords.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            # LOGGING FOR DEBUGGING
            print(f"DEBUG LOGIN: Trying {username} (DB Password: '{user.password}', Typed: '{password}')")
            
            # DIRECT STRING COMPARISON
            if user.password == password:
                if user.is_active:
                    print("DEBUG LOGIN: Success!")
                    return user
                else:
                    print("DEBUG LOGIN: User is inactive.")
        except User.DoesNotExist:
            print(f"DEBUG LOGIN: User '{username}' not found.")
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
