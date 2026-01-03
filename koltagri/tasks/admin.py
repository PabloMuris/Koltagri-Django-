from django.contrib import admin
from koltagri.tasks.models import Task,TaskCompletion,Attachment

# Register your models here.

@admin.register(Task)
class TasksAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "start_in", "due_date", "priority")
    filter_horizontal = ("cultivation_plant",)

@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "user", "completed_at", "is_completed")

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "file", "type","user")