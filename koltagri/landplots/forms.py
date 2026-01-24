# forms.py
from django import forms
from .models import CultivationPlant, Cultivation,HarvestCultivationPlant
from django.utils.translation import gettext_lazy as _
class CultivationPlantForm(forms.ModelForm):
    class Meta:
        model = CultivationPlant
        fields = ["cultivation", "plant_species", "count"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Opcional: textos de placeholder
        self.fields["count"].widget.attrs.update({
            "placeholder": "Ex: 120",
            "min": 1
        })

class CultivationForm(forms.ModelForm):
    class Meta:
        model = Cultivation
        fields = ["name", "description"]

class HarvestCultivationPlantForm(forms.ModelForm):
    class Meta:
        model = HarvestCultivationPlant
        fields = ['harvest_date', 'quantity', 'unity']
        