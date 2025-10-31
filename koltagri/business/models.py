from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class ExpensesCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Expense(models.Model):
    category = models.ForeignKey(
        ExpensesCategory,
        on_delete=models.CASCADE,
        related_name="expenses"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)

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
    


class Questionnaire(models.Model):
    QUESTIONNAIRE_TYPES = [
        ("INSUMOS", "Insumos"),
        ("FIXOS", "Gastos Fixos"),
        ("VENDAS", "Vendas"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questionnaires")
    type = models.CharField(max_length=20, choices=QUESTIONNAIRE_TYPES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True  