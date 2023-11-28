from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import BuildingData
from django.contrib.auth.models import Group

def building_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name = 'Building')
        instance.groups.add(group)
        BuildingData.objects.create(
            user = instance,
        )

post_save.connect(building_profile, sender = User)