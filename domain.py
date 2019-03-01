from .models import User, Situation, Response, Thought
from datetime import datetime

class Statistics:
    '''Domain layer that contains basic statistical analysis functions.'''
    negative_thought_freq_dict = {} # frequencies of negative thoughts
    negative_thought_emotion_dict = {} # most common emotional response to each negative thought
    negative_thought_response_dict = {} # most common response to each negative thought
    thought_challenge_dict = {} # most effective challenge to each negative thought
    thought_challenge_eff_dict = {} # tuple consisting of the challenge to the efficacy of the challenge to each negative thought

    def compute_for_user(self, user):
        # compute thought frequencies from creation dates of each situation that involves each thought
        negative_thought_freq_dict = {thought: self.thought_freq(thought, user) for thought in Thought.objects.filter(user=user, is_nat=True)}

    def thought_freq(self, thought, user):
        '''Compute user's frequency of a thought from addition dates of situations it occurs in.'''
        earliest_add_date = Situation.objects.filter(user=user).order_by('+add_date')[0].add_date
        latest_add_date = Situation.objects.filter(user=user).order_by('-add_date')[0].add_date
        return Situation.objects.count() / (latest_add_date - earliest_add_date).total_seconds()