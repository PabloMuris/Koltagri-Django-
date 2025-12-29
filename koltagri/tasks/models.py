from django.db import models
from koltagri.landplots.models import CultivationPlant,PlantSpecies
from koltagri.core.models import BaseModelWithSoftDelete
from django.core.exceptions import ValidationError
from django.conf import settings
from koltagri.business.models import AgriculturalInputs



class Task(BaseModelWithSoftDelete):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cultivation_plant= models.ManyToManyField(CultivationPlant, verbose_name=("cultivo da planta"), blank=True)
    supplies = models.ManyToManyField(AgriculturalInputs, verbose_name=("insumos agrícolas"), blank=True)
    start_in = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    user = models.ManyToManyField("users.User", related_name='tasks')
    priority = models.IntegerField(default=0)


    def __str__(self):
        return self.name


class Attachment(models.Model):
    TASK = 'task'
    COMPLETION = 'completion'
    ATTACHMENT_TYPES = [
        (TASK, 'Anexo da Tarefa'),
        (COMPLETION, 'Anexo de Conclusão'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default=TASK)

    def __str__(self):
        return self.name
    
class TaskCompletion(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='completed_tasks')
    completed_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} → {self.task}"