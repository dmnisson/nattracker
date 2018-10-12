from django.contrib import admin

from .models import Situation, Response, Thought, Emotion, Behavior

class SituationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'situation_text']}),
        ('Date information', {'fields': ['add_date']}),
        ('Responses', {'fields': ['unhelpful_response', 'helpful_response']}),
        ]

class ThoughtInline(admin.StackedInline):
    model = Thought
    extra = 1

class EmotionInline(admin.StackedInline):
    model = Response.emotions.through
    extra = 1

class BehaviorInline(admin.StackedInline):
    model = Response.behaviors.through
    extra = 1

class ResponseAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['response_name']}),]
    inlines = [ ThoughtInline, EmotionInline, BehaviorInline, ]
    exclude = ('emotions', 'behaviors',)

admin.site.register(Response, ResponseAdmin)
admin.site.register(Situation, SituationAdmin)
admin.site.register(Emotion)
admin.site.register(Behavior)