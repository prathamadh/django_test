from django.db import models

# Create your models here.


class UserInteraction(models.Model):
    user_id = models.CharField(max_length=50)
    product_id = models.CharField(max_length=50)
    action = models.CharField(max_length=20, choices=[('view', 'View'), ('click', 'Click'), ('buy', 'Buy')])

    def __str__(self):
        return f"{self.user_id} - {self.product_id} - {self.action}"
