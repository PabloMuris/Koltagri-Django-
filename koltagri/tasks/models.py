from django.db import models
from koltagri.landplots.models import CultivationPlant,PlantSpecies
from koltagri.core.models import BaseModelWithSoftDelete
from django.core.exceptions import ValidationError
# Create your models here.

class Task(BaseModelWithSoftDelete):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cultivation_plant= models.ManyToManyField(CultivationPlant, verbose_name=("cultivo da planta"))
    start_in = models.DateTimeField()
    end_in = models.DateTimeField()


    def clean(self):
        super().clean()
        if self.end_in < self.start_in:
            raise ValidationError({
                'end_in': 'The end date can\'t be earlier than start date'
            })
