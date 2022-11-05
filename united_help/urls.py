"""united_help URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from united_help import views

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


router = routers.SimpleRouter()
router.register(r'users', views.UserView)
router.register(r'profiles', views.ProfileView)
router.register(r'events', views.EventsView)
router.register(r'cities', views.CityView)
router.register(r'skills', views.SkillView)
router.register(r'comments', views.CommentView)
# router.register(r'groups', views.GroupViewSet)

# Rename views to avoid conflict with app views
from rest_framework.authtoken import views as rest_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # Include default login and logout views for use with the browsable API. 
    # Optional, but useful if your API requires authentication and you want to use the browsable API.
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # API to generate auth token from user. Note that the URL part of the pattern can be whatever you want to use.
    # path('api-token-auth/', rest_views.obtain_auth_token, name='api-token-auth'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('events/', EventsView.as_view()),
    # path('cities/', CityView.as_view()),
    # path('users/', UserView.as_view()),
    # path('profiles/', ProfileView.as_view()),
    # path('comments/', CommentView.as_view()),
    # path('skills/', SkillView.as_view()),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
