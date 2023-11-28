from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class BuildingData(models.Model):
    user = models.OneToOneField(User, null = True, blank = True, on_delete = models.CASCADE)
    location = models.CharField(max_length = 600, null = True)
    profilepic = models.ImageField(default = '/images/ProfileDefault.jpg', upload_to = 'images', null = True, blank = True)

    def __str__(self):
        return self.user.first_name

class Flat(models.Model):
    CATEGORIES = (
        ('1BHK', '1BHK'),
        ('2BHK', '2BHK'),
        ('2.5BHK', '2.5BHK'),
        ('3BHK', '3BHK'),
        ('4BHK+', '4BHK+'),
    )

    CLIMATEZONES = (
        ('Hot & Dry', 'Hot & Dry'),
        ('Composite', 'Composite'),
        ('Warm & Humid', 'Warm & Humid'),
        ('Temperate', 'Temperate'),
        ('Cold', 'Cold'),
    )

    STARS = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    )
    
    building = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, null = True)
    category = models.TextField(max_length = 200, choices = CATEGORIES, default = 'Choose BHK...', null = True)
    name = models.CharField(max_length = 200, null = True)
    area = models.IntegerField(default = 0, null = True)
    rooms = models.IntegerField(default = 0, null = True)
    occupants = models.IntegerField(default = 0, null = True)
    appliances = models.IntegerField(default = 0, null = True) 
    units = models.IntegerField(default = 0, null = True)
    billamt = models.IntegerField(default = 0, null = True)
    lastyr_units = models.CharField(max_length = 500, null = True)
    twoyrbfr_units = models.CharField(max_length = 500, null = True)
    threeyrbfr_units = models.CharField(max_length = 500, null = True)
    created_date = models.DateTimeField(default = timezone.now, null = True)
    append_date = models.DateTimeField(auto_now_add = True, null = True)

    def __str__(self):
        return self.name

class ApplianceData(models.Model):
    APPLIANCES = (
        ('Air Conditioner', 'Air Conditioner'),
        ('Computer', 'Computer'),
        ('LED', 'LED'),
        ('CFL', 'CFL'),
        ('Microwave', 'Microwave'),
        ('Washing Machine', 'Washing Machine'),
        ('Ceiling Fan', 'Ceiling Fan'),
        ('Refrigerator', 'Refrigerator'),
        ('Air Fryer', 'Air Fryer'),
        ('Chimney', 'Chimney'),
        ('Geyser', 'Geyser'),
        ('OTG', 'OTG'),
        ('Oven', 'Oven'),
        ('Electric Stove', 'Electric Stove'),
        ('BEV Charger', 'BEV Charger'),
        ('Television', 'Television'),
        ('Room Heater', 'Room Heater'),
        ('Electric Kettle', 'Electric Kettle'),
    )

    flat = models.ForeignKey(Flat, on_delete = models.CASCADE, null = True) 
    appltype = models.TextField(max_length = 200, choices = APPLIANCES, default = 'Appliance Type...', null = True)
    brand = models.CharField(max_length = 200, null = True)
    modelname = models.CharField(max_length = 500, null = True)
    rating = models.DecimalField(default = 0, max_digits = 10, decimal_places = 5, null = True)

    def __str__(self):
        return self.modelname
