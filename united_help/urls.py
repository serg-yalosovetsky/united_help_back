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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from united_help import views, settings

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from united_help.views import ActivateProfileView, EventSubscribeView, EventUnsubscribeView, EventsSubscribedView

router = routers.SimpleRouter()
router.register(r'users', views.UserView)
router.register(r'profiles', views.ProfileView)
router.register(r'events', views.EventsView, basename='events')
router.register(r'cities', views.CityView)
router.register(r'skills', views.SkillView)
router.register(r'comments', views.CommentView)
# router.register(r'groups', views.GroupViewSet)
# events_list = views.EventsView.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# event_detail = views.EventsView.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })

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
    re_path(r'^auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('api-auth/', include('rest_framework.urls')),
    # path('events/', views.EventsView.as_view({'get': 'list', })),
    # path('events/', events_list, name='snippet-list'),
    # path('events/<int:pk>/', event_detail, name='snippet-detail'),
    path('', include(router.urls)),
    # re_path('^events/(?P<enabled>.+)/$', views.EventsView.as_view({'get': 'list'})),

    # Include default login and logout views for use with the browsable API. 
    # Optional, but useful if your API requires authentication and you want to use the browsable API.
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # API to generate auth token from user. Note that the URL part of the pattern can be whatever you want to use.
    # path('api-token-auth/', rest_views.obtain_auth_token, name='api-token-auth'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('activate-profile/', ActivateProfileView.as_view()),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('events/<int:pk>/subscribe', EventSubscribeView.as_view()),
    path('events/subscribed', EventsSubscribedView.as_view()),
    path('events/<int:pk>/unsubscribe', EventUnsubscribeView.as_view()),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
