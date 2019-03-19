from abc import ABC, abstractmethod

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, UpdateView, DeleteView

from django.core.paginator import Paginator

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Situation, Response, Emotion, Behavior
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect

from django.http import HttpResponse, JsonResponse

import datetime

from .forms import SituationForm, ResponseForm

from .domain import Statistics

class ProfileView(LoginRequiredMixin, ListView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/profile.html'
    context_object_name = 'latest_situations_list'

    def get_queryset(self):
        return Situation.objects.filter(user=self.request.user).filter(add_date__lte=timezone.now()).order_by('-add_date')[:5]

    def get_context_data(self, **kwargs):
        responses = Response.objects.filter(user=self.request.user)
        latest_occur_dict = {}

        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        for response in responses:
            unhelpful_situation = response.unhelpful_in_situations.filter(add_date__lte=timezone.now()).order_by('-add_date').first()
            helpful_situation = response.helpful_in_situations.filter(add_date__lte=timezone.now()).order_by('-add_date').first()

            if (unhelpful_situation != None):
                latest_occur_dict[response] = unhelpful_situation.add_date

            if (helpful_situation != None and (unhelpful_situation == None or helpful_situation.add_date > unhelpful_situation.add_date)):
                latest_occur_dict[response] = helpful_situation.add_date
        latest_responses_list = list(responses)
        latest_responses_list.sort(key=lambda r: latest_occur_dict[r] if r in latest_occur_dict else datetime.datetime.utcfromtimestamp(0).replace(tzinfo=timezone.get_current_timezone()), reverse=True)

        context['latest_responses_list'] = latest_responses_list[:5]
        context['response_latest_occur_dict'] = latest_occur_dict
        return context

class ObjectOwnerMixin(object):
    def get_object(self, queryset=None):
        '''Deny permission if user does not own the object.'''
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get('pk', None);
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

class ResponseView(LoginRequiredMixin, ObjectOwnerMixin, DetailView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/response_details.html'

    model = Response


class SituationFormView(ABC, LoginRequiredMixin, ObjectOwnerMixin):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/edit_situation.html'
    form_class = SituationForm

class ResponseFormView(ABC, LoginRequiredMixin, ObjectOwnerMixin, TemplateView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/edit_response.html'

    def get(self, request, *args, **kwargs):
        form = self.create_form(request, kwargs.get('pk', None), None)
        success_path = kwargs.get('success_path', reverse('profile'))
        context_data = self.get_context_data(success_path=success_path)
        context_data['form'] = form
        return render(request, self.template_name, context_data)

    def post(self, request, *args, **kwargs):
        form = self.create_form(request, kwargs.get('pk', None), request.POST or None)
        success_path = kwargs.get('success_path', reverse('profile'))
        if (form.is_valid()):
            self.form_valid(form)
            return redirect('/' + success_path)

        context_data = self.get_context_data(success_path=success_path)
        context_data['form'] = form
        return render(request, self.template_name, context_data)

    @abstractmethod
    def form_valid(self, form):
        return form.is_valid()

    @abstractmethod
    def create_form(self, request, pk, data):
        return ResponseForm(request.user)

class AddSituationView(SituationFormView, FormView):
    action_situation = 'add'
    success_url = '/nattracker/users/profile/'

    def form_valid(self, form):
        form.addNewSituation(self.request.user)
        return super(FormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('add_situation')
        return context



class EditSituationView(SituationFormView, UpdateView):
    action_situation = 'edit'
    success_url = '/nattracker/users/profile/'
    model = Situation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('edit_situation', args=[self.object.pk])
        return context

class AddResponseView(ResponseFormView):
    action_response = 'add'

    def form_valid(self, form):
        form.addNewResponse(self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_url'] = reverse('add_response', args=[kwargs['success_path']])
        return context

    def create_form(self, request, pk, data):
        return ResponseForm(request.user, data=data)

class EditResponseView(ResponseFormView):
    action_response = 'edit'

    def form_valid(self, form):
        form.editResponse(self.get_response())
        return super().form_valid(form)

    def get_response(self):
        pk = self.kwargs['pk']
        return Response.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['response'] = self.get_response()
        context['action_url'] = reverse('edit_response', args=[self.get_response().pk, kwargs['success_path']])
        return context

    def create_form(self, request, pk, data):
        return ResponseForm(request.user, data=data, instance=Response.objects.get(pk=pk))

class DeleteResponseView(LoginRequiredMixin, ObjectOwnerMixin, DeleteView):
    login_url = '/nattracker/users/login'

    template_name = 'nattracker/delete_response.html'

    model = Response
    success_url = reverse_lazy('manage_responses')

class StatisticsView(LoginRequiredMixin, TemplateView):
    login_url = '/nattracker/users/login'

    template_name = 'nattracker/statistics.html'

    statistics = Statistics()

    def get_context_data(self, **kwargs):
        self.statistics.compute_for_user(self.request.user)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['most_frequent_negative_thoughts_list'] = list(map(lambda kv: kv[0], sorted(self.statistics.negative_thought_freq_dict.items(), key=lambda kv: kv[1], reverse=True)))
        # display frequencies per day
        context['thought_freq_dict'] = {thought:freq*86400 for thought, freq in self.statistics.negative_thought_freq_dict.items()}
        context['most_effective_positive_challenges_list'] = list(map(lambda kv: kv[0], sorted(self.statistics.thought_challenge_dict.items(), key=lambda kv: self.statistics.thought_challenge_eff_dict[kv[0]][kv[1]], reverse=True)))
        context['thought_challenge_dict'] = self.statistics.thought_challenge_dict
        # display efficacies as percentages
        context['thought_challenge_eff_dict'] = {thought:{challenge:eff*100 for challenge, eff in eff_dict.items()} for thought, eff_dict in self.statistics.thought_challenge_eff_dict.items()}

        return context

class ResponseManagerView(LoginRequiredMixin, TemplateView):
    login_url = '/nattracker/users/login/'

    template_name = 'nattracker/manage_responses.html'

    def get_context_data(self, **kwargs):
        response_list = Response.objects.filter(user=self.request.user)
        paginator = Paginator(response_list, 25)

        page = self.kwargs['page'] if ('page' in self.kwargs) else 1
        responses = paginator.get_page(page)

        # range of pages to show in the paginator
        view_page_range = [1, 2, 3]
        view_page_range = view_page_range + (list(range(4, page + 1)) if (page - 3 <= 4) else (["...",] + list(range(page - 6, page + 1))))
        view_page_range = view_page_range + (list(range(page + 1, paginator.num_pages + 1)) if (page + 7 >= paginator.num_pages) else (list(range(page + 1, page + 4)) + ["...",] + list(range(paginator.num_pages - 2, paginator.num_pages + 1))))

        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['responses'] = responses

        return context

# API views
class AddEmotionView(LoginRequiredMixin, View):
    login_url = '/nattracker/users/login'

    def post(self, request, *args, **kwargs):
        emotion = Emotion.objects.create(user=request.user, emotion_name=request.body.decode(encoding='utf-8'))
        return JsonResponse({'id': emotion.id}, status=201)

class AddBehaviorView(LoginRequiredMixin, View):
    login_url = '/nattracker/users/login'

    def post(self, request, *args, **kwargs):
        behavior = Behavior.objects.create(user=request.user, behavior_text=request.body.decode(encoding='utf-8'))
        return JsonResponse({'id': behavior.id}, status=201)
