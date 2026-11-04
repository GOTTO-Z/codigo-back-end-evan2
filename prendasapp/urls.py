from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_pagina, name= 'login_pagina'),
    path('prendas/', views.inicio, name= 'inicio'),
    path('logout/', views.logout_vista, name='logout'),
    path('api/prendas/', views.PrendaApiView.as_view(), name='api_prendas'),
    path('api/prendas/<int:id>/', views.PrendaDetalleApiView.as_view(), name='api_prenda_detalle'),

    path('crear/', views.crear_prenda, name= "crear_prenda"),
    path('detalle/<int:id>/', views.detalle_prenda, name='detalle_prenda'),
    path('editar/<int:id>/', views.editar_prenda, name='editar_prenda'),
    path('eliminar/<int:id>/', views.eliminar_prenda, name='eliminar_prenda'),

    path('api/login/', views.LoginApiView.as_view(), name='login_api'),
]