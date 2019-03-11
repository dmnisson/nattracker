from django.urls import include, path

from django.views.generic.base import TemplateView

from .views import ProfileView, SituationView, AddSituationView, EditSituationView
from .views import AddResponseView, EditResponseView, StatisticsView
from .views import ResponseManagerView, AddEmotionView, AddBehaviorView

urlpatterns = [
    path('', TemplateView.as_view(template_name='nattracker/index.html'), name='index'),
    path('users/', include('django.contrib.auth.urls')),
    path('users/profile/', ProfileView.as_view(), name='profile'),
    path('users/situation/<int:pk>', SituationView.as_view(), name='detail'),
    path('users/situation/add', AddSituationView.as_view(), name='add_situation'),
    path('users/situation/edit/<int:pk>', EditSituationView.as_view(), name='edit_situation'),
    path('users/response/add', AddResponseView.as_view(), name='add_response'),
    path('users/response/edit/<int:pk>', EditResponseView.as_view(), name='edit_response'),
    path('users/statistics/', StatisticsView.as_view(), name='statistics'),
    path('users/manageresponses/', ResponseManagerView.as_view(), name='manage_responses'),
    path('users/manageresponses/<int:page>', ResponseManagerView.as_view(), name='manage_responses'),

    path('api/emotion/add', AddEmotionView.as_view(), name='add_emotion'),
    path('api/behavior/add', AddBehaviorView.as_view(), name='add_behavior'),
]
