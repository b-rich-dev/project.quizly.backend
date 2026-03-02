from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """
    Inline admin interface for editing questions within a quiz.
    Allows adding, editing, and removing questions directly from the quiz edit page.
    """
    
    model = Question
    extra = 1
    fields = ['question_title', 'question_options', 'answer']
    

class QuizAdmin(admin.ModelAdmin):
    """
    Admin interface for Quiz model.
    Provides list display, search, filtering, and inline question editing capabilities.
    """
    
    list_display = ['title', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]
    fieldsets = (
        ('Quiz Information', {
            'fields': ('user', 'title', 'description', 'video_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class QuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for Question model.
    Provides list display, search, filtering for individual question management.
    """
    
    list_display = ['question_title', 'quiz', 'answer', 'created_at']
    list_filter = ['created_at', 'quiz']
    search_fields = ['question_title', 'answer', 'quiz__title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Question Information', {
            'fields': ('quiz', 'question_title', 'question_options', 'answer')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
