from django.db import models
import datetime
from django.utils.timezone import now

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    permission = models.CharField(max_length=20, default="admin")
    def __str__(self):
        return self.name

class City(models.Model):
    id = models.AutoField(primary_key=True)
    states = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    title = models.CharField(max_length=100)

class Race(models.Model):
    id = models.AutoField(primary_key=True)
    city_id = models.IntegerField(default=1)
    date = models.DateField(default=now)
    number = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    length = models.IntegerField(default=0)
    level = models.CharField(max_length=100)
    money = models.CharField(max_length=100)
    splits = models.CharField(max_length=50)

class Race_Data(models.Model):
    id = models.AutoField(primary_key=True)
    race_id = models.IntegerField(default=1)
    box = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    trainer = models.CharField(max_length=100)
    time = models.FloatField(default=0.0)
    margin = models.FloatField(default=0.0)
    split = models.FloatField(default=0.0)
    in_run = models.IntegerField(default=0)
    weight = models.FloatField(default=0.0)
    sire = models.CharField(max_length=100)
    dam = models.CharField(max_length=100)
    sp = models.FloatField(default=0.0)










