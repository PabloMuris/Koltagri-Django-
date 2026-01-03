import django_filters
from .models import Expense



class ExpenseFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="date",
        label="Data"
    )

    class Meta:
        model = Expense
        fields = ["date"]