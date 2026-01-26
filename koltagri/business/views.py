from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView ,ListView,CreateView,UpdateView,DetailView,DeleteView,FormView
from django_filters.views import FilterView
from .models import Expense,ExpensesCategory,AgriculturalInputs,AgriculturalInputUsage,AgriculturalInputPack
from .forms import ExpenseForm,AgriculturalInputPackForm,AgriculturalInputUsageForm
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from .filters import ExpenseFilter
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

from koltagri.core.mixins import IsManagerMixin
from django.contrib.auth.decorators import login_required


from koltagri.core.mixins import SiteRequiredMixin

class BusinessDashboardView(SiteRequiredMixin, TemplateView):
    template_name = 'business.html'

class PlanningView(LoginRequiredMixin, TemplateView):
    template_name = 'planning_form.html'

class StatisticsView(SiteRequiredMixin, FilterView):
    template_name = 'financial/statistics.html'
    model = Expense
    context_object_name = 'expenses'
    filterset_class = ExpenseFilter  # Usar o filtro personalizado
    paginate_by = 10

    def get_queryset(self):
        site = self.request.session['selected_site_location']
        queryset = super().get_queryset()
        queryset = queryset.filter(site=site).order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar formulário de criação
        context['form'] = ExpenseForm()
        
        # Adicionar todas as categorias para o filtro
        context['categories'] = ExpensesCategory.objects.all()
        
        # Obter dados filtrados para os cards
        filtered_queryset = self.filterset.qs
        
        # Total de gastos
        total_expenses = filtered_queryset.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Gastos do mês atual
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        expenses_this_month = filtered_queryset.filter(
            date__gte=first_day_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Categoria principal
        expenses_by_category = (
            filtered_queryset
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        
        main_category = expenses_by_category.first() if expenses_by_category else None
        
        # Adicionar dados para os cards
        context['total_expenses_filtered'] = total_expenses
        context['month_expenses_filtered'] = expenses_this_month
        context['main_category_filtered'] = main_category
        
        return context

class SuppliesView(LoginRequiredMixin, TemplateView):
    template_name = 'supplies/supplies.html'

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


class SuppliesListView(SiteRequiredMixin, ListView):
    template_name = 'extra/supplies_form.html'
    model = AgriculturalInputs
    context_object_name = 'supplies'

    def get_queryset(self):
        site = self.request.session['selected_site_location']
        q =  super().get_queryset()
        queryset = q.filter(site=site)
        return queryset

class ExpenseCreateUpdateView(LoginRequiredMixin,FormView):
    template_name = "financial/statistics.html"
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
        
        
        return AgriculturalInputPack.objects.filter(
            agricultural_input=agricultural_input
        ).order_by("-purchase_date")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_id = self.request.session.get("selected_site_location")
        supplie_pk = self.kwargs.get('supplie_pk')
        
        try:
            
            context['agricultural_input'] = AgriculturalInputs.objects.get(
                id=supplie_pk,
                site_id=site_id
            )
        except AgriculturalInputs.DoesNotExist:
            
            context['agricultural_input'] = None
        
        # Calcula totais
        queryset = self.get_queryset()
        context['total_packs'] = queryset.count()
        context['supplie_pk'] = supplie_pk

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

         # Para redirecionar para o detalhe do pack

        messages.success(self.request, "Pack criado com sucesso e despesa registrada.")
        return redirect(reverse("packs_list", kwargs={"supplie_pk": supplie_pk }))

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
    

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from django.db.models import Sum, Count, F, Q
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import csv
import openpyxl
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
import matplotlib.pyplot as plt
import numpy as np

class GenerateExpenseReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        site_id = request.session.get("selected_site_location")
        if not site_id:
            return JsonResponse({"error": "Site não selecionado"}, status=400)
        
        site = get_object_or_404(Site, id=site_id)
        
        # Obter parâmetros do formulário
        period_type = request.POST.get('period', 'month')
        month = request.POST.get('month')
        year = request.POST.get('year')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        report_format = request.POST.get('format', 'pdf')
        
        include_plant_data = request.POST.get('include_plant_data') == 'on'
        include_cultivation_data = request.POST.get('include_cultivation_data') == 'on'
        include_production_data = request.POST.get('include_production_data') == 'on'
        include_break_even = request.POST.get('include_break_even') == 'on'
        
        # Definir período baseado nos parâmetros
        today = timezone.now().date()
        
        if period_type == 'month' and month:
            year_month = month.split('-')
            year = int(year_month[0])
            month = int(year_month[1])
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        elif period_type == 'year' and year:
            start_date = datetime(int(year), 1, 1).date()
            end_date = datetime(int(year), 12, 31).date()
        elif period_type == 'custom' and start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Padrão: mês atual
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Coletar dados para o relatório
        report_data = self.collect_report_data(
            site, start_date, end_date, 
            include_plant_data, include_cultivation_data, 
            include_production_data, include_break_even
        )
        
        # Gerar relatório no formato solicitado
        if report_format == 'pdf':
            return self.generate_pdf_report(report_data, start_date, end_date, site.name)
        elif report_format == 'excel':
            return self.generate_excel_report(report_data, start_date, end_date, site.name)
        elif report_format == 'csv':
            return self.generate_csv_report(report_data, start_date, end_date, site.name)
        else:
            return JsonResponse({"error": "Formato não suportado"}, status=400)
    
    def collect_report_data(self, site, start_date, end_date, 
                           include_plant_data, include_cultivation_data,
                           include_production_data, include_break_even):
        """
        Coleta todos os dados necessários para o relatório
        """
        data = {
            'site_name': site.name,
            'period': f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}",
            'start_date': start_date,
            'end_date': end_date,
        }
        
        # 1. Gastos por categoria
        expenses_by_category = (
            Expense.objects.filter(
                site=site,
                date__range=[start_date, end_date]
            )
            .values('category__name')
            .annotate(
                total=Sum('amount'),
                count=Count('id')
            )
            .order_by('-total')
        )
        data['expenses_by_category'] = list(expenses_by_category)
        
        # 2. Total de gastos
        total_expenses = (
            Expense.objects.filter(
                site=site,
                date__range=[start_date, end_date]
            ).aggregate(total=Sum('amount'))['total'] or 0
        )
        data['total_expenses'] = total_expenses
        
        # 3. Gastos por espécie de planta (se solicitado)
        if include_plant_data:
            # Gastos relacionados a insumos usados por espécie
            from koltagri.landplots.models import CultivationPlant, PlantSpecies
            
            plant_expenses = (
                AgriculturalInputUsage.objects.filter(
                    pack__agricultural_input__site=site,
                    usage_date__range=[start_date, end_date]
                )
                .values(
                    'cultivation_plant__plant_species__name'
                )
                .annotate(
                    total_cost=Sum(F('quantity_used') * F('pack__price') / F('pack__quantity')),
                    total_used=Sum('quantity_used')
                )
                .order_by('-total_cost')
            )
            data['expenses_by_plant_species'] = list(plant_expenses)
        
        # 4. Gastos por área cultivada (se solicitado)
        if include_cultivation_data:
            cultivation_expenses = (
                AgriculturalInputUsage.objects.filter(
                    pack__agricultural_input__site=site,
                    usage_date__range=[start_date, end_date]
                )
                .values(
                    'cultivation_plant__cultivation__name',
                    'cultivation_plant__plant_species__name'
                )
                .annotate(
                    total_cost=Sum(F('quantity_used') * F('pack__price') / F('pack__quantity')),
                    area_size=Count('cultivation_plant', distinct=True)
                )
                .order_by('-total_cost')
            )
            data['expenses_by_cultivation_area'] = list(cultivation_expenses)
        
        # 5. Dados de produção (se solicitado)
        if include_production_data:
            from koltagri.landplots.models import HarvestCultivationPlant
            
            production_data = (
                HarvestCultivationPlant.objects.filter(
                    cultivation_plant__cultivation__site=site,
                    harvest_date__range=[start_date, end_date]
                )
                .values(
                    'cultivation_plant__plant_species__name',
                    'unity'
                )
                .annotate(
                    total_quantity=Sum('quantity'),
                    total_harvests=Count('id')
                )
                .order_by('-total_quantity')
            )
            data['production_data'] = list(production_data)
            
            # Total de produção
            total_production = (
                HarvestCultivationPlant.objects.filter(
                    cultivation_plant__cultivation__site=site,
                    harvest_date__range=[start_date, end_date]
                ).aggregate(total=Sum('quantity'))['total'] or 0
            )
            data['total_production'] = total_production
        
        # 6. Cálculo de ponto de equilíbrio (se solicitado)
        if include_break_even:
            # Gastos com insumos
            input_expenses = (
                AgriculturalInputPack.objects.filter(
                    agricultural_input__site=site,
                    purchase_date__range=[start_date, end_date]
                ).aggregate(total=Sum('price'))['total'] or 0
            )
            
            # Outros gastos (não insumos)
            other_expenses = (
                Expense.objects.filter(
                    site=site,
                    date__range=[start_date, end_date]
                ).exclude(
                    category__name__icontains='insumo'
                ).aggregate(total=Sum('amount'))['total'] or 0
            )
            
            # Cálculo simplificado do ponto de equilíbrio
            # Assumindo um preço de venda médio (você pode ajustar isso)
            avg_selling_price = Decimal('10.00')  # Preço médio por unidade
            
            if avg_selling_price > 0 and data.get('total_production', 0) > 0:
                total_costs = input_expenses + other_expenses
                break_even_units = total_costs / avg_selling_price
                actual_units = data.get('total_production', 0)
                profitability = (actual_units * avg_selling_price) - total_costs
                
                data['break_even_analysis'] = {
                    'input_expenses': input_expenses,
                    'other_expenses': other_expenses,
                    'total_costs': total_costs,
                    'avg_selling_price': avg_selling_price,
                    'break_even_units': break_even_units,
                    'actual_units': actual_units,
                    'profitability': profitability,
                    'is_profitable': profitability > 0
                }
        
        return data
    
    def generate_pdf_report(self, data, start_date, end_date, site_name):
        """
        Gera um relatório em PDF usando ReportLab
        """
        buffer = io.BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story.append(Paragraph(f"Relatório Financeiro - {site_name}", title_style))
        story.append(Paragraph(f"Período: {data['period']}", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # 1. Resumo Executivo
        story.append(Paragraph("1. Resumo Executivo", styles['Heading2']))
        
        summary_data = [
            ['Total de Gastos', f"R$ {data['total_expenses']:.2f}"],
            ['Período Analisado', data['period']],
            ['Site/Fazenda', site_name],
        ]
        
        if 'total_production' in data:
            summary_data.append(['Total Produzido', f"{data['total_production']} unidades"])
        
        if 'break_even_analysis' in data:
            profitability_status = "Lucrativo" if data['break_even_analysis']['is_profitable'] else "Prejuízo"
            summary_data.append(['Situação Financeira', profitability_status])
            summary_data.append(['Lucro/Prejuízo', f"R$ {data['break_even_analysis']['profitability']:.2f}"])
        
        summary_table = Table(summary_data, colWidths=[200, 200])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4a6fa5')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 14),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # 2. Gastos por Categoria
        story.append(Paragraph("2. Gastos por Categoria", styles['Heading2']))
        
        if data['expenses_by_category']:
            category_data = [['Categoria', 'Total (R$)', 'Nº de Gastos']]
            for item in data['expenses_by_category']:
                category_data.append([
                    item['category__name'],
                    f"{item['total']:.2f}",
                    str(item['count'])
                ])
            
            category_table = Table(category_data, colWidths=[250, 150, 100])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            
            story.append(category_table)
        else:
            story.append(Paragraph("Nenhum gasto registrado neste período.", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # 3. Dados por Espécie de Planta (se disponível)
        if 'expenses_by_plant_species' in data and data['expenses_by_plant_species']:
            story.append(Paragraph("3. Gastos por Espécie de Planta", styles['Heading2']))
            
            plant_data = [['Espécie', 'Custo Total (R$)', 'Quantidade Usada']]
            for item in data['expenses_by_plant_species']:
                plant_data.append([
                    item['cultivation_plant__plant_species__name'] or 'Não especificado',
                    f"{item['total_cost']:.2f}" if item['total_cost'] else '0.00',
                    f"{item['total_used']:.2f}" if item['total_used'] else '0.00'
                ])
            
            plant_table = Table(plant_data, colWidths=[250, 150, 150])
            plant_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            
            story.append(plant_table)
            story.append(Spacer(1, 30))
        
        # 4. Dados de Produção (se disponível)
        if 'production_data' in data and data['production_data']:
            story.append(Paragraph("4. Produção por Espécie", styles['Heading2']))
            
            production_data_table = [['Espécie', 'Quantidade Total', 'Unidade', 'Nº de Colheitas']]
            for item in data['production_data']:
                production_data_table.append([
                    item['cultivation_plant__plant_species__name'] or 'Não especificado',
                    str(item['total_quantity']),
                    item['unity'],
                    str(item['total_harvests'])
                ])
            
            production_table = Table(production_data_table, colWidths=[200, 120, 80, 100])
            production_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            
            story.append(production_table)
            story.append(Spacer(1, 30))
        
        # 5. Análise de Ponto de Equilíbrio (se disponível)
        if 'break_even_analysis' in data:
            story.append(Paragraph("5. Análise de Ponto de Equilíbrio", styles['Heading2']))
            
            be_data = data['break_even_analysis']
            be_table_data = [
                ['Item', 'Valor'],
                ['Gastos com Insumos', f"R$ {be_data['input_expenses']:.2f}"],
                ['Outros Gastos', f"R$ {be_data['other_expenses']:.2f}"],
                ['Custo Total', f"R$ {be_data['total_costs']:.2f}"],
                ['Preço Médio de Venda', f"R$ {be_data['avg_selling_price']:.2f}"],
                ['Unidades para Break-even', f"{be_data['break_even_units']:.0f}"],
                ['Unidades Produzidas', f"{be_data['actual_units']:.0f}"],
                ['Resultado Financeiro', f"R$ {be_data['profitability']:.2f}"],
                ['Situação', 'Lucrativo' if be_data['is_profitable'] else 'Prejuízo']
            ]
            
            be_table = Table(be_table_data, colWidths=[250, 150])
            be_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            
            story.append(be_table)
        
        # Rodapé
        story.append(Spacer(1, 40))
        story.append(Paragraph(f"Relatório gerado em {timezone.now().strftime('%d/%m/%Y %H:%M')}", 
                             styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        
        buffer.seek(0)
        
        # Criar resposta
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"relatorio_{site_name}_{start_date.strftime('%Y%m')}_{end_date.strftime('%Y%m')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    def generate_excel_report(self, data, start_date, end_date, site_name):
        """
        Gera um relatório em Excel
        """
        wb = Workbook()
        
        # Sheet 1: Resumo
        ws1 = wb.active
        ws1.title = "Resumo"
        
        ws1['A1'] = f"Relatório Financeiro - {site_name}"
        ws1['A2'] = f"Período: {data['period']}"
        
        # Adicionar dados ao Excel...
        # (implementação similar ao PDF, mas formatada para Excel)
        
        # Salvar para buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"relatorio_{site_name}_{start_date.strftime('%Y%m')}_{end_date.strftime('%Y%m')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    def generate_csv_report(self, data, start_date, end_date, site_name):
        """
        Gera um relatório em CSV
        """
        response = HttpResponse(content_type='text/csv')
        filename = f"relatorio_{site_name}_{start_date.strftime('%Y%m')}_{end_date.strftime('%Y%m')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response, delimiter=';')
        
        # Escrever cabeçalhos e dados...
        writer.writerow(['Relatório Financeiro', site_name])
        writer.writerow(['Período', data['period']])
        writer.writerow([])
        
        # Gastos por categoria
        writer.writerow(['Gastos por Categoria'])
        writer.writerow(['Categoria', 'Total (R$)', 'Nº de Gastos'])
        for item in data['expenses_by_category']:
            writer.writerow([item['category__name'], item['total'], item['count']])
        
        return response