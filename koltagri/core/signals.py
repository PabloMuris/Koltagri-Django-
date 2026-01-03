from django.db.models.signals import post_save
from django.dispatch import receiver
from koltagri.tasks.models import Task,TaskCompletion

from koltagri.landplots.models import SiteMembership

from koltagri.landplots.models import Site




@receiver(post_save, sender=Task)
def create_task_completions_for_site(sender, instance, created, **kwargs):
    if not created:
        return

    site = instance.site
    users = site.members.all()  

    completions = [
        TaskCompletion(task=instance, user=user)
        for user in users
    ]

    TaskCompletion.objects.bulk_create(completions)