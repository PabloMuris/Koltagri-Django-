# forms.py
from django import forms
from .models import CultivationPlant, Cultivation, HarvestCultivationPlant
from django.utils.translation import gettext_lazy as _

class CultivationPlantForm(forms.ModelForm):
    class Meta:
        model = CultivationPlant
        fields = ["cultivation", "plant_species", "count"]
        labels = {
            "cultivation": _("Cultivo"),
            "plant_species": _("Espécie de Planta"),
            "count": _("Quantidade"),
        }
        help_texts = {
            "count": _("Número de plantas"),
        }

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
        labels = {
            "name": _("Nome"),
            "description": _("Descrição"),
        }
        widgets = {
            "description": forms.Textarea(attrs={
                "placeholder": _("Descreva este cultivo..."),
                "rows": 4
            }),
        }

class HarvestCultivationPlantForm(forms.ModelForm):
    class Meta:
        model = HarvestCultivationPlant
        fields = ['harvest_date', 'quantity', 'unity']
        labels = {
            'harvest_date': _('Data da Colheita'),
            'quantity': _('Quantidade'),
            'unity': _('Unidade'),
        }
        widgets = {
            'harvest_date': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': _('DD/MM/AAAA')
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': _('Ex: 100'),
                'min': 0
            }),
        }
        