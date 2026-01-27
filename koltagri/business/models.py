from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from koltagri.core.models import BaseModelWithSoftDelete
# Create your models here.


class ExpensesCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Expense(models.Model):
    site = models.ForeignKey(
        'landplots.site',
        on_delete=models.CASCADE,
        related_name='expenses',
        null=True
    )
    
    category = models.ForeignKey(
        ExpensesCategory,
        on_delete=models.CASCADE,
        related_name="expenses"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    

    def __str__(self):
        return f"{self.category.name} - {self.amount} on {self.date}"
    
class IncomeCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Income(models.Model):
    category = models.ForeignKey(
        IncomeCategory,
        on_delete=models.CASCADE,
        related_name="incomes"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount} on {self.date}"
    



class AgriculturalInputs(BaseModelWithSoftDelete):
    UNIT_CHOICES = [
            ("kg", "Kilogram"),
            ("g", "Gram"),
            ("l", "Liter"),
            ("ml", "Milliliter"),
            ("pcs", "Pieces"),
            
        ]

    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    unit = models.CharField(max_length=30, choices=UNIT_CHOICES)
    
    image = models.ImageField(upload_to='agricultural_inputs/', null=True, blank=True)
    
    site = models.ForeignKey(
        "landplots.site",
        on_delete=models.CASCADE,
        related_name="supplies",
        null=True

    )
    def __str__(self):
        return self.name
    

# models.py (trechos relevantes)

class AgriculturalInputPack(BaseModelWithSoftDelete):
    agricultural_input = models.ForeignKey(
        AgriculturalInputs,
        on_delete=models.CASCADE,
        related_name="packs"
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    name = models.CharField(max_length=255, editable=False)

    def save(self, *args, **kwargs):
        # mantém sua escolha original de só gerar se name vazio,
        # mas você pode trocar para sempre gerar (ver nota abaixo)
        if not self.name:
            self.name = self.generate_name()
        super().save(*args, **kwargs)

    def generate_name(self):
        # usa a unidade do agricultural_input (corrigido)
        unit = self.agricultural_input.get_unit_display()
        return f"{self.agricultural_input.name} - {self.quantity} {unit}"

    def total_used(self):
        from django.db.models import Sum
        total = self.usages.aggregate(total=Sum("quantity_used"))["total"]
        return total or 0

    def remaining_quantity(self):
        return (self.quantity or 0) - self.total_used()

    def is_depleted(self):
        return self.remaining_quantity() <= 0

    def __str__(self):
        return self.name



class AgriculturalInputUsage(BaseModelWithSoftDelete):
    pack = models.ForeignKey(
        AgriculturalInputPack,
        on_delete=models.PROTECT,
        related_name="usages",
        verbose_name=_("Pacote")
    )

    cultivation_plant = models.ForeignKey(
        "landplots.CultivationPlant",
        on_delete=models.CASCADE,
        related_name="input_usages",
        verbose_name=_("Cultivo de Planta")
    )

    quantity_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Quantidade usada do pacote"),
        verbose_name=_("Quantidade Usada")
    )

    usage_date = models.DateField(default=timezone.now, verbose_name=_("Data de Uso"))

    class Meta:
        verbose_name = _("Uso de Insumo")
        verbose_name_plural = _("Usos de Insumo")

    def __str__(self):
        return (
            f"{self.quantity_used} "
            f"{self.pack.agricultural_input.unit} de "
            f"{self.pack.agricultural_input.name} "
            f"em {self.cultivation_plant}"
        )
    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)