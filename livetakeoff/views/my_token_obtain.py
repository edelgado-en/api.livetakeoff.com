from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.contrib.auth.models import User

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Calls TokenObtainPairView and then updates the last_login field of the user.
    We are using the last_login value to flag first-time logins.
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        username = request.data.get('username')

        user = User.objects.get(username=username)

        first_time_login = user.last_login is None

        user.last_login = timezone.now()
        user.save()

        response.data['first_time_login'] = first_time_login

        return response
