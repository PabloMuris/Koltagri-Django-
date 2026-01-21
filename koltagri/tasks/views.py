from django.shortcuts import render,get_list_or_404,get_object_or_404
from django.http import FileResponse, Http404,HttpResponseForbidden
from django.views.generic import ListView,TemplateView,View,DetailView
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from asgiref.sync import sync_to_async
from django_filters.views import FilterView
from django.views.decorators.http import require_POST


import mimetypes


from django.db.models import Q


from koltagri.landplots.models import CultivationPlant, PlantSpecies,Site,SiteMembership
from koltagri.business.models import AgriculturalInputs
from .forms import TaskForm
from .models import Attachment
import os
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

from koltagri.person.mixins import SiteOwnerRequiredMixin,SiteManagerRequiredMixin,SiteTeamRequiredMixin
from .models import Task,TaskCompletion,Attachment

from django.contrib.auth import get_user_model

from django.core.exceptions import PermissionDenied

User = get_user_model()

from django.utils import timezone
from django.urls import reverse
from django.db.models import Min, Max
from datetime import timedelta


from django.http import HttpResponseNotAllowed
# Create your views here.

from koltagri.core.mixins import IsManagerMixin, IsStaffMixin,IsManagerOrTechnicalAssistanceMixin 

class TaskTemplateView(LoginRequiredMixin, FilterView):
    template_name = "tasks/tasks.html"
    context_object_name = "tasks"
    model = Task
    paginate_by = 3
    filterset_fields = {
        "name": ["icontains"],
        "due_date": ["gte",'exact', "lte"],
        "is_completed": ["exact"],
    }

    def get_queryset(self):
        site_id = self.request.session.get("selected_site_location")

        if not site_id:
            return Task.objects.none() 

        return (
            super()
            .get_queryset()
            .filter(site=site_id)
        )
    
    def get_context_data(self, **kwargs):

        
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        start_of_week = today - timedelta(days=today.weekday())  # monday
        end_of_week = start_of_week + timedelta(days=6)
        prev_week_start = start_of_week - timedelta(days=7)
        prev_week_end = start_of_week - timedelta(days=1)
        next_week_start = end_of_week + timedelta(days=1)
        next_week_end = end_of_week + timedelta(days=7)

        extremes = Task.objects.aggregate(min_date=Min('due_date'), max_date=Max('due_date'))
        min_date = extremes['min_date']
        max_date = extremes['max_date']

        context['preset_urls'] = {
            'today': f"?due_date__gte={today}&due_date__lte={today}",
            'last_week_until_today': f"?due_date__gte={prev_week_start}&due_date__lte={today}",
            'today_until_next_week': f"?due_date__gte={today}&due_date__lte={next_week_end}",
            'before_prev_week_until_extreme': f"?due_date__lte={prev_week_end}&due_date__gte={min_date if min_date else ''}",
            'next_week_until_extreme': f"?due_date__gte={next_week_start}&due_date__lte={max_date if max_date else ''}",
        }

        return context

class TaskDetailTemplateView(DetailView):
    template_name = "tasks/tasks_detail.html"
    context_object_name = "task_d"
    model = Task
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["task_id"] = self.kwargs.get("pk")

        task_completion = TaskCompletion.objects.filter(task=self.object, user=self.request.user).first()
        is_completed = task_completion.is_completed if task_completion else False
        context["is_completed"] = is_completed
        
        task_owner = Task.objects.filter(user=self.request.user)
        if task_owner: 
            context['is_owner'] = True
        else:
            context['is_owner'] = False

        context['user'] = self.request.user
        
        return context

class TaskboardTemplateView(ListView):
    template_name = "tasks/task_board.html"
    context_object_name = "task_d"
    model = Task 

class TaskCreateUpdateView(IsManagerOrTechnicalAssistanceMixin, View):
    template_name = "tasks/task_form.html"
    
    def get(self, request, pk=None):
        plants = []

        if pk:
            task = get_object_or_404(Task, pk=pk)
            form = TaskForm(instance=task)

            species_qs = (
                PlantSpecies.objects
                    .filter(plantings__in=task.cultivation_plant.all())  # plantings = related_name do FK
                    .distinct()
                    .values('id', 'name')
            )

            plants = list(species_qs)  # já vem como [{'id':..., 'name':...}, ...]
        else:
            form = TaskForm()

        return render(request, self.template_name, {
            'form': form,
            'is_edit': bool(pk),
            'task_id': pk,
            'plants': plants,
        })
    def post(self, request, pk=None):
    # 1️⃣ Site vem da session (âncora do domínio)
        site_id = request.session.get("selected_site_location")
        if not site_id:
            raise PermissionDenied("Site não selecionado")

        site = get_object_or_404(
            Site,
            id=site_id,
            members=request.user
        )

        # 2️⃣ IDs das espécies vindos do form
        species_ids = [
            int(pid) for pid in request.POST.getlist("plants")
            if pid and pid.isdigit()
        ]

        # 3️⃣ Task (create/update)
        task = get_object_or_404(Task, id=pk) if pk else None
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            task = form.save(commit=False)

            if not pk:
                task.created_by = request.user

            task.updated_by = request.user
            task.site = site
            task.save()

            # 4️⃣ Resolver SOMENTE os plantios do site
            cultivation_plants = CultivationPlant.objects.filter(
                plant_species_id__in=species_ids,
                cultivation__site=site
            )

            # 5️⃣ Redefinir M2M com segurança
            task.cultivation_plant.set(cultivation_plants)

            return redirect("tasks")

        return render(request, self.template_name, {
            "form": form,
            "is_edit": bool(pk),
            "task_id": pk,
        })


class TaskParticipantTemplateView(LoginRequiredMixin, ListView):  # Alterado de FilterView para ListView
    template_name = "tasks/task_team.html"
    context_object_name = "participants"
    model = SiteMembership
    paginate_by = 10

    def get_queryset(self):
        site_id = self.request.session.get("selected_site_location")
        site = get_object_or_404(Site, id=site_id)
        
        # Obter o parâmetro de busca da requisição GET
        search_query = self.request.GET.get('search', '').strip()
        
        queryset = SiteMembership.objects.filter(site=site).select_related('user')
        
        # Aplicar filtro de busca se houver um termo
        if search_query:
            # Busca tanto no first_name quanto no last_name
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query)
            )
        
        return queryset.order_by('user__first_name', 'user__last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o termo de busca ao contexto para manter o campo preenchido
        context['search_query'] = self.request.GET.get('search', '')
        context['task_pk'] = self.kwargs.get('pk')
        return context

class TaskDocsTemplateView(TemplateView):
    template_name = "tasks/task_detail_docs.html"


class TaskAttachmentsTemplateView(LoginRequiredMixin, FilterView):
    template_name = "tasks/task_attachments.html"
    model = Attachment
    context_object_name = "attachments"
    filterset_fields = ["name"]
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, pk=self.kwargs.get("task_pk"))
        context["user"] = get_object_or_404(User, pk=self.kwargs.get("user_pk"))
        return context

    def get_queryset(self):

        user_pk = self.kwargs.get("user_pk")

        user = get_object_or_404(User, pk=user_pk)

        task_pk = self.kwargs.get("task_pk")

        task = get_object_or_404(Task, pk=task_pk)

        site = self.request.session.get("selected_site_location")

        queryset = super().get_queryset()
        return queryset.filter(task=task, user=user, task__site=site)

    def dispatch(self, request, *args, **kwargs):
        site = request.session.get("selected_site_location")

        if not site:
            return HttpResponseForbidden()

        is_task_owner = Task.objects.filter(
            user=request.user,
            site=site
        ).exists()

        is_site_member = SiteMembership.objects.filter(
            user=request.user,
            site=site
        ).exists()

        if is_task_owner or is_site_member:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()
@login_required
async def fetch_plant_species(request):
    q = request.GET.get("q", "").strip()

    qs = PlantSpecies.objects.all().values("id", "name")

    if q:
        qs = qs.filter(name__icontains=q)

    
    qs = qs[:20]

    species = await sync_to_async(list)(qs)

    return JsonResponse(species, safe=False)



@login_required
def conclude_task(request, pk):
    
    task = get_object_or_404(Task, pk=pk)
    task_completion = TaskCompletion.objects.filter(task=task, user=request.user).first()

    if task_completion.is_completed:
        task_completion.is_completed = False
    else:
        task_completion.is_completed = True
    task_completion.save()

    return redirect("task_detail", pk=pk)

class DownloadFileView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        attachment = get_object_or_404(Attachment, pk=pk)

        if not attachment.file:
            raise Http404("Arquivo não associado.")
        
        if not hasattr(attachment.file, "path"):
            raise Http404("Storage não suportado para download direto.")
        
        file_path = attachment.file.path
        if not os.path.exists(file_path):
            raise Http404("Arquivo não encontrado.")
        
        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)

        response = FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=filename,
        )
        if mime_type:
            response["Content-Type"] = mime_type

        return response
    

from django.db.models import Min, Max
from .filters import TaskFilter
from django.views.generic.list import ListView

class SimpleFilteringTasksView(LoginRequiredMixin, FilterView):
    template_name = "tasks/tasks_expanded.html"
    context_object_name = "tasks"
    model = Task
    paginate_by = 10
    filterset_class = TaskFilter  # Use o filtro customizado

    def get_queryset(self):
        site_id = self.request.session.get("selected_site_location")

        if not site_id:
            return Task.objects.none()

        queryset = Task.objects.filter(site=site_id)
        
        # Ordenação padrão: mais antigas primeiro
        queryset = queryset.order_by('due_date', 'created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar limites de datas para o frontend
        site_id = self.request.session.get("selected_site_location")
        if site_id:
            extremes = Task.objects.filter(site=site_id).aggregate(
                min_date=Min('due_date'), 
                max_date=Max('due_date')
            )
            context['min_date'] = extremes['min_date']
            context['max_date'] = extremes['max_date']
        
        return context
    


@login_required
@require_POST
def upload_task_attachment(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "Nenhum arquivo enviado"}, status=400)

    # 1. Usuário precisa fazer parte do site da tarefa
    if task.site and not request.user.site_memberships.filter(site=task.site).exists():
        return HttpResponseForbidden("Você não tem acesso a esta tarefa")

    # 2. Define o tipo do anexo
    if task.user.filter(id=request.user.id).exists():
        attachment_type = Attachment.TASK
    else:
        attachment_type = Attachment.COMPLETION

    attachment = Attachment.objects.create(
        task=task,
        file=file,
        name=file.name,
        type=attachment_type,
        user=request.user
    )

    return JsonResponse({
        "id": attachment.id,
        "name": attachment.name,
        "type": attachment.get_type_display(),
        "file_url": attachment.file.url,
    }, status=201)


class AttachmentForTasksView(SiteTeamRequiredMixin,FilterView):
    model = Attachment
    template_name = "tasks/task_attachments_task"
    context_object_name = 'attachments'