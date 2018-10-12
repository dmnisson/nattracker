from django.db import models
from django.contrib.auth.models import User

class Emotion(models.Model):
    emotion_name = models.CharField(max_length=50)

    def __str__(self):
        return self.emotion_name

class Behavior(models.Model):
    behavior_text = models.CharField(max_length=200)

    def __str__(self):
        return self.behavior_text

class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response_name = models.CharField(max_length=50)
    emotions = models.ManyToManyField(Emotion)
    behaviors = models.ManyToManyField(Behavior)

    def __str__(self):
        return self.response_name

class Situation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    situation_text = models.CharField(max_length=200)
    add_date = models.DateTimeField('date added')
    unhelpful_response = models.ForeignKey(Response, on_delete=models.SET_NULL, related_name='unhelpful_response', null=True)
    helpful_response = models.ForeignKey(Response, on_delete=models.SET_NULL, related_name='helpful_response', null=True)

    def __str__(self):
        return self.situation_text

class Thought(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    thought_text = models.CharField(max_length=200)

    def __str__(self):
        return self.thought_text

