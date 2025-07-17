from ..models import Cultivation,Task
from rest_framework import serializers



class CreateUpdateTaskSerializer(serializers.ModelSerializer):
    cultivation = serializers.SlugRelatedField(
        many=True,
        queryset=Cultivation.objects.filter(site=user__site_membership__site),
        slug_field='uuid',
        required= False,
    )

    class Meta:
        model = Task
        fields = [
            'id', 'uuid','name', 'description',
            'cultivation', 'start_in', 'end_in',
            'created_at', 'updated_at',
        ]

    def validate(self, data):
        start = data.get('start_in')
        end = data.get('end_in')
        if start and end and end < start:
            raise serializers.ValidationError({
            'end_in': 'A data de término não pode ser anterior ao início.'
            })
        
        cultivation = data.get('cultivation')
        return data
    
    def create(self, validated_data):
        cultivations = validated_data.pop('cultivation', None)
        task = Task.objects.create(**validated_data)
        task.cultivation.set(cultivations)
        return task
    
    def update(self, instance, validated_data):
        cultivations = validated_data.pop('cultivation', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if cultivations is not None:
            instance.cultivation.set(cultivations)
        return instance