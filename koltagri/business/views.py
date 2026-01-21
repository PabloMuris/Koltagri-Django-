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
    template_name = 'financial/statistics.html'
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

    def get_queryset(self):

        site = self.request.session['selected_site_location']

        q = super().get_queryset()
        queryset = q.filter(site=site)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sup_pk'] = self.kwargs.get('pk')
        return context


class SuppliesListView(LoginRequiredMixin, ListView):
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



# business/views.py
class AgriculturalInputPackListView(LoginRequiredMixin, ListView):
    model = AgriculturalInputPack
    template_name = "supplies/packs_list.html"
    context_object_name = "packs"
    paginate_by = 10
    
    def get_queryset(self):
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        
        if not site_id:
            return AgriculturalInputPack.objects.none()
        
        # Verifica se o insumo existe e pertence ao site
        try:
            agricultural_input = AgriculturalInputs.objects.get(
                id=supplie_pk,
                site_id=site_id
            )
        except AgriculturalInputs.DoesNotExist:
            return AgriculturalInputPack.objects.none()
        
        # Retorna apenas packs deste insumo
        return AgriculturalInputPack.objects.filter(
            agricultural_input=agricultural_input
        ).order_by("-purchase_date")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        
        try:
            # Obtém o insumo para o contexto
            context['agricultural_input'] = AgriculturalInputs.objects.get(
                id=supplie_pk,
                site_id=site_id
            )
        except AgriculturalInputs.DoesNotExist:
            # Se não encontrar, passa None e lidaremos no template
            context['agricultural_input'] = None
        
        # Calcula totais
        queryset = self.get_queryset()
        context['total_packs'] = queryset.count()
        
        # Calcula o valor total
        total_value = queryset.aggregate(total=Sum('price'))['total']
        context['total_value'] = total_value if total_value else 0
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        site_id = request.session.get("selected_site_location")
        if not site_id:
            messages.error(request, "Site não selecionado.")
            return redirect('business_board')
        return super().dispatch(request, *args, **kwargs)

class AgriculturalInputPackDetailView(LoginRequiredMixin, DetailView):
    model = AgriculturalInputPack
    template_name = "supplies/pack_detail.html"
    context_object_name = "pack"


class AgriculturalInputPackCreateView(LoginRequiredMixin, CreateView):
    model = AgriculturalInputPack
    form_class = AgriculturalInputPackForm
    template_name = "supplies/pack_form.html"

    def get_context_data(self, **kwargs):
        """Adiciona o insumo ao contexto"""
        context = super().get_context_data(**kwargs)
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        
        try:
            # Passa o insumo para o template
            context['agricultural_input'] = AgriculturalInputs.objects.get(
                id=supplie_pk,
                site_id=site_id
            )
        except AgriculturalInputs.DoesNotExist:
            context['agricultural_input'] = None
            
        return context

    def get_initial(self):
        """Configura valores iniciais"""
        initial = super().get_initial()
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        
        try:
            insumo = AgriculturalInputs.objects.get(
                id=supplie_pk,
                site_id=site_id
            )
            initial['agricultural_input'] = insumo
        except AgriculturalInputs.DoesNotExist:
            pass
            
        return initial

    def form_valid(self, form):
        """Salva o pack e cria a despesa automaticamente"""
        site_id = self.request.session.get("selected_site_location")
        
        if not site_id:
            messages.error(self.request, "Site não selecionado.")
            return redirect('business_board')
        
        # Obtém o insumo
        supplie_pk = self.kwargs.get('supplie_pk')
        try:
            agricultural_input = AgriculturalInputs.objects.get(
                id=supplie_pk,
                site_id=site_id
            )
        except AgriculturalInputs.DoesNotExist:
            messages.error(self.request, "Insumo não encontrado.")
            return redirect('supplies')
        
        # Salva o pack
        instance = form.save(commit=False)
        instance.agricultural_input = agricultural_input
        
        # Garante que o nome seja gerado
        instance.name = instance.generate_name()
        instance.save()
        
        # Cria a despesa automaticamente
        self.create_expense_for_pack(instance)
        
        messages.success(self.request, "Pack criado com sucesso e despesa registrada.")
        return redirect(reverse("pack_detail", kwargs={"pk": instance.pk}))

    def create_expense_for_pack(self, pack):
        """
        Cria uma despesa automaticamente para o pack usando a categoria "Insumos"
        """
        try:
            site = pack.agricultural_input.site
            
            # 1. Obter ou criar a categoria de despesa "Insumos"
            category, created = ExpensesCategory.objects.get_or_create(
                name="Insumos"
            )
            
            # 2. Criar a descrição da despesa
            unit_display = pack.agricultural_input.get_unit_display()
            description = (
                f"Aquisição de {pack.quantity} {unit_display} de "
                f"{pack.agricultural_input.name}"
            )
            
            # 3. Criar notas adicionais
            note = (
                f"Pack ID: {pack.id}\n"
                f"Insumo: {pack.agricultural_input.name}\n"
                f"Quantidade: {pack.quantity} {unit_display}\n"
                f"Preço unitário: R${pack.price / pack.quantity:.2f}\n"
                f"Data da compra: {pack.purchase_date}\n"
                f"Registrado automaticamente ao cadastrar o pack."
            )
            
            # 4. Criar a despesa
            Expense.objects.create(
                site=site,
                category=category,
                amount=pack.price,  # Preço total do pack
                date=pack.purchase_date,
                description=description,
                note=note
            )
            
        except Exception as e:
            # Log do erro, mas não impedir a criação do pack
            print(f"Erro ao criar despesa para pack: {e}")
            # Você também pode enviar uma mensagem de alerta
            messages.warning(self.request, 
                f"Pack criado, mas houve um erro ao registrar a despesa: {e}")
            
class AgriculturalInputPackUpdateView(LoginRequiredMixin, UpdateView):
    model = AgriculturalInputPack
    form_class = AgriculturalInputPackForm
    template_name = "supplies/pack_form.html"

    def get_object(self, queryset=None):
        """Busca o objeto com validação"""
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        pack_pk = self.kwargs.get('pk')
        
        if not site_id:
            return None
            
        return get_object_or_404(
            AgriculturalInputPack, 
            pk=pack_pk,
            agricultural_input_id=supplie_pk,
            agricultural_input__site_id=site_id
        )

    def form_valid(self, form):
        """Atualiza o pack e atualiza a despesa relacionada"""
        instance = form.save(commit=False)
        
        # Pega o valor antigo do preço
        old_instance = AgriculturalInputPack.objects.get(pk=instance.pk)
        old_price = old_instance.price
        
        # Re-gerar o nome
        instance.name = instance.generate_name()
        instance.save()
        
        # Se o preço foi alterado, atualiza a despesa relacionada
        if old_price != instance.price:
            self.update_expense_for_pack(instance)
            messages.success(self.request, 
                "Pack atualizado com sucesso. Despesa ajustada.")
        else:
            messages.success(self.request, "Pack atualizado com sucesso.")
            
        return redirect(reverse("pack_detail", kwargs={"pk": instance.pk}))

    def update_expense_for_pack(self, pack):
        """
        Atualiza a despesa relacionada ao pack
        """
        try:
            # Procura a despesa relacionada a este pack
            # Podemos identificar pela nota que contém "Pack ID: {pack.id}"
            expenses = Expense.objects.filter(
                site=pack.agricultural_input.site,
                note__contains=f"Pack ID: {pack.id}"
            )
            
            if expenses.exists():
                # Atualiza a primeira despesa encontrada
                expense = expenses.first()
                expense.amount = pack.price
                expense.date = pack.purchase_date
                
                unit_display = pack.agricultural_input.get_unit_display()
                expense.description = (
                    f"Aquisição de {pack.quantity} {unit_display} de "
                    f"{pack.agricultural_input.name}"
                )
                
                expense.note = (
                    f"Pack ID: {pack.id}\n"
                    f"Insumo: {pack.agricultural_input.name}\n"
                    f"Quantidade: {pack.quantity} {unit_display}\n"
                    f"Preço unitário: R${pack.price / pack.quantity:.2f}\n"
                    f"Data da compra: {pack.purchase_date}\n"
                    f"Atualizado automaticamente ao editar o pack."
                )
                
                expense.save()
            else:
                # Se não encontrar, cria uma nova
                self.create_expense_for_pack(pack)
                
        except Exception as e:
            print(f"Erro ao atualizar despesa para pack: {e}")

    def create_expense_for_pack(self, pack):
        """
        Método auxiliar para criar despesa (reutilizado do CreateView)
        Usa a categoria "Insumos"
        """
        try:
            site = pack.agricultural_input.site
            
            # Obter ou criar a categoria de despesa "Insumos"
            category, created = ExpensesCategory.objects.get_or_create(
                name="Insumos"
            )
            
            # Criar a descrição da despesa
            unit_display = pack.agricultural_input.get_unit_display()
            description = (
                f"Aquisição de {pack.quantity} {unit_display} de "
                f"{pack.agricultural_input.name}"
            )
            
            # Criar notas adicionais
            note = (
                f"Pack ID: {pack.id}\n"
                f"Insumo: {pack.agricultural_input.name}\n"
                f"Quantidade: {pack.quantity} {unit_display}\n"
                f"Preço unitário: R${pack.price / pack.quantity:.2f}\n"
                f"Data da compra: {pack.purchase_date}\n"
                f"Registrado automaticamente ao editar o pack."
            )
            
            # Criar a despesa
            Expense.objects.create(
                site=site,
                category=category,
                amount=pack.price,
                date=pack.purchase_date,
                description=description,
                note=note
            )
            
        except Exception as e:
            print(f"Erro ao criar despesa para pack: {e}")

class AgriculturalInputUsageCreateView(LoginRequiredMixin, CreateView):
    model = AgriculturalInputUsage
    form_class = AgriculturalInputUsageForm
    template_name = "supplies/pack_usage_form.html"

    def get_pack(self):
        """Obtém o pack baseado nos parâmetros da URL"""
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        pack_pk = self.kwargs.get('pk')
        
        if not site_id:
            return None
            
        return get_object_or_404(
            AgriculturalInputPack,
            id=pack_pk,
            agricultural_input__id=supplie_pk,
            agricultural_input__site_id=site_id
        )

    def get_initial(self):
        """Configura valores iniciais do formulário"""
        initial = super().get_initial()
        pack = self.get_pack()
        
        if pack:
            initial['pack'] = pack
            initial['usage_date'] = timezone.now().date()
            
        return initial

    def get_form_kwargs(self):
        """Passa o pack para o formulário"""
        kwargs = super().get_form_kwargs()
        pack = self.get_pack()
        
        if pack:
            # Passa o pack para o form
            kwargs['pack'] = pack
            
            # Limita o queryset do campo pack apenas a este pack
            kwargs['pack_queryset'] = AgriculturalInputPack.objects.filter(pk=pack.pk)
        
        return kwargs

    def get_context_data(self, **kwargs):
        """Adiciona informações do pack ao contexto"""
        context = super().get_context_data(**kwargs)
        pack = self.get_pack()
        
        if pack:
            context['pack'] = pack
            context['available_quantity'] = pack.remaining_quantity()
            context['unit'] = pack.agricultural_input.get_unit_display()
            context['supplie'] = pack.agricultural_input
            
        return context

    def form_valid(self, form):
        """Valida e salva o uso"""
        instance = form.save(commit=False)
        pack = instance.pack
        
        # Verificação final de segurança
        if instance.quantity_used > pack.remaining_quantity():
            form.add_error('quantity_used', 
                f"Erro: Quantidade excede o estoque disponível. "
                f"Restam apenas {pack.remaining_quantity()} {pack.agricultural_input.unit}.")
            return self.form_invalid(form)
        
        instance.save()
        messages.success(self.request, "Uso registrado com sucesso!")
        
        # Redireciona de volta para a lista de packs do insumo
        return redirect("packs_list", supplie_pk=pack.agricultural_input.id)

class AgriculturalInputPackDeleteView(LoginRequiredMixin, DeleteView):
    model = AgriculturalInputPack
    template_name = "supplies/pack_delete_modal.html"
    
    def get_object(self, queryset=None):
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        pk = self.kwargs.get('pk')
        
        if not site_id:
            return None
            
        return get_object_or_404(
            AgriculturalInputPack,
            id=pk,
            agricultural_input__id=supplie_pk,
            agricultural_input__site_id=site_id
        )
    
    def delete(self, request, *args, **kwargs):
        # Primeiro exclui a despesa relacionada
        pack = self.get_object()
        if pack:
            self.delete_related_expense(pack)
        
        # Depois exclui o pack
        return super().delete(request, *args, **kwargs)
    
    def delete_related_expense(self, pack):
        """Exclui a despesa relacionada ao pack"""
        try:
            expenses = Expense.objects.filter(
                site=pack.agricultural_input.site,
                note__contains=f"Pack ID: {pack.id}"
            )
            
            if expenses.exists():
                expense = expenses.first()
                expense.delete()
        except Exception as e:
            print(f"Erro ao excluir despesa do pack: {e}")
    
    def get_success_url(self):
        supplie_pk = self.kwargs.get('supplie_pk')
        messages.success(self.request, "Pack e despesa relacionada excluídos com sucesso.")
        return reverse('packs_list', kwargs={'supplie_pk': supplie_pk})
    


# business/views.py

class PackUsagesListView(LoginRequiredMixin, ListView):
    template_name = 'supplies/usages_list.html'
    model = AgriculturalInputUsage
    context_object_name = "usages"
    paginate_by = 10
    
    def get_queryset(self):
        """Filtra os usos pelo pack específico"""
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        pack_pk = self.kwargs.get('pk')
        
        if not site_id:
            return AgriculturalInputUsage.objects.none()
        
        # Verifica se o pack existe e pertence ao site
        try:
            pack = AgriculturalInputPack.objects.get(
                id=pack_pk,
                agricultural_input__id=supplie_pk,
                agricultural_input__site_id=site_id
            )
        except AgriculturalInputPack.DoesNotExist:
            return AgriculturalInputUsage.objects.none()
        
        # Retorna os usos deste pack, ordenados por data decrescente
        return AgriculturalInputUsage.objects.filter(
            pack=pack
        ).order_by("-usage_date", "-created_at")
    
    def get_context_data(self, **kwargs):
        """Adiciona informações do pack e insumo ao contexto"""
        context = super().get_context_data(**kwargs)
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        pack_pk = self.kwargs.get('pk')
        
        try:
            # Obtém o pack
            pack = AgriculturalInputPack.objects.get(
                id=pack_pk,
                agricultural_input__id=supplie_pk,
                agricultural_input__site_id=site_id
            )
            context['pack'] = pack
            context['agricultural_input'] = pack.agricultural_input
            
            # Calcula totais
            queryset = self.get_queryset()
            context['total_usages'] = queryset.count()
            
            # Soma da quantidade total usada
            total_used = queryset.aggregate(total=Sum('quantity_used'))['total']
            context['total_quantity_used'] = total_used if total_used else 0
            
            # Quantidade restante no pack
            context['remaining_quantity'] = pack.remaining_quantity()
            
        except AgriculturalInputPack.DoesNotExist:
            context['pack'] = None
            context['agricultural_input'] = None
            context['total_usages'] = 0
            context['total_quantity_used'] = 0
            context['remaining_quantity'] = 0
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        site_id = request.session.get("selected_site_location")
        if not site_id:
            messages.error(request, "Site não selecionado.")
            return redirect('business_board')
        return super().dispatch(request, *args, **kwargs)