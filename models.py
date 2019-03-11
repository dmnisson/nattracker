from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Make sure to add to settings.py:
#      AUTH_USER_MODEL = 'nattracker.User'
class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    allowed_subjects = models.ManyToManyField("self", blank=True)
    groups = models.ManyToManyField(Group, related_name="nattracker_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="nattracker_permissions")

class Emotion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emotion_name = models.CharField(max_length=50)

    def __str__(self):
        return self.emotion_name

class Behavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    situation_text = models.CharField(max_length=255)
    add_date = models.DateTimeField('date added')
    unhelpful_response = models.ForeignKey(Response, on_delete=models.SET_NULL, related_name='unhelpful_in_situations', null=True)
    helpful_response = models.ForeignKey(Response, on_delete=models.SET_NULL, related_name='helpful_in_situations', null=True)

    def __str__(self):
        return self.situation_text

class Thought(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    thought_text = models.CharField(max_length=256000)
    is_nat = models.BooleanField(default=False)

    def __str__(self):
        return self.thought_text

