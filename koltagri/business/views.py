from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView ,ListView,CreateView,UpdateView,DetailView,DeleteView,FormView
from django_filters.views import FilterView
from .models import Expense,ExpensesCategory,AgriculturalInputs,AgriculturalInputUsage,AgriculturalInputPack
from .forms import ExpenseForm,AgriculturalInputPackForm,AgriculturalInputUsageForm
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from koltagri.landplots.models import Site
from django.http import HttpResponseForbidden
from .forms import AgriculturalInputValidationForm
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import FormView,UpdateView
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
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
    
    def get_queryset(self):

        site = self.request.session['selected_site_location']

        q = super().get_queryset()
        queryset = q.filter(site=site)
        return queryset


class SuppliesView(LoginRequiredMixin, TemplateView):
    template_name = 'supplies.html'

class SuppliesDetailView(LoginRequiredMixin, DetailView):
    template_name = 'supplies/supplies_detail.html'
    model = AgriculturalInputs
    context_object_name = 'insumo'


class SuppliesFormView(LoginRequiredMixin, ListView):
    template_name = 'supplies_form.html'
    model = AgriculturalInputs
    context_object_name = 'supplies'

    def get_queryset(self):
        site = self.request.session['selected_site_location']
        q =  super().get_queryset()
        queryset = q.filter(site=site)
        return queryset

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
        site_id = self.request.session.get("selected_site_location")

        if not site_id:
            return HttpResponseForbidden("Site não selecionado")

        expense = form.save(commit=False)
        site = get_object_or_404(Site, id=site_id)
        expense.site = site
        expense.save()

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
        pk = self.kwargs.get("pk")
        site_id = self.request.session.get("selected_site_location")

        if pk and site_id:
            return get_object_or_404(
                AgriculturalInputs,
                pk=pk,
                site_id=site_id
            )
        return None

    def get(self, request, *args, **kwargs):
        insumo = self.get_object()

        initial = {}
        if insumo:
            initial = {
                "name": insumo.name,
                "description": insumo.description,
                "unit": insumo.unit,
            }

        form = AgriculturalInputValidationForm(initial=initial)

        return render(request, self.template_name, {
            "form": form,
            "insumo": insumo,
            "is_edit": insumo is not None,
        })

    def post(self, request, *args, **kwargs):
        insumo = self.get_object()
        form = AgriculturalInputValidationForm(request.POST, request.FILES)
        print("POST data:", dict(request.POST))
        print("FILES:", dict(request.FILES))
        if form.is_valid():
            cd = form.cleaned_data
            site_id = request.session.get("selected_site_location")

            if not site_id:
                return HttpResponseForbidden("Site não selecionado")

            if insumo:
                # UPDATE
                insumo.name = cd["name"]
                insumo.description = cd.get("description")
                insumo.unit = cd["unit"]
                

                img = cd.get("image") if "image" in cd else request.FILES.get("image")
                if img:
                    insumo.image = img

                insumo.save()
                messages.success(request, "Insumo atualizado com sucesso.")
            else:
                # CREATE
                img = cd.get("image") if "image" in cd else request.FILES.get("image")

                AgriculturalInputs.objects.create(
                    site_id=site_id,
                    name=cd["name"],
                    description=cd.get("description"),
                    unit=cd["unit"],
                    image=img,
                )
                messages.success(request, "Insumo criado com sucesso.")

            return redirect(reverse("supplies"))
        
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
    # Remova a verificação do site_id já que o modelo não tem esse campo
    # site_id = request.session.get("selected_site_location")
    # if not site_id:
    #     return JsonResponse({"error": "Site não selecionado"}, status=400)

    # Use todas as despesas do usuário (ou filtre por outro critério)
    expenses_qs = Expense.objects.all()  # Modifique conforme necessário
    
    # Se você quer filtrar por usuário logado, precisa adicionar um campo user ao modelo
    # expenses_qs = Expense.objects.filter(user=request.user)
    
    # Total por categoria (geral)
    expenses_by_category = (
        expenses_qs
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    # Gastos do mês atual
    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    expenses_this_month = (
        expenses_qs
        .filter(date__gte=first_day_of_month)
        .aggregate(total=Sum("amount"))
    )
    
    # Categoria principal
    main_category = expenses_by_category.first() if expenses_by_category else None

    labels = [e["category__name"] for e in expenses_by_category]
    data = [float(e["total"]) for e in expenses_by_category]

    return JsonResponse({
        "labels": labels,
        "data": data,
        "month_total": expenses_this_month["total"] or 0,
        "main_category": main_category["category__name"] if main_category else None,
        "main_category_total": main_category["total"] if main_category else 0
    })
class ExpenseDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        expense = get_object_or_404(Expense, id=kwargs.get("pk"))
        expense.delete()
        return redirect("statistics")



class AgriculturalInputPackListView(LoginRequiredMixin, FilterView):
    model = AgriculturalInputPack
    template_name = "supplies/packs_list.html"
    context_object_name = "packs"
    paginate_by = 30
    queryset = AgriculturalInputPack.objects.order_by("-purchase_date")


    def get_queryset(self):
        q = super().get_queryset()
        site_id = self.request.session.get("selected_site_location")

        if not site_id:
            return q.none()

        return q.filter(agricultural_input__site_id=site_id)


class AgriculturalInputPackDetailView(LoginRequiredMixin, DetailView):
    model = AgriculturalInputPack
    template_name = "supplies/pack_detail.html"
    context_object_name = "pack"


class AgriculturalInputPackCreateView(LoginRequiredMixin, CreateView):
    model = AgriculturalInputPack
    form_class = AgriculturalInputPackForm
    template_name = "supplies/pack_form.html"

    def form_valid(self, form):
        # garante que o name será gerado no save() do modelo (se save só gerar quando vazio)
        instance = form.save(commit=False)
        # se quiser forçar nome sempre atualizado: instance.name = instance.generate_name()
        instance.save()
        messages.success(self.request, "Pack criado com sucesso.")
        return redirect(reverse("pack_detail", kwargs={"pk": instance.pk}))


class AgriculturalInputPackUpdateView(LoginRequiredMixin, UpdateView):
    model = AgriculturalInputPack
    form_class = AgriculturalInputPackForm
    template_name = "inputs/pack_form.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        # re-gerar o nome aqui para refletir mudanças em quantity (mesmo que save() só gere quando vazio)
        instance.name = instance.generate_name()
        instance.save()
        messages.success(self.request, "Pack atualizado com sucesso.")
        return redirect(reverse("pack_detail", kwargs={"pk": instance.pk}))


# View para criar um uso (consumo)
class AgriculturalInputUsageCreateView(LoginRequiredMixin, CreateView):
    model = AgriculturalInputUsage
    form_class = AgriculturalInputUsageForm
    template_name = "inputs/usage_form.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        # se quiser gravar quem criou, ajuste o modelo para ter created_by
        # instance.created_by = self.request.user
        instance.save()
        messages.success(self.request, "Uso registrado com sucesso.")
        return redirect(reverse("cultivationplant_detail", kwargs={"pk": instance.cultivation_plant.pk}))