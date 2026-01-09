import django_filters
from django.utils import timezone
from django.db.models import Q, OuterRef, Subquery, Exists
from .models import Task, TaskCompletion
from django.db import models

class TaskFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", 
        lookup_expr="icontains",
        label="Nome da tarefa"
    )
    
    due_date = django_filters.DateFilter(
        field_name="due_date",
        lookup_expr="exact",
        label="Data exata"
    )

    due_date__gte = django_filters.DateFilter(
        field_name="due_date",
        lookup_expr="gte",
        label="Data inicial"
    )
    
    due_date__lte = django_filters.DateFilter(
        field_name="due_date",
        lookup_expr="lte",
        label="Data final"
    )

    # Filtro para status de atraso
    status = django_filters.ChoiceFilter(
        method='filter_by_status',
        label="Status",
        choices=[
            ('', 'Todas as tarefas'),
            ('overdue', 'Apenas atrasadas'),
            ('not_overdue', 'Apenas não atrasadas'),
        ]
    )

    class Meta:
        model = Task
        fields = ['name', 'status', 'due_date', 'due_date__gte', 'due_date__lte']

    def filter_by_status(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'overdue':
            # Tarefas atrasadas: data de vencimento passada E não concluídas
            # OU concluídas após a data de vencimento
            return queryset.filter(
                Q(due_date__lt=today) & (
                    Q(is_completed=False) |
                    Q(completions__is_completed=False) |
                    Q(completions__completed_at__gt=models.F('due_date'))
                )
            ).distinct()
            
        elif value == 'not_overdue':
            # Tarefas não atrasadas: data de vencimento no futuro
            # OU concluídas antes/na data de vencimento
            return queryset.filter(
                Q(due_date__gte=today) |
                Q(is_completed=True, due_date__gte=today) |
                Q(completions__is_completed=True, completions__completed_at__lte=models.F('due_date'))
            ).distinct()
            
        return queryset