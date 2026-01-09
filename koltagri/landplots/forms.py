# forms.py
from django import forms
from .models import CultivationPlant

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
