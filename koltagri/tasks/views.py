from django.shortcuts import render,get_list_or_404,get_object_or_404
from django.http import FileResponse, Http404
from django.views.generic import ListView,TemplateView,View,DetailView
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from asgiref.sync import sync_to_async
from django_filters.views import FilterView

import mimetypes


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

from koltagri.person.mixins import SiteOwnerRequiredMixin,SiteManagerRequiredMixin

from .models import Task,TaskCompletion,Attachment

from django.contrib.auth import get_user_model

from django.core.exceptions import PermissionDenied

User = get_user_model()

from django.http import HttpResponseNotAllowed
# Create your views here.

class TaskTemplateView(LoginRequiredMixin, FilterView):
    template_name = "tasks/tasks.html"
    context_object_name = "tasks"
    model = Task
    paginate_by = 3
    filterset_fields = {
        "name": ["icontains"],
        "due_date": ["gte", "lte"],
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

        return context

class TaskboardTemplateView(ListView):
    template_name = "tasks/task_board.html"
    context_object_name = "task_d"
    model = Task 

class TaskCreateUpdateView(LoginRequiredMixin, View):
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

class TaskParticipantTemplateView(LoginRequiredMixin, ListView):
    template_name = "tasks/task_team.html"
    context_object_name = "participants"
    model = SiteMembership

    def get_queryset(self):  
        site_id = self.request.session.get("selected_site_location")
        site = get_object_or_404(Site, id=site_id)
        return (
            SiteMembership.objects
            .filter(site=site)
            
        )
    


class TaskDocsTemplateView(TemplateView):
    template_name = "tasks/task_detail_docs.html"


class TaskAttachmentsTemplateView(LoginRequiredMixin, FilterView):
    template_name = "tasks/task_attachments.html"
    model = Attachment
    context_object_name = "attachments"
    filterset_fields = ["name"]
    paginate_by = 1

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
        return super().dispatch(request, *args, **kwargs)
    

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