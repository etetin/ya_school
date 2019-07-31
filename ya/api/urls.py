from django.urls import path
from . import views

urlpatterns = [
    path('imports', views.imports),
    path('imports/<int:import_id>/citizens/<int:citizen_id>', views.import_change),
    path('imports/<int:import_id>/citizens', views.import_data),
]
