from sspagri_back.landplots.models import Task,CultivationPlant,Cultivation,Site
task = CultivationPlant.objects.get(id=1)
print(task)

print(task[0].uuid)

#dabb0b52-753b-4d2f-aeba-5568c33eb887


#e5fcf0af-a7da-4082-bd5e-004caab7d20a