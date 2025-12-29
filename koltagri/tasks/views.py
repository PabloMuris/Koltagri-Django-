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

from koltagri.person.mixins import SiteOwnerRequiredMixin,SiteManagerRequiredMixin

from .models import Task


# Create your views here.

class TaskTemplateView(ListView):
    template_name = "tasks/tasks.html"
    context_object_name = "tasks"
    model = Task


class TaskDetailTemplateView(DetailView):
    template_name = "tasks/tasks_detail.html"
    context_object_name = "task_d"
    model = Task  

class TaskboardTemplateView(ListView):
    template_name = "tasks/task_board.html"
    context_object_name = "task_d"
    model = Task 

class TaskCreateUpdateView(LoginRequiredMixin, View):
    template_name = "tasks/task_form.html"
    
    def get(self, request, pk=None):
        if pk:
            task = get_object_or_404(Task, pk=pk)
            form = TaskForm(instance=task)
        else:
            form = TaskForm()
        
        return render(request, self.template_name, {
            'form': form,
            'is_edit': bool(pk),
            'task_id': pk,
        })
    
    def post(self, request, pk=None):
        if pk:
            task = get_object_or_404(Task, id=pk)
            form = TaskForm(request.POST, instance=task)
        else:
            form = TaskForm(request.POST)

            print(request.POST)
        
        if form.is_valid():
            task = form.save(commit=False)
            
            if not pk:
                task.created_by = request.user
            
            task.updated_by = request.user
            
            task.save()
            
            
            return redirect('tasks')
        
        # Se o form não for válido
        return render(request, self.template_name, {
            'form': form,
            'is_edit': bool(pk),
            'task_id': pk,
        })
class TaskParticipantTemplateView(TemplateView):
    template_name = "tasks/task_team.html"

class TaskDocsTemplateView(TemplateView):
    template_name = "tasks/task_detail_docs.html"



    
@login_required
async def fetch_plant_species(request):
    q = request.GET.get("q", "").strip()

    qs = PlantSpecies.objects.all().values("id", "name")

    if q:
        qs = qs.filter(name__icontains=q)

    
    qs = qs[:20]

    species = await sync_to_async(list)(qs)

    return JsonResponse(species, safe=False)

