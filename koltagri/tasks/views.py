from django.shortcuts import render
from django.views.generic import ListView,TemplateView,View
from rest_framework.views import APIView
from django.http import JsonResponse
from asgiref.sync import sync_to_async

from koltagri.landplots.models import PlantSpecies
from koltagri.business.models import AgriculturalInputs
from .forms import TaskForm, AttachmentFormSet
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required



from .models import Task

# Create your views here.

class TaskTemplateView(ListView):
    template_name = "tasks.html"
    context_object_name = "tasks"
    model = Task


class TaskDetailTemplateView(ListView):
    template_name = "tasks_detail.html"
    context_object_name = "task_d"
    model = Task  

class TaskboardTemplateView(ListView):
    template_name = "task_board.html"
    context_object_name = "task_d"
    model = Task 

class TaskCreateUpdateView(SingleObjectMixin, FormView):
    template_name = "task_form.html"
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task_list")  # ajuste para sua URL

    def get_object(self):
        """
        Se tiver pk => edita, senão cria novo.
        """
        pk = self.kwargs.get("pk")
        if pk:
            return Task.objects.get(pk=pk)
        return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.form_class(instance=self.object)
        formset = AttachmentFormSet(instance=self.object)

        return self.render_to_response({
            "form": form,
            "formset": formset,
            "is_edit": self.object is not None,
        })

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.form_class(request.POST, instance=self.object)
        formset = AttachmentFormSet(
            request.POST, request.FILES, instance=self.object
        )

        if form.is_valid() and formset.is_valid():
            task = form.save()
            formset.instance = task
            formset.save()
            return redirect(self.success_url)

        return self.render_to_response({
            "form": form,
            "formset": formset,
            "is_edit": self.object is not None,
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

    species = await sync_to_async(list)(qs)

    return JsonResponse(species, safe=False)