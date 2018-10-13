from abc import ABC, abstractmethod

from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Situation
from django.utils import timezone
from django.urls import reverse

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

class SituationFormView(ABC, LoginRequiredMixin, FormView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/edit_situation.html'
    form_class = SituationForm

    @abstractmethod
    def form_valid(self, form):
        return super().form_valid(form)

class AddSituationView(SituationFormView):
    action_situation = 'add'
    success_url = '/nattracker/users/profile/'

    def form_valid(self, form):
        form.addNewSituation(self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('add_situation')
        return context



class EditSituationView(SituationFormView):
    action_situation = 'edit'
    success_url = '/nattracker/users/profile/'

    def form_valid(self, form):
        form.editSituation(super(SituationFormView, self).get_situation())
        return super().form_valid(form)

    def get_situation(self):
        return Situation.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['situation'] = self.get_situation()
        context['action_url'] = reverse('edit_situation', args=[self.get_situation().pk])
        return context

