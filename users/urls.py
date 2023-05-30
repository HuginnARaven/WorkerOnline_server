from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, TokenVerifyView)


from users.views import ProfileView, ChangePasswordView, TechSupportRequestView

user_router = routers.SimpleRouter()
user_router.register(r'tech-support', TechSupportRequestView, basename='tech-support')


urlpatterns = [
    path('user/', include(user_router.urls)),
    path('change_password/', ChangePasswordView.as_view()),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('profile/', ProfileView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
