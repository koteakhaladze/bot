from django.db import models


class Message(models.Model):
    ticket = models.CharField(max_length=50)
    action = models.CharField(max_length=50)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
