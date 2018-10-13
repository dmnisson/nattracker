from django.urls import include, path

from django.views.generic.base import TemplateView

from .views import ProfileView, SituationView, AddSituationView, EditSituationView

urlpatterns = [
    path('', TemplateView.as_view(template_name='nattracker/index.html'), name='index'),
    path('users/', include('django.contrib.auth.urls')),
    path('users/profile/', ProfileView.as_view(), name='profile'),
    path('users/situation/<int:pk>', SituationView.as_view(), name='detail'),
    path('users/situation/add', AddSituationView.as_view(), name='add_situation'),
    path('users/situation/edit/<int:pk>', EditSituationView.as_view(), name='edit_situation')
]