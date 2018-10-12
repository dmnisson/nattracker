from django import forms

from .models import Situation
from .models import Response

class SituationForm(forms.Form):
    situation_desc = forms.CharField(label='Situation', max_length=255)
    unhelpful_response = forms.ModelChoiceField(label='Responses', queryset=Response.objects.all())
    helpful_response = forms.ModelChoiceField(label='Behaviors', queryset=Response.objects.all())

    def addNewSituation(self, user):
        situation = Situation(user=user,
            situation_text=self.cleaned_data['situation_desc'],
            unhelpful_response=self.cleaned_data['unhelpful_response'],
            helpful_response=self.cleaned_data['helpful_response'])
        situation.save()

    def editSituation(self, situation):
        situation.situation_text = self.cleaned_data['situation_desc']
        situation.unhelpful_response = self.cleaned_data['unhelpful_response']
        situation.helpful_response = self.cleaned_data['helpful_response']
        situation.save()