from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('add_activity/', views.add_activity, name='add_activity'),  # No date parameter
    path('add_activity/<str:date>/', views.add_activity, name='add_activity_with_date'),  # With date parameter
]
