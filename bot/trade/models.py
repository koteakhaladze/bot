from django.db import models


class Message(models.Model):
    ticket = models.CharField(max_length=50)
    action = models.CharField(max_length=50)
    message = models.CharField(max_length=500)
    result = models.CharField(max_length=500, blank=True)
    result_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Messages'
        ordering = ['result_at']
