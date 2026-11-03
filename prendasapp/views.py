from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .models import Prenda
# Create your views here.

def inicio(request):
    prendas = Prenda.objects.all()

    return render(request, 'prendasapp/inicio.html') 

def crear_prenda(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        disponible = 'disponible' in request.POST

        imagen = request.FILES.get('imagen')

        Prenda.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            disponible=disponible,
            imagen=imagen
        )
        return redirect('inicio')
    return render(request, 'prendasapp/crear.html')

def detalle_prenda(request, id):
    prenda = Prenda.objects.get(id=id)
    return render(request, 'prendasapp/detalle.html', {
        'prenda': prenda
    })

def editar_prenda(request, id):
    prenda = Prenda.objects.get(id=id)
    if request.method == 'POST':
        prenda.nombre = request.POST['nombre']
        prenda.descripcion = request.POST['descripcion']
        prenda.disponible = 'disponible' in request.POST

        
        if 'imagen' in request.FILES:
            prenda.imagen = request.FILES['imagen']
        
        prenda.save()
        
        return redirect('inicio')
    return render(request, 'prendasapp/editar.html', {
        'prenda': prenda
    })

def eliminar_prenda(request, id):
    prenda = Prenda.objects.get(id=id)
    if request.method == 'POST':
        prenda.delete()
        return redirect('inicio')
    return render(request, 'prendasapp/eliminar.html', {
        'prenda': prenda
    })

def login_pagina(request):
    return render(request, 'prendasapp/login.html')

class LoginApiView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        #recibir las crendenciales desde JSON
        username = request.data.get('username')
        password = request.data.get('password')

        # Validar credenciales

        usuario = authenticate(
            username=username, 
            password=password
        )

        # Si el usuario y la constraseña son correctos

        if usuario is not None:

            token, creado = Token.objects.get_or_create(
                user=usuario
            )

            return Response({
                'mensaje':'Autenticacion Correcta',
                'usuario':usuario.username,
                'token':token.key
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Usuario o contraseña incorrectos'
        }, status=status.HTTP_401_UNAUTHORIZED)


class PrendaApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # GET: listar de las prendas
    def get(self, request):

        prendas = Prenda.objects.all()

        datos = []

        for prenda in prendas:
            datos.append({
                'id': prenda.id,
                'nombre': prenda.nombre,
                'descripcion': prenda.descripcion,
                'imagen': str(prenda.imagen) if prenda.imagen else None,
                'disponible': prenda.disponible
            })

        return Response(datos, status=status.HTTP_200_OK)


    #POST Crear nueva Prenda

    def post(self, request):

        #Recibir los datos enviados desde el cliente

        nombre = request.data.get('nombre')
        descripcion= request.data.get('descripcion')
        imagen = request.FILES.get('imagen') or request.data.get('imagen')
        disponible = request.data.get('disponible', False)

        #Validar que los campos

        if not nombre or not nombre.strip() or not descripcion or not descripcion.strip() or not imagen:
            return Response({
                'error': 'Los campos nombre, descripción e imagen son obligatorios.'
            }, status=status.HTTP_400_BAD_REQUEST)


        #Crear y guardar en la BD

        prenda = Prenda.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            imagen=imagen,
            disponible=disponible
        )

        # devolver

        return Response({
            'mensaje': 'Prenda creada correctamente',
            'prenda':{
                'id':prenda.id, 
                'nombre': prenda.nombre,
                'descripcion': prenda.descripcion,
                'imagen': str(prenda.imagen) if prenda.imagen else None,
                'disponible': prenda.disponible
            }
        }, status=status.HTTP_201_CREATED)
