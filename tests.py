from django.test import TestCase
from django.utils import timezone
import datetime
from django.urls import reverse

from .models import User, Situation, Response, Thought, Behavior, Emotion

from .domain import Statistics

import math

def create_situation(user_id, situation_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Situation.objects.create(user_id=user_id, situation_text=situation_text, add_date=time)

def create_response(user_id, response_name, nat_thought_strs, pt_thought_strs, emotion_strs, behavior_strs):
    emotions = map(lambda str: Emotion.objects.create(user_id=user_id, emotion_name=str), emotion_strs)
    behaviors = map(lambda str: Behavior.objects.create(user_id=user_id, behavior_text=str), behavior_strs)
    response = Response.objects.create(user_id=user_id, response_name=response_name)
    response.emotions.add(*emotions)
    response.behaviors.add(*behaviors)

    for tstr in nat_thought_strs:
        Thought.objects.create(user_id=user_id, response=response, thought_text=tstr, is_nat=True)

    for tstr in pt_thought_strs:
        Thought.objects.create(user_id=user_id, response=response, thought_text=tstr, is_nat=False)

    response.save()
    return response

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tmpuser', 'tmpuser@example.com', 'tmppass')

    def tmpLogIn(self):
        print(self.client.login(username='tmpuser', password='tmppass'))

    def test_no_situations(self):
        self.tmpLogIn()
        response = self.client.get(reverse('profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No situations have been added.")
        self.assertQuerysetEqual(response.context['latest_situations_list'], [])

    def test_past_situation(self):
        create_situation(self.user.id, "Past situation.", -1)

        self.tmpLogIn()
        response = self.client.get(reverse('profile'), follow=True)
        self.assertQuerysetEqual(response.context['latest_situations_list'], ['<Situation: Past situation.>'])

    def test_future_situation(self):
        create_situation(self.user.id, "Future situation.", 1)

        self.tmpLogIn()
        response = self.client.get(reverse('profile'), follow=True)
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
        response = self.client.get(reverse('detail', args=(past_situation.id,)), follow=True)
        self.assertContains(response, past_situation.situation_text)

    def test_future_situation(self):
        future_situation = create_situation(self.user.id, "Future situation.", 1)
        self.tmpLogIn()
        response = self.client.get(reverse('detail', args=(future_situation.id,)), follow=True)
        self.assertContains(response, future_situation.situation_text)

class StatisticsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tmpuser', 'tmpuser@example.com', 'tmppass')

    def tmpLogIn(self):
        print(self.client.login(username='tmpuser', password='tmppass'))

    def test_no_thoughts(self):
        statistics = Statistics()
        self.tmpLogIn()
        statistics.compute_for_user(self.user)
        self.assertEqual(len(statistics.negative_thought_freq_dict), 0)
        self.assertEqual(len(statistics.thought_challenge_dict), 0)
        self.assertEqual(len(statistics.thought_challenge_eff_dict), 0)

    def test_single_past_situation_no_helpful_responses(self):
        situation = create_situation(self.user.id, "Situation", -1)
        situation.unhelpful_response = create_response(self.user.id, "Unhelpful Response", ["NAT1", "NAT2", "NAT3"], [], ["angry", "scared"], ["ran", "screamed"])
        self.tmpLogIn()
        statistics = Statistics()
        statistics.compute_for_user(self.user)
        self.assertEqual(len(statistics.negative_thought_freq_dict), 3)
        self.assertEqual(len(statistics.thought_challenge_dict), 0)
        self.assertEqual(len(statistics.thought_challenge_eff_dict), 3)
        for thought, freq in statistics.negative_thought_freq_dict.items():
            self.assertTrue(math.isnan(freq))

    def test_single_past_situation_some_helpful_responses(self):
        situation = create_situation(self.user.id, "Situation", -1)
        situation.unhelpful_response = create_response(self.user.id, "Unhelpful Response", ["NAT1", "NAT2", "NAT3"], [], ["angry", "scared"], ["ran", "screamed"])
        situation.helpful_response = create_response(self.user.id, "Helpful Response", [], ["PC1", "PC2", "PC3"], ["happy", "calm"], ["sat down", "breathed"])
        situation.save()
        self.tmpLogIn()
        statistics = Statistics()
        statistics.compute_for_user(self.user)
        self.assertEqual(len(statistics.negative_thought_freq_dict), 3)
        self.assertEqual(len(statistics.thought_challenge_dict), 3)
        self.assertEqual(len(statistics.thought_challenge_eff_dict), 3)
        for thought, freq in statistics.negative_thought_freq_dict.items():
            self.assertTrue(math.isnan(freq))

        for thought, eff_dict in statistics.thought_challenge_eff_dict.items():
            for challenge, eff in eff_dict.items():
                self.assertAlmostEqual(eff, 1/3, places=5)

    def test_multiple_past_situations_some_helpful_responses(self):
        situation1 = create_situation(self.user.id, "Situation 1", -1)
        situation1.unhelpful_response = create_response(self.user.id, "Unhelpful Response 1", ["NAT11", "NAT12", "NAT13"], [], ["angry", "scared"], ["ran", "screamed"])
        situation1.helpful_response = create_response(self.user.id, "Helpful Response 1", [], ["PC11", "PC12", "PC13"], ["happy", "calm"], ["sat down", "breathed"])
        situation1.save()
        situation2 = create_situation(self.user.id, "Situation 2", -2)
        situation2.unhelpful_response = create_response(self.user.id, "Unhelpful Response 2", ["NAT21", "NAT22", "NAT23"], [], ["angry", "scared"], ["ran", "screamed"])
        situation2.save()
        situation3 = create_situation(self.user.id, "Situation 3", -4)
        situation3.unhelpful_response = situation1.unhelpful_response
        situation3.helpful_response = create_response(self.user.id, "Helpful Response 2", [], ["PC31", "PC32", "PC33"], ["calm"], ["lay down", "relaxed"])
        situation3.save()
        self.tmpLogIn()
        statistics = Statistics()
        statistics.compute_for_user(self.user)
        self.assertEqual(len(statistics.negative_thought_freq_dict), 6)
        self.assertEqual(len(statistics.thought_challenge_dict), 3)
        self.assertEqual(len(statistics.thought_challenge_eff_dict), 6)
        for thought, freq in statistics.negative_thought_freq_dict.items():
            if (thought.thought_text[:4] == "NAT1"):
                self.assertAlmostEqual(freq, 2/259200, places=5)
            elif (thought.thought_text[:4] == "NAT2"):
                self.assertAlmostEqual(freq, 1/259200, places=5)
            else:
                self.assertTrue(thought.thought_text[:3] == "NAT")

        for thought, eff_dict in statistics.thought_challenge_eff_dict.items():
            for challenge, eff in eff_dict.items():
                self.assertAlmostEqual(eff, 1/3, places=5)
