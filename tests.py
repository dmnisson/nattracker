from django.test import TestCase
from django.utils import timezone
import datetime
from django.urls import reverse

from .models import Situation

from django.contrib.auth.models import User

def create_situation(user_id, situation_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Situation.objects.create(user_id=user_id, situation_text=situation_text, add_date=time)

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tmpuser', 'tmpuser@example.com', 'tmppass')

    def tmpLogIn(self):
        print(self.client.login(username='tmpuser', password='tmppass'))

    def test_no_situations(self):
        self.tmpLogIn()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No situations have been added.")
        self.assertQuerysetEqual(response.context['latest_situations_list'], [])

    def test_past_situation(self):
        create_situation(self.user.id, "Past situation.", -1)

        self.tmpLogIn()
        response = self.client.get(reverse('profile'))
        self.assertQuerysetEqual(response.context['latest_situations_list'], ['<Situation: Past situation.>'])

    def test_future_situation(self):
        create_situation(self.user.id, "Future situation.", 1)

        self.tmpLogIn()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No situations have been added.")
        self.assertQuerysetEqual(response.context['latest_situations_list'], [])


class SituationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tmpuser', 'tmpuser@example.com', 'tmppass')

    def tmpLogIn(self):
        print(self.client.login(username='tmpuser', password='tmppass'))

    def test_past_situation(self):
        past_situation = create_situation(self.user.id, "Past situation.", -1)
        self.tmpLogIn()
        response = self.client.get(reverse('detail', args=(past_situation.id,)))
        self.assertContains(response, past_situation.situation_text)

    def test_future_situation(self):
        future_situation = create_situation(self.user.id, "Future situation.", 1)
        self.tmpLogIn()
        response = self.client.get(reverse('detail', args=(future_situation.id,)))
        self.assertEqual(response.status_code, 404)