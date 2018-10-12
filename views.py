from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Situation
from django.utils import timezone

from .forms import SituationForm

class ProfileView(LoginRequiredMixin, ListView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/profile.html'
    context_object_name = 'latest_situations_list'

    def get_queryset(self):
        return Situation.objects.filter(add_date__lte=timezone.now()).order_by('-add_date')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class SituationView(LoginRequiredMixin, DetailView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/detail.html'

    model = Situation

    def get_queryset(self):
        return Situation.objects.filter(add_date__lte=timezone.now())

class EditSituationView(LoginRequiredMixin, FormView):
    login_url = '/nattracker/users/login/'

    template_name = 'nettracker/edit_situation.html'
    form_class = SituationForm

    def form_valid(self, form):

