from django.urls import path, include

urlpatterns = [
    path('', include('ya.api.urls')),
]
