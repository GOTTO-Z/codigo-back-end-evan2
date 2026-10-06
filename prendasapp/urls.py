from django.urls import path
from . import views


urlpatterns = [
    path('', views.inicio, name= 'inicio'),
    path('crear/', views.crear_prenda, name= "crear_prenda"),
    path('detalle/<int:id>/', views.detalle_prenda, name='detalle_prenda'),
    path('editar/<int:id>/', views.editar_prenda, name='editar_prenda'),
    path('eliminar/<int:id>/', views.eliminar_prenda, name='eliminar_prenda')
]