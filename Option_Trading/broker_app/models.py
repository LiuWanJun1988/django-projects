from django.db import models

# Create your models here.
class Account(models.Model):
    user_id = models.CharField(max_length=50)
    sure_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    permission = models.IntegerField(default=2)
    status = models.CharField(max_length=20, default='enable')
    expire_date = models.DateField()
    ib_user_name = models.CharField(max_length=20, default='some string')
    ib_id = models.IntegerField()
    ib_port = models.IntegerField()
    saxo_token = models.TextField()


class Security(models.Model):
    user_id = models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    expire_date = models.DateField()
    symbols = models.TextField()
    data_size = models.IntegerField(default=250)





