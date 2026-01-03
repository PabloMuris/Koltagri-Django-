from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from koltagri.core.models import BaseModelWithSoftDelete
# Create your models here.


class ExpensesCategory(BaseModelWithSoftDelete):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Expense(BaseModelWithSoftDelete):
    
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

class IncomeCategory(BaseModelWithSoftDelete):
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
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=30, choices=UNIT_CHOICES)
    purchase_date = models.DateField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.ImageField(upload_to='agricultural_inputs/products/images', null=True, blank=True)

    def __str__(self):
        return self.name