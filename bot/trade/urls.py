from trade.views import message_create
from django.urls import path

app_name = 'trade'

urlpatterns = [
    path('create/', message_create, name='create')
]
