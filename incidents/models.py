from django.db import models
import json


class knowledge(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    summary = models.TextField()
    label = models.CharField(max_length=100)

    def __str__(self):
        return str(self.timestamp) + ': ' + self.label
