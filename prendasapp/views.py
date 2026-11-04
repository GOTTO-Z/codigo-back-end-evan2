from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .models import Prenda


def validar_prenda(nombre, descripcion, imagen=None, imagen_obligatoria=False):
    errores = []
    nombre = (nombre or '').strip()
    descripcion = (descripcion or '').strip()

    if not nombre:
        errores.append('La prenda no puede estar sin nombre.')
    elif len(nombre) < 3:
        errores.append('El mínimo son 3 caracteres.')
    elif len(nombre) > 100:
        errores.append('El nombre no puede superar los 100 caracteres.')

    if not descripcion:
        errores.append('La descripción es obligatoria.')
    elif len(descripcion) < 5:
        errores.append('Debe tener un mínimo de 5 caracteres.')

    if imagen_obligatoria and not imagen:
        errores.append('La imagen es obligatoria.')
    elif imagen and not imagen.content_type.startswith('image/'):
        errores.append('Solo se puede subir una imagen como archivo.')

    return errores


def prenda_a_dict(prenda):
    return {
        'id': prenda.id,
        'nombre': prenda.nombre,
        'descripcion': prenda.descripcion,
        'imagen': str(prenda.imagen) if prenda.imagen else None,
        'disponible': prenda.disponible
    }


def a_booleano(valor):
    if isinstance(valor, bool):
        return valor
    return str(valor).lower() in ('true', '1', 'on', 'si', 'sí')



@login_required
def inicio(request):
    prendas = Prenda.objects.all()
    return render(request, 'prendasapp/inicio.html', {
        'prendas': prendas
    })


@login_required
def crear_prenda(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        disponible = 'disponible' in request.POST
        imagen = request.FILES.get('imagen')

        errores = validar_prenda(nombre, descripcion, imagen)
        if errores:
            return render(request, 'prendasapp/crear.html', {
                'errores': errores,
                'datos': request.POST
            })

        Prenda.objects.create(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            disponible=disponible,
            imagen=imagen
        )
        return redirect('inicio')
    return render(request, 'prendasapp/crear.html')


@login_required
def detalle_prenda(request, id):
    prenda = get_object_or_404(Prenda, id=id)
    return render(request, 'prendasapp/detalle.html', {
        'prenda': prenda
    })


@login_required
def editar_prenda(request, id):
    prenda = get_object_or_404(Prenda, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        imagen = request.FILES.get('imagen')

        errores = validar_prenda(nombre, descripcion, imagen, imagen_obligatoria=True)
        if errores:
            return render(request, 'prendasapp/editar.html', {
                'prenda': prenda,
                'errores': errores
            })

        prenda.nombre = nombre.strip()
        prenda.descripcion = descripcion.strip()
        prenda.disponible = 'disponible' in request.POST
        if imagen:
            prenda.imagen = imagen
        prenda.save()
        return redirect('inicio')
    return render(request, 'prendasapp/editar.html', {
        'prenda': prenda
    })


@login_required
def eliminar_prenda(request, id):
    prenda = get_object_or_404(Prenda, id=id)
    if request.method == 'POST':
        prenda.delete()
        return redirect('inicio')
    return render(request, 'prendasapp/eliminar.html', {
        'prenda': prenda
    })


def login_pagina(request):
    return render(request, 'prendasapp/login.html')


def logout_vista(request):
    logout(request)
    return redirect('login_pagina')




class LoginApiView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        
        username = request.data.get('username')
        password = request.data.get('password')

        
        usuario = authenticate(username=username, password=password)

        if usuario is not None:
            
            login(request._request, usuario)

            
            token, creado = Token.objects.get_or_create(user=usuario)

            return Response({
                'mensaje': 'Autenticación correcta',
                'usuario': usuario.username,
                'token': token.key
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Usuario o contraseña incorrectos'
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutApiView(APIView):
    """
    Vista de API para cerrar sesión destruyendo el token del usuario.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Elimina el token del usuario actual para invalidar la sesión
            request.user.auth_token.delete()
            return Response({
                'mensaje': 'Sesión cerrada correctamente (Token eliminado).'
            }, status=status.HTTP_200_OK)
        except AttributeError:
            return Response({
                'error': 'El usuario no tiene un token activo.'
            }, status=status.HTTP_400_BAD_REQUEST)

class PrendaApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        datos = [prenda_a_dict(p) for p in Prenda.objects.all()]
        return Response(datos, status=status.HTTP_200_OK)

    
    def post(self, request):
        nombre = request.data.get('nombre')
        descripcion = request.data.get('descripcion')
        imagen = request.FILES.get('imagen')
        disponible = a_booleano(request.data.get('disponible', False))

        errores = validar_prenda(nombre, descripcion, imagen)
        if not imagen:
            errores.append('La imagen es obligatoria.')
        if errores:
            return Response({'errores': errores},
                            status=status.HTTP_400_BAD_REQUEST)

        prenda = Prenda.objects.create(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            imagen=imagen,
            disponible=disponible
        )
        return Response({
            'mensaje': 'Prenda creada correctamente',
            'prenda': prenda_a_dict(prenda)
        }, status=status.HTTP_201_CREATED)


class PrendaDetalleApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def obtener(self, id):
        try:
            return Prenda.objects.get(id=id)
        except Prenda.DoesNotExist:
            return None

    
    def get(self, request, id):
        prenda = self.obtener(id)
        if prenda is None:
            return Response({'error': 'La prenda no existe.'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(prenda_a_dict(prenda), status=status.HTTP_200_OK)

    
    def put(self, request, id):
        prenda = self.obtener(id)
        if prenda is None:
            return Response({'error': 'La prenda no existe.'},
                            status=status.HTTP_404_NOT_FOUND)

        nombre = request.data.get('nombre')
        descripcion = request.data.get('descripcion')
        imagen = request.FILES.get('imagen')

        errores = validar_prenda(nombre, descripcion, imagen)
        if errores:
            return Response({'errores': errores},
                            status=status.HTTP_400_BAD_REQUEST)

        prenda.nombre = nombre.strip()
        prenda.descripcion = descripcion.strip()
        if 'disponible' in request.data:
            prenda.disponible = a_booleano(request.data.get('disponible'))
        if imagen:
            prenda.imagen = imagen
        prenda.save()

        return Response({
            'mensaje': 'Prenda actualizada correctamente',
            'prenda': prenda_a_dict(prenda)
        }, status=status.HTTP_200_OK)

    
    def delete(self, request, id):
        prenda = self.obtener(id)
        if prenda is None:
            return Response({'error': 'La prenda no existe.'},
                            status=status.HTTP_404_NOT_FOUND)
        prenda.delete()
        return Response({'mensaje': 'Prenda eliminada correctamente'},
                        status=status.HTTP_200_OK)