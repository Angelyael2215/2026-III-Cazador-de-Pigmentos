from django.shortcuts import render

# Create your views here.
# Ejemplo de la lógica de respuesta para la vista del mapa
def obtener_estado_mapa(usuario):
    perfil = usuario.perfil
    niveles_completados = perfil.sesiones.filter(completado=True).values_list('nivel_id', flat=True)
    
    mapa_data = []
    modulos = ModuloTeorico.objects.prefetch_related('niveles').all().order_by('orden')
    
    for modulo in modulos:
        datos_modulo = {
            "id": modulo.id,
            "titulo": modulo.titulo,
            "niveles": []
        }
        for nivel in modulo.niveles.all():
            estado = "completado" if nivel.id in niveles_completados else "bloqueado"
            # Lógica extra: Si el nivel anterior está completado, este pasa a "disponible"
            
            datos_modulo["niveles"].append({
                "id": nivel.id,
                "titulo": nivel.titulo,
                "mecanica": nivel.tipo_mecanica,
                "estado": estado
            })
        mapa_data.append(datos_modulo)
        
    return mapa_data
