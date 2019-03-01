from abc import ABC, abstractmethod

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Situation
from django.utils import timezone
from django.urls import reverse

from .forms import SituationForm

from .domain import Statistics

class ProfileView(LoginRequiredMixin, ListView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/profile.html'
    context_object_name = 'latest_situations_list'

    def get_queryset(self):
        #return Situation.objects.filter(user=self.request.user).filter(add_date__lte=timezone.now()).order_by('-add_date')[:5]
        return Situation.objects.order_by('-add_date')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class ObjectOwnerMixin(object):
    def get_object(self, queryset=None):
        '''Deny permission if user does not own the object.'''
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_arg, None)
        queryset = queryset.filter(pk=pk, user=self.request.user)

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise PermissionDenied

        return obj

class SituationView(LoginRequiredMixin, ObjectOwnerMixin, DetailView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/detail.html'

    model = Situation


class SituationFormView(ABC, LoginRequiredMixin, ObjectOwnerMixin, FormView):
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

class StatisticsView(LoginRequiredMixin, TemplateView):
    login_url = '/nattracker/users/login'

    template_name = 'nattracker/statistics.html'

    statistics = Statistics()

    def get_context_data(self, **kwargs):
        self.statistics.compute_for_user(self.request.user)
        context = super().get_context_data(**kwargs)
        context['most_frequent_negative_thoughts_list'] = map(lambda kv: kv[0], sorted(self.statistics.negative_thought_freq_dict.items(), key=lambda kv: kv[1], reverse=True))
        context['thought_freq_dict'] = self.statistics.negative_thought_freq_dict
        context['thought_emotion_dict'] = self.statistics.negative_thought_emotion_dict
        context['thought_response_dict'] = self.statistics.negative_thought_response_dict
        context['most_effective_positive_challenges_list'] = map(lambda kv: self.statistics.challenged_thought(kv[0]), sorted(self.statistics.thought_challenge_eff_dict.items(), key=lambda kv: kv[1], reverse=True))
        context['thought_challenge_dict'] = self.statistics.thought_challenge_dict
        context['thought_challenge_eff_dict'] = self.statistics.thought_challenge_eff_dict

        return context





