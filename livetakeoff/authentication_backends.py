from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CaseInsensitiveModelBackend(ModelBackend):
    """
    Custom authentication backend that performs case-insensitive username matching.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Perform case-insensitive lookup for username
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return None
        
        # Check if the provided password is correct
        if user.check_password(password):
            return user
        
        return None

    def get_user(self, user_id):
        """
        Required for the backend to work properly with Django's auth system.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None