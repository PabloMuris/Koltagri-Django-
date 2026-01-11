from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView ,ListView,CreateView,UpdateView,DetailView,DeleteView,FormView
from django_filters.views import FilterView
from .models import Expense,ExpensesCategory,AgriculturalInputs
from .forms import ExpenseForm
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from .forms import AgriculturalInputValidationForm
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import FormView,UpdateView

from koltagri.landplots.permissions import IsInGroupPermissionMixin

from django.contrib.auth.decorators import login_required

class BusinessDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'business.html'

class PlanningView(LoginRequiredMixin, TemplateView):
    template_name = 'planning_form.html'

class StatisticsView(LoginRequiredMixin, FilterView):
    template_name = 'statistics.html'
    model = Expense
    context_object_name = 'expenses'
    filterset_fields = ['category', 'date','description']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['form'] = ExpenseForm()

        return context

class SuppliesView(LoginRequiredMixin, TemplateView):
    template_name = 'supplies.html'

class SuppliesDetailView(LoginRequiredMixin, DetailView):
    template_name = 'supplies_detail.html'
    model = AgriculturalInputs
    context_object_name = 'insumo'


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
    

class SupplieDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        supllie = get_object_or_404(AgriculturalInputs, id=kwargs.get("pk"))
        supllie.delete()
        return redirect("supplies")





class AgriculturalInputCreateUpdateView(LoginRequiredMixin, View):
    template_name = "supplies/supplies_form.html"

    def get_object(self):
        # pega pk direto das kwargs — se não vier, retorna None
        pk = self.kwargs.get("pk")
        if pk:
            return get_object_or_404(AgriculturalInputs, pk=pk)
        return None

    def get(self, request, *args, **kwargs):
        insumo = self.get_object()

        # se for edição, preenche initial com os valores do insumo
        initial = {}
        if insumo:
            initial = {
                "name": insumo.name,
                "description": insumo.description,
                "quantity": insumo.quantity,
                "unit": insumo.unit,
                "purchase_date": insumo.purchase_date,
                "price": insumo.price,
            }

        form = AgriculturalInputValidationForm(initial=initial)

        return render(request, self.template_name, {
            "form": form,
            "insumo": insumo,
            "is_edit": insumo is not None,
        })

    def post(self, request, *args, **kwargs):
        insumo = self.get_object()

        # note: AgriculturalInputValidationForm é forms.Form -> não recebe instance
        form = AgriculturalInputValidationForm(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data

            if insumo:
                # UPDATE manual (igual ao que você tinha)
                insumo.name = cd["name"]
                insumo.description = cd.get("description")
                insumo.quantity = cd["quantity"]
                insumo.unit = cd["unit"]
                insumo.purchase_date = cd.get("purchase_date")
                insumo.price = cd["price"]

                # imagem: venha de request.FILES via form.cleaned_data (se configurado)
                # aqui usamos request.FILES diretamente caso form não contenha image
                img = cd.get("image") if "image" in cd else request.FILES.get("image")
                if img:
                    insumo.image = img

                insumo.save()
                messages.success(request, "Insumo atualizado com sucesso.")
            else:
                # CREATE manual
                img = cd.get("image") if "image" in cd else request.FILES.get("image")
                AgriculturalInputs.objects.create(
                    name=cd["name"],
                    description=cd.get("description"),
                    quantity=cd["quantity"],
                    unit=cd["unit"],
                    purchase_date=cd.get("purchase_date"),
                    price=cd["price"],
                    image=img,
                )
                messages.success(request, "Insumo criado com sucesso.")

            return redirect(reverse("supplies"))  # ajuste se necessário

        # se inválido, reexibe com erros e insumo (para o template decidir action/labels)
        return render(request, self.template_name, {
            "form": form,
            "insumo": insumo,
            "is_edit": insumo is not None,
        })


class ExpenseUpdateView(LoginRequiredMixin,UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "financial/expense_form.html"

    def get_success_url(self):
        return reverse("statistics")
    


@login_required
def expense_data_view(request):
    site_id = request.session.get("selected_site_location")

    if not site_id:
        return JsonResponse({"error": "Site não selecionado"}, status=400)

    expenses = (
        Expense.objects
        .filter(site_id=site_id)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("category__name")
    )

    labels = [e["category__name"] for e in expenses]
    data = [float(e["total"]) for e in expenses]

    return JsonResponse({
        "labels": labels,
        "data": data
    })

class ExpenseDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        expense = get_object_or_404(Expense, id=kwargs.get("pk"))
        expense.delete()
        return redirect("statistics")



