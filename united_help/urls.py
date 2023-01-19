
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from united_help import views, settings

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from united_help.views import ActivateProfileView, EventSubscribeView, EventUnsubscribeView, EventsSubscribedView, \
    MeUserView, MeProfilesView, FinishEventView, CancelEventView, ActivateEventView, EventsCreatedView, \
    EventsAttendedView, EventsFinishedView, CommentsEventView, UserCommentsEventView, ContactsView, \
    UserAddFirebaseTokenView, UserProfileView, ProfileSubscribeView, ProfileUnsubscribeView

router = routers.SimpleRouter()
router.register(r'users', views.UserView)
router.register(r'profiles', views.ProfileView)
router.register(r'events', views.EventsView, basename='events')
router.register(r'cities', views.CityView)
router.register(r'skills', views.SkillView)
router.register(r'comments', views.CommentView)

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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('activate-profile/', ActivateProfileView.as_view()),

    path('events/subscribed/', EventsSubscribedView.as_view()),
    path('events/attended/', EventsAttendedView.as_view()),
    path('events/created/', EventsCreatedView.as_view()),
    path('events/finished/', EventsFinishedView.as_view()),
    path('events/<int:pk>/subscribe/', EventSubscribeView.as_view()),
    path('events/<int:pk>/unsubscribe/', EventUnsubscribeView.as_view()),
    path('events/<int:pk>/cancel/', CancelEventView.as_view()),
    path('events/<int:pk>/activate/', ActivateEventView.as_view()),
    path('events/<int:pk>/finish/', FinishEventView.as_view()),
    path('events/<int:pk>/comments/', CommentsEventView.as_view()),
    path('events/<int:pk>/usercomments/', UserCommentsEventView.as_view()),

    path('users/me/', MeUserView.as_view()),
    path('users/me/add_fb_token/', UserAddFirebaseTokenView.as_view()),

    path('profiles/me/', MeProfilesView.as_view()),
    path('profiles/contacts/', ContactsView.as_view()),
    path('userprofile/<int:pk>/', UserProfileView.as_view()),

    path('profiles/<int:pk>/subscribe/', ProfileSubscribeView.as_view()),
    path('profiles/<int:pk>/unsubscribe/', ProfileUnsubscribeView.as_view()),

    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('', include(router.urls)),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
