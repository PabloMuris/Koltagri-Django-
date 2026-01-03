from django.shortcuts import render
from django.views.generic import TemplateView ,ListView,CreateView,UpdateView,DetailView,DeleteView,FormView
from django_filters.views import FilterView
from .models import Expense,ExpensesCategory,AgriculturalInputs
from .forms import ExpenseForm
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin


class BusinessDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'business.html'

class PlanningView(LoginRequiredMixin, TemplateView):
    template_name = 'planning_form.html'

class StatisticsView(LoginRequiredMixin, FilterView):
    template_name = 'statistics.html'
    model = Expense
    context_object_name = 'expenses'
    filterset_fields = ['category', 'date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['form'] = ExpenseForm()

        return context

class SuppliesView(LoginRequiredMixin, TemplateView):
    template_name = 'supplies.html'

class SuppliesDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'supplies_detail.html'


class SuppliesFormView(LoginRequiredMixin, ListView):
    template_name = 'supplies_form.html'
    model = AgriculturalInputs
    context_object_name = 'supplies'

class ExpenseCreateUpdateView(LoginRequiredMixin,FormView):
    template_name = "statistics.html"
    form_class = ExpenseForm

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        """Adiciona a lista de despesas e categorias ao contexto do template"""
        context = super().get_context_data(**kwargs)
        context["expenses"] = Expense.objects.all()
        context["categories"] = ExpensesCategory.objects.all()
        return context

    def get_form_kwargs(self):
        """
        Aqui é a mágica: verificamos se é uma edição ou criação.
        Se vier um 'id' no POST, injetamos a 'instance' no formulário.
        """
        kwargs = super().get_form_kwargs()
        
        if self.request.method == "POST":
            expense_id = self.request.POST.get("id")
            if expense_id:
                expense_instance = get_object_or_404(Expense, id=expense_id)
                kwargs["instance"] = expense_instance
        
        return kwargs

    def form_valid(self, form):
        """Se o form for válido, salvamos (create ou update)"""
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """Se der erro, o FormView já recarrega a página com os erros automaticamente"""
        return super().form_invalid(form)
    
