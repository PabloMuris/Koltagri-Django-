from django.contrib import admin
from koltagri.tasks.models import Task

# Register your models here.

@admin.register(Task)
class TasksAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "start_in", "end_in")
    filter_horizontal = ("cultivation_plant",) 