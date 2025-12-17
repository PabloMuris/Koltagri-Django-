from django.shortcuts import render,get_list_or_404,get_object_or_404
from django.views.generic import ListView,TemplateView,View,DetailView
from rest_framework.views import APIView
from django.http import JsonResponse
from asgiref.sync import sync_to_async

from koltagri.landplots.models import PlantSpecies
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

from .models import Task


# Create your views here.

class TaskTemplateView(ListView):
    template_name = "tasks.html"
    context_object_name = "tasks"
    model = Task


class TaskDetailTemplateView(DetailView):
    template_name = "tasks_detail.html"
    context_object_name = "task_d"
    model = Task  

class TaskboardTemplateView(ListView):
    template_name = "task_board.html"
    context_object_name = "task_d"
    model = Task 

class TaskCreateUpdateView(LoginRequiredMixin, View):
    template_name = "task_form.html"
    
    def get(self, request, pk=None):
        if pk:
            task = get_object_or_404(Task, pk=pk)
            form = TaskForm(instance=task)
        else:
            # Criação nova
            form = TaskForm()
        
        return render(request, self.template_name, {
            'form': form,
            'is_edit': bool(pk),
            'task_id': pk,
        })
    
    def post(self, request, pk=None):
        # Se tiver pk, está editando uma tarefa existente
        if pk:
            task = get_object_or_404(Task, pk=pk)
            form = TaskForm(request.POST, instance=task)
        else:
            # Criação nova
            form = TaskForm(request.POST)
        
        if form.is_valid():
            # Salva a tarefa
            task = form.save()
            
            # 1. Processa NOVOS anexos (uploads)
            uploaded_files = request.FILES.getlist('attachments')
            for uploaded_file in uploaded_files:
                # Pega nome customizado se existir
                file_name = uploaded_file.name
                attachment_type = request.POST.get('attachment_type', 'task')
                
                # Cria attachment manualmente
                Attachment.objects.create(
                    task=task,
                    file=uploaded_file,
                    name=file_name,
                    type=attachment_type
                )
            
            # 2. Processa anexos para deletar (checkboxes)
            delete_attachments = request.POST.getlist('delete_attachment')
            if delete_attachments:
                Attachment.objects.filter(id__in=delete_attachments).delete()
            
            return redirect('tasks')
        
        # Se o form não for válido, renderiza novamente com erros
        attachments = task.attachments.all() if pk else []
        return render(request, self.template_name, {
            'form': form,
            'attachments': attachments,
            'is_edit': bool(pk),
            'task_id': pk,
        })
class TaskParticipantTemplateView(TemplateView):
    template_name = "task_team.html"

class TaskDocsTemplateView(TemplateView):
    template_name = "task_detail_docs.html"


class TaskPlantApiView(APIView):
    def get(self, request, *args, **kwargs):
        tasks = Task.objects.all().values("id", "title", "description", "status", "due_date")
        return render(request, 'tasks.html', {'tasks': tasks})
    
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
async def fetch_inputs(request):
    q = request.GET.get("q", "").strip()

    qs = AgriculturalInputs.objects.all().values("id", "name")

    if q:
        qs = qs.filter(name__icontains=q)

    
    qs = qs[:20]

    supplies = await sync_to_async(list)(qs)

    return JsonResponse(supplies, safe=False)