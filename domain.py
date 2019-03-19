from .models import User, Situation, Response, Thought
from datetime import datetime

class Statistics:
    '''Domain layer that contains basic statistical analysis functions.'''
    negative_thought_freq_dict = {} # frequencies of negative thoughts
    thought_challenge_dict = {} # most effective challenge to each negative thought
    thought_challenge_eff_dict = {} # dictionary of challenges to each negative thought and their efficacies

    def compute_for_user(self, user):
        # compute thought frequencies from creation dates of each situation that involves each thought
        self.negative_thought_freq_dict = {thought:self.thought_freq(thought, user) for thought in Thought.objects.filter(user=user, is_nat=True)}
        self.thought_challenge_eff_dict = {thought:self.thought_challenge_eff(thought, user) for thought in Thought.objects.filter(user=user, is_nat=True)}
        self.thought_challenge_dict = {thought:max(self.thought_challenge_eff_dict[thought].keys(), key=lambda k: self.thought_challenge_eff_dict[thought][k]) for thought in self.thought_challenge_eff_dict if len(self.thought_challenge_eff_dict[thought]) > 0}

    def thought_freq(self, thought, user):
        '''Compute user's frequency of a thought from addition dates of situations it occurs in.'''
        situations = Situation.objects.filter(user=user)
        if situations:
        	earliest_add_date = Situation.objects.filter(user=user).order_by('add_date')[0].add_date
        	latest_add_date = Situation.objects.filter(user=user).order_by('-add_date')[0].add_date
        	duration = (latest_add_date - earliest_add_date).total_seconds()
        	if duration != 0:
        		return (thought.response.unhelpful_in_situations.count() + thought.response.helpful_in_situations.count()) / duration
        	else:
        		return float('NaN')
        else:
        	return 0

    def thought_challenge_eff(self, thought, user):
        '''Estimate the efficacy of challenges to a given unhelpful thought'''
        response = thought.response
        return_dict = {}
        for situation in response.unhelpful_in_situations.all():
            if (situation.helpful_response):
                challenge_response_thought_count = situation.helpful_response.thought_set.count()
                for thought in situation.helpful_response.thought_set.all():
                    total_situation_count = situation.helpful_response.unhelpful_in_situations.count() + situation.helpful_response.helpful_in_situations.count()
                    helpful_situation_count = situation.helpful_response.helpful_in_situations.count()
                    return_dict[thought] = helpful_situation_count / (total_situation_count * challenge_response_thought_count)

        return return_dict
