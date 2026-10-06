from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Prenda

# Create your views here.

def inicio(request):
    prendas = Prenda.objects.all()
    return render(request, 'prendasapp/inicio.html', {
        'prendas': prendas
    })

def crear_prenda(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        disponible = 'disponible' in request.POST

        imagen = request.FILES.get['imagen']

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