from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.

class Accounts(models.Model):
    UserName = models.CharField(max_length = 20)
    Password = models.CharField(max_length = 20)
    Account_No = models.IntegerField(primary_key = True)
    Customer_Name = models.CharField(max_length = 20)
    Curr_Balance = models.IntegerField()
    email = models.EmailField(max_length = 100, default = 'user@lenzbank.com')

def __str__(self):
    return self.UserName

