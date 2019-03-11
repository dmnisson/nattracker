from django import forms

from .models import Situation, Response, Thought, Emotion, Behavior

import datetime

class SituationForm(forms.Form):
    situation_desc = forms.CharField(label='Situation', max_length=255)
    unhelpful_response = forms.ModelChoiceField(label='Unhelpful Response', queryset=Response.objects.all())
    helpful_response = forms.ModelChoiceField(label='Helpful Response', queryset=Response.objects.all())

    def addNewSituation(self, user):
        situation = Situation(user=user,
            add_date=datetime.datetime.now(),
            situation_text=self.cleaned_data['situation_desc'],
            unhelpful_response=self.cleaned_data['unhelpful_response'],
            helpful_response=self.cleaned_data['helpful_response'])
        situation.save()

    def editSituation(self, situation):
        situation.situation_text = self.cleaned_data['situation_desc']
        situation.unhelpful_response = self.cleaned_data['unhelpful_response']
        situation.helpful_response = self.cleaned_data['helpful_response']
        situation.save()

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['response_name', 'emotions', 'behaviors']

    response_name = forms.CharField(label='Response Name', max_length=50)
    emotions = forms.ModelMultipleChoiceField(label='Emotions', queryset=Emotion.objects.all())
    behaviors = forms.ModelMultipleChoiceField(label='Behaviors', queryset=Behavior.objects.all())

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['emotions'].queryset = Emotion.objects.filter(user=user)
        self.fields['behaviors'].queryset = Behavior.objects.filter(user=user)

        thoughts = Thought.objects.filter(response=self.instance)
        for i in range(len(thoughts) + 1):
            text_field_name = 'thought_text_%s' % (i,)
            check_field_name = 'thought_is_nat_%s' % (i,)
            self.fields[text_field_name] = forms.CharField(widget=forms.Textarea, label='Thought Description', max_length=256000, required=(i == 0))
            self.fields[check_field_name] = forms.BooleanField(label='Is Negative Automatic Thought', required=False)
            try:
                self.initial[text_field_name] = thoughts[i].thought_text
                self.initial[check_field_name] = thoughts[i].is_nat
            except IndexError:
                self.initial[text_field_name] = ""
                self.initial[check_field_name] = False
        # extra blank fields
        text_field_name = 'thought_text_%s' % (i + 1,)
        check_field_name = 'thought_is_nat_%s' % (i + 1,)
        self.fields[text_field_name] = forms.CharField(widget=forms.Textarea, label='Thought Description', max_length=256000, required=False)
        self.fields[check_field_name] = forms.BooleanField(label='Is Negative Automatic Thought', required=False)
        self.initial[text_field_name] = ""
        self.initial[check_field_name] = False

    def get_thought_text_and_check_fields(self):
        for field_name in self.fields:
            if field_name.startswith('thought_text_'):
                yield (self[field_name], self['thought_is_nat_' + field_name[13:]])

    def addNewResponse(self, user):
        response = Response.objects.create(user=user,
            response_name=self.cleaned_data['response_name'])
        response.emotions.add(*(self.cleaned_data['emotions']))
        response.behaviors.add(*(self.cleaned_data['behaviors']))
        self.saveResponseWithThoughts(response, user)

    def editResponse(self, response):
        response.response_name = self.cleaned_data['response_name'],
        response.emotions.all().delete()
        response.emotions.add(*(self.cleaned_data['emotions']))
        response.behaviors.all().delete()
        response.behaviors.add(*(self.cleaned_data['behaviors']))
        self.saveResponseWithThoughts(response, response.user)

    def clean(self):
        # interpret multiple thoughts correctly
        thoughts = []
        thought_nat_checks = []
        i = 0
        text_field_name = 'thought_text_%s' % (i,)
        check_field_name = 'thought_is_nat_%s' % (i,)
        while self.cleaned_data.get(text_field_name):
            thought_text = self.cleaned_data[text_field_name]
            thought_is_nat = self.cleaned_data[check_field_name]
            if not thought_text.isspace():
                thoughts.append(thought_text)
                thought_nat_checks.append(thought_is_nat)

            i += 1
            text_field_name = 'thought_text_%s' % (i,)
            check_field_name = 'thought_is_nat_%s' % (i,)
        self.cleaned_data['thoughts'] = thoughts
        self.cleaned_data['thought_nat_checks'] = thought_nat_checks

    def saveResponseWithThoughts(self, response, user):
        response.thought_set.all().delete()
        thought_texts = list(self.cleaned_data['thoughts'])
        thought_checks = list(self.cleaned_data['thought_nat_checks'])
        for i in range(len(thought_texts)):
            Thought.objects.create(user=user, response=response,
                thought_text=thought_texts[i],
                is_nat=thought_checks[i])
        response.save()

