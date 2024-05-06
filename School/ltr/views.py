from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView, UserModel
from .form import UserForm, PasswordChangingForm, CustomCreationForm
from django.urls import reverse_lazy

from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.db import transaction
from django.urls import reverse
#################################################################################################
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from . models import Nivel, Curso, Tipocontacto, Area, Subarea, Ticket, Seguimiento, Estadoticket, ResponsableSubareaNivel, ResponsableSuperior, CoordinadorCiclo, Personas, ProfesorResponsable, Asignatura, ProfesorJefe, TipoRespuestaColegio, Mensaje
from django.views.generic import ListView, DetailView
from django.core.serializers import serialize
from datetime import date, timedelta, datetime
from django.contrib.auth.models import User


#################################################################################################
# Create your views here.
#########################
class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    #form_class = PasswordChangeForm
    success_url = reverse_lazy('password-success')

def password_success(request):
    return render(request, 'registration/password_success.html')    

def envia_correo(request):
    # remitente
    remitente = 'bienestar@colegiolaabadia.cl'
    password = 'Abadia2024'

    # remitente = 'negocio.paulo@gmail.com'
    # password = 'paulo_2106'

    # datos destinatario
    destinatario = 'pvalenzuela@coaniquem.org'

    # crear el mensaje
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Ejemplo de formulario por mail"

    # Contenido del mensaje
    cuerpo = """
    Hola .
    
    Por favor, responde este correo unicamente presionando el link a continuación:
    <a href="http://127.0.0.1:8000/formulario_respuesta">Responder al formulario</a>

    Gracias.
    """
    mensaje.attach(MIMEText(cuerpo, "html"))

    # Configurar el servidor SMTP
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.starttls()
    smtp.login(remitente, password)

    # Enviar el Mensaje
    smtp.sendmail(remitente, destinatario, mensaje.as_string())

    # Cerrar la conexión SMTP
    smtp.quit()

# def obtener_destinatarios_unicos(responsables):
#     # Recolecta IDs de Persona de los responsables
#     persona_ids = {responsable.persona.id for responsable in responsables}
#     # Retorna una lista de direcciones de correo, asegurando que no hay duplicados
#     return Personas.objects.filter(id__in=persona_ids).values_list('correo', flat=True).distinct()

def obtener_destinatarios_unicos(responsables):
    # Recolecta IDs de Persona de los responsables
    persona_ids = {responsable.persona.id for responsable in responsables}
    # Retorna objetos de Personas asegurando que no hay duplicados
    return Personas.objects.filter(id__in=persona_ids).distinct()    

def obtener_destinatarios_ticket(ticket_id):
    # Retorna lista de correos de destino únicos y destinatario principal

    ticket = get_object_or_404(Ticket, id=ticket_id)
    nivel = get_object_or_404(Nivel, id=ticket.nivel.id)
    subarea = get_object_or_404(Subarea, id=ticket.subarea.id)
    asignatura = get_object_or_404(Asignatura, id=ticket.asignatura.id)

    responsableprofesor = ProfesorResponsable.objects.filter(
        asignatura=ticket.asignatura, nivel=ticket.nivel)
    responsablessubareanivel = ResponsableSubareaNivel.objects.filter(
        subarea=ticket.subarea, nivel=ticket.nivel)
    coordinadorciclo = CoordinadorCiclo.objects.filter(ciclo=nivel.ciclo)
    responsablesuperior = ResponsableSuperior.objects.filter(
        subarea=ticket.subarea)

    if subarea.profejefe:
        profesorjefe = ProfesorJefe.objects.filter(
            nivel=ticket.nivel, curso=ticket.curso)
        # Unir todos los responsables en una lista
        if asignatura.id > 1:
            todos_responsables = list(responsableprofesor) + list(responsablessubareanivel) + list(
                coordinadorciclo) + list(responsablesuperior) + list(profesorjefe)
        else:
            todos_responsables = list(responsablessubareanivel) + list(
                coordinadorciclo) + list(responsablesuperior) + list(profesorjefe)
    else:
        # Unir todos los responsables en una lista
        if asignatura.id > 1:
            todos_responsables = list(responsableprofesor) + list(
                responsablessubareanivel) + list(coordinadorciclo) + list(responsablesuperior)
        else:
            todos_responsables = list(
                responsablessubareanivel) + list(coordinadorciclo) + list(responsablesuperior)

        # Obtener todos los destinatarios sin duplicados
    

    lista_destinatarios = obtener_destinatarios_unicos(todos_responsables)

   
    if asignatura.id > 1:
        # Primer Destinatario es el Profesor
        for responsable in responsableprofesor:
            persona = get_object_or_404(Personas, id=responsable.persona.id)
            # destinatario_correo = persona.nombre
            # cargo = persona.cargo
    else:
        # Si Destinatrario correo no ha sido asignado antes
        for responsable in responsablessubareanivel:
            persona = get_object_or_404(Personas, id=responsable.persona.id)
            # destinatario_correo = persona.nombre
            # cargo = persona.cargo

    return (lista_destinatarios, persona)


@transaction.atomic
def envio_correo_colegio(request,to_adr,ticket,mensaje,destinatario_correo,asunto,message,ticketnuevo):
    ############################
    # Envia Correo al Colegio  #
    ############################
    try:

        template = get_template('correo_colegio.html')
        content = template.render({
            'destinatario': destinatario_correo,
            'ticket': ticket,
            'mensaje': mensaje,
            'message': message,
            'ticketnuevo': ticketnuevo,
        })

        mail = EmailMultiAlternatives(
            subject=asunto,
            body='',
            from_email=settings.EMAIL_HOST_USER,
            to=to_adr
        )
        mail.attach_alternative(content, 'text/html')
        mail.send()

        return True


    except Exception as e:
        print(f"Error: {e}")
        return False
        


def envia_primer_correo_colegio(request):
    ###########################################################
    #           PRIMER ENVIO DE CORREO AL COLEGIO             #
    # Prepara los datos para llamar a la función envio_correo #
    ###########################################################
        
    # Prepara los datos para llamar al envio_correo_colegio

    ticket = Ticket.objects.get(id=request.POST.get('idticket'))
    nuevo_estado = get_object_or_404(Estadoticket, id=2)
    user = get_object_or_404(User, username='bridge')
    area = ticket.subarea.area.nombre

    personas_destinatarias, principal = obtener_destinatarios_ticket(ticket.id)

    to_adr = [persona.correo for persona in personas_destinatarias]

    asunto = ticket.tipocontacto.nombre+' - '+ticket.subarea.nombre+' - '+ticket.nombre+' '+ticket.apellido

    # asunto='Nuevo Caso en Sistema de Bienestar'
    emisor = 'bienestar@colegiolaabadia.cl'
    message = f"De: {emisor}\n Para: {principal.correo}\n Asunto: {asunto}\n Mensaje: {ticket.motivo}"
    try:
        # Crea Mensaje
        nuevo_mensaje = Mensaje.objects.create(
            ticket=ticket,
            correoemisor=emisor,
            correodestino=principal.correo,
            respondido=0,
            asunto=asunto,
            message=message,
            persona=principal
        )
        # Actualiza Ticket
        fec = datetime.today()
        ticket.fechaprimerenvio = fec
        ticket.estadoticket = nuevo_estado
        ticket.fechahoracambioestado = fec
        ticket.save()

        # Crea Seguimiento
        Seguimiento.objects.create(
            ticket=ticket,
            comentario=f'se deriva caso al área {area}',
            user=user,
            fechahora=fec
        )

        envio = envio_correo_colegio(
            request,
            to_adr,
            ticket,
            nuevo_mensaje,
            principal,
            asunto,
            message,
            1
        )
        if not envio:
            contexto = {
            'texto': 'Ha ocurrido un error en el envío del Mensaje, revise la casilla de bienestar@abadia.cl'
            }
            return render(request, 'correo_enviado.html', contexto)


    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return redirect(f'/{ticket.id}')


def pruebacorreo(request):
    # botón desde Descripción para envío de correo
    ticket = Ticket.objects.get(id=request.POST.get('idticket'))
    print(ticket)
   # envio_correo_colegio(ticket.id)
    return render(request, 'exito.html')


def formulariorespuesta_colegio(request, ticket_id, mensaje_id):
    ##############################################################################
    #               L I N K    CORREO COLEGIO                                    #
    # Vista que se presenta luego de presionar el Link en el correo del Colegio  #
    # desde aquí se dará respuesta al Apoderado al presionar el botón ENVIAR     # 
    ##############################################################################
    template_name = "formulario_respuesta_colegio.html"

    ticket = get_object_or_404(Ticket, id=ticket_id)
    mensaje = get_object_or_404(Mensaje,id = mensaje_id)

    try:
        mensaje_respondido = Mensaje.objects.get(mensajerespondidoid=mensaje.id)
    except Mensaje.DoesNotExist:
        mensaje_respondido = None

    # Validar que correo no haya sido respondido
    if mensaje.respondido == 1:
        # mensaje ya fue respondido
        contexto = {
            'mensaje': mensaje_respondido,
        }
       
        return render(request, 'correo_respondido.html', contexto)
        
    
    tiporespuesta = TipoRespuestaColegio.objects.all().order_by('id')

    # Obtener todos los destinatarios sin duplicados, en este caso el principal es el Apoderado (no se usa)
    personas_destinatarios,principal = obtener_destinatarios_ticket(ticket.id)

    contexto = {
        'ticket': ticket,
        'mensaje': mensaje,
        'destinatarios': personas_destinatarios,
        'tiporespuestas': tiporespuesta,

    }
    return render(request, template_name, context=contexto)


@transaction.atomic
def envio_correo_apoderado(request,to_adr, subject, message, persona_firma, ticket, mensaje):
    #############################
    # Envío Correo al Apoderado #
    #############################
    try:
        # ticket = get_object_or_404(Ticket, id=ticket_id)
        # mensaje = get_object_or_404(Mensaje, id=mensaje_id)
        #persona = get_object_or_404(Personas, id=firma_id)

        template = get_template('correo_apoderado.html')
        content = template.render({
            'ticket': ticket,
            'mensaje': mensaje,
            'persona': persona_firma,
            'texto': message,
        })

        mail = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=settings.EMAIL_HOST_USER,
            to=to_adr
        )
        mail.attach_alternative(content, 'text/html')
        mail.send()
        
        return True

        
    except Exception as e:
        print(f"Error: {e}")
        return False
        

def formulariorespuesta_apoderado(request, ticket_id, mensaje_id):
    ###############################################################################
    # Vista que se presenta luego de presionar el Link en el correo del Apoderado #
    # desde aquí se dará respuesta al Colegio una vez presione el botón ENVIAR    # 
    ###############################################################################
    template_name = "formulario_respuesta_apoderado.html"

    ticket = get_object_or_404(Ticket, id=ticket_id)
    mensaje = get_object_or_404(Mensaje,id = mensaje_id)

    contexto = {
        'ticket': ticket,
        'mensaje': mensaje,
        
    }
    return render(request, template_name, context=contexto)


def respuesta_colegio(request):
    ##############################################################################################
    # Aquí viene la Respuesta del Colegio desde el formulario: formulario_respuesta_colegio.html #
    # Se preparan los datos para enviar correo al Apoderado                                      #
    ##############################################################################################
    if request.method == 'POST':
       
        idticket = request.POST['idticket']
        tiporespuesta = request.POST['tiporespuesta']
        respuesta = request.POST['motivo']
        emisor = request.POST['emisor']
        currentmensaje = request.POST['idmensaje']

        try:
            # Lee datos del ticket
            ticket = get_object_or_404(Ticket,id = idticket)

            # Actualiza estado del mensaje anterior como Respondido
            mensaje = get_object_or_404(Mensaje, id=currentmensaje)
            mensaje.respondido = 1
            mensaje.save()

            fechahoracambioestado = datetime.today()
          
            if tiporespuesta == '1':
                # da respuesta al Apoderado
                opcion = 4
                estadoticket = Estadoticket.objects.get(id=opcion)
                if ticket.estadoticket_id == 2:
                    # guardar fecha y hora de primera respuesta del colegio
                    ticket.fechaprimerarespuesta = fechahoracambioestado

                ticket.fechahoracambioestado = fechahoracambioestado
                ticket.estadoticket_id = estadoticket.id
                ticket.save()

            if tiporespuesta == '2':
                # se mantiene el caso del lado del Colegio
                opcion = 3
                estadoticket = Estadoticket.objects.get(id=opcion)

                # if ticket.estadoticket_id == 2:
                #     # guardar fecha y hora de primera respuesta del colegio (estado=2)
                #     ticket.fechaprimerarespuesta = fechahoracambioestado

                ticket.fechahoracambioestado = fechahoracambioestado
                ticket.estadoticket_id = estadoticket.id
                ticket.save()

            # crea seguimiento con datos de respuesta del colegio al apoderado
            user = get_object_or_404(User, username='bridge')
            personaemisor = get_object_or_404(Personas, id=emisor)

            motivo = personaemisor.nombre+' , (' + personaemisor.correo+'), Mensaje : ' + respuesta

            Seguimiento.objects.create(
                ticket=ticket,
                comentario=motivo,
                user=user)

            # Crear registro modelo:Mensaje
            lista_destinatarios, principal = obtener_destinatarios_ticket(ticket.id)
            destinatarios_str = [persona.correo for persona in lista_destinatarios]
            destinatarios_str.insert(0, ticket.correo)

            correos_formateados = ', '.join(destinatarios_str)  # Formatea la lista a un string separado por comas
            message = f"De: {personaemisor.correo}\nPara: {correos_formateados}\nAsunto: {mensaje.asunto}\nMensaje: {respuesta}"
            #message = f"De: {personaemisor.correo}\n Para: {destinatarios_str}\n Asunto: {mensaje.asunto}\n Mensaje: {respuesta}"

            nuevo_mensaje = Mensaje.objects.create(
                ticket=ticket,
                correoemisor=personaemisor.correo,
                correodestino=ticket.correo,
                respondido=0,
                asunto=mensaje.asunto,
                message=message,
                persona=personaemisor,
                mensajerespondidoid=mensaje.id
            )

            # enviar correo de respuesta al Apoderado cc a todos los involucrados
            
            envio = envio_correo_apoderado(
                request,
                destinatarios_str,
                mensaje.asunto,
                respuesta,
                personaemisor,
                ticket,
                nuevo_mensaje
            )

            if envio:
                contexto = {
                    'texto': 'Se enviará una copia a su correo.'
                    }
                return render(request,'correo_enviado.html',contexto)
            else:
                contexto = {
                    'texto': 'Ha ocurrido un error en el envío del Correo, verifique la casilla, sino intente nuevamente'
                }
                return render(request,'correo_enviado.html',contexto)

        except Exception as e:
            #print(f"Error: {e}")
            contexto = {
                'texto': 'Ha ocurrido un error con el envío del Mensaje, por favor vuelva a intentarlo.'
                }
            return render(request,'correo_enviado.html',contexto)
    else:
        # Redireccionar o mostrar un error si se accede al método incorrecto
        contexto = {
            'texto': 'No es posible ingresar a este formulario. Contacte al administrador'
                }
        return render(request,'correo_enviado.html',contexto)


def respuesta_apoderado(request):
    ##################################################################################################
    # Aquí viene la Respuesta del Apoderado desde el formulario: formulario_respuesta_apoderado.html #
    # Se preparan los datos para enviar respuesta al Colegio                                         #
    ##################################################################################################
    if request.method == 'POST':
        idticket = request.POST['idticket']
        respuesta = request.POST['motivo']
        currentmensaje = request.POST['idmensaje']

        print ('idticket ', idticket)
        print ('respuesta ',respuesta)
        print ('currentmensaje ', currentmensaje)

        try:
            # Lee datos del ticket
            ticket = get_object_or_404(Ticket,id = idticket)

            # Actualiza estado del mensaje anterior como Respondido
            mensaje = get_object_or_404(Mensaje, id=currentmensaje)
            mensaje.respondido = 1
            mensaje.save()

            # crea seguimiento con datos de respuesta del colegio al apoderado
            user = get_object_or_404(User, username='bridge')
            #personaemisor = get_object_or_404(Personas, id=emisor)

            motivo = ticket.nombre+' '+ticket.apellido+' , (' + ticket.correo+'), Mensaje : ' + respuesta

            Seguimiento.objects.create(
                ticket=ticket,
                comentario=motivo,
                user=user)

            # Crear registro modelo:Mensaje
            lista_destinatarios, principal = obtener_destinatarios_ticket(ticket.id)
            destinatarios_str = [persona.correo for persona in lista_destinatarios]
            #destinatarios_str.insert(0, ticket.correo)

            correos_formateados = ', '.join(destinatarios_str)  # Formatea la lista a un string separado por comas
            message = f"De: {mensaje.correodestino}\nPara: {correos_formateados}\nAsunto: {mensaje.asunto}\nMensaje: {respuesta}"

            nuevo_mensaje = Mensaje.objects.create(
                ticket=ticket,
                correoemisor=mensaje.correodestino,
                correodestino=mensaje.correoemisor,
                respondido=0,
                asunto=mensaje.asunto,
                message=message,
                persona=mensaje.persona,
                mensajerespondidoid=mensaje.id
            )

            # enviar correo de respuesta al Apoderado cc a todos los involucrados

            #request,to_adr,ticket,mensaje,destinatario_correo,asunto,message,ticketnuevo
            envio = envio_correo_colegio(
                request,
                destinatarios_str,
                ticket,
                nuevo_mensaje,  
                mensaje.persona,
                mensaje.asunto,
                respuesta,
                0
                
            )

            if envio:
                contexto = {
                    'texto': 'Le responderemos a la brevedad'
                    }
                return render(request,'correo_enviado.html',contexto)
            else:
                contexto = {
                    'texto': 'Ha ocurrido un error en el envío del Correo, verifique la casilla, sino intente nuevamente'
                }
                return render(request,'correo_enviado.html',contexto)



        except Exception as e:
            print(f"Error: {e}")
            contexto = {
                'texto': 'Ha ocurrido un error con el envío del Mensaje, por favor vuelva a intentarlo.'
                }
            return render(request,'correo_enviado.html',contexto)
    else:
        # Redireccionar o mostrar un error si se accede al método incorrecto
        contexto = {
            'texto': 'No es posible ingresar a este formulario,contacte al Administrador.'
                }
        return render(request,'correo_enviado.html',contexto)

def enviacorreoalapoderado(request):
    # Envío correo de respuesta al Apoderado
    ticket = Ticket.objects.get(id=request.POST.get('idticket'))

    print(ticket)
    envio_correo_apoderado(ticket.id)
    return redirect(f'/{ticket.id}')


def registroticket(request):
    # Registro Ticket Colegio Abadía Id=1
    ' Colegio 1'
    colegio_id = 1  # ID del Colegio 1
    niveles = Nivel.objects.filter(
        ciclo__colegio_id=colegio_id).order_by('orden')
    cursos = Curso.objects.filter(colegio_id=colegio_id).order_by('orden')
    tipocontactos = Tipocontacto.objects.filter(colegio_id=colegio_id)
    # areas = Area.objects.filter(colegio_id = colegio_id)
    subareas = Subarea.objects.filter(
        area__colegio_id=colegio_id).order_by('area')
    asignatura = Asignatura.objects.filter(
        colegio_id=colegio_id).order_by('orden')

    template_name = "formulario_ticket.html"
    contexto = {
        'niveles': niveles,
        'cursos': cursos,
        'tipocontactos': tipocontactos,
        'subareas': subareas,
        'asignaturas': asignatura,

    }
    return render(request, template_name, contexto)


def cargar_subareas(request):
    areaid = request.GET.get('area_id')
    # print(areaid)
    subareas = Subarea.objects.filter(area_id=areaid).order_by('nombre')
    list_subareas = list(subareas.values('id', 'nombre'))
    # print (list_subareas)
    return JsonResponse(list_subareas, safe=False)


def creaticket(request):
    if request.method == 'POST':
        estadoticket = get_object_or_404(Estadoticket, id=1)
        nombre = request.POST['nombre']
        apellidos = request.POST['apellidos']
        email = request.POST['email']
        fono = request.POST['fono']
        nombrealumno = request.POST['nombrealumno']
        apellidosalumno = request.POST['apellidosalumno']
        nivel = request.POST['nivel']
        curso = request.POST['curso']
        tipocontacto = request.POST['tipocontacto']
        subarea = request.POST['subarea']
        motivo = request.POST['motivo']
        asignaturaid = request.POST['asignatura']
        fechahoracambioestado = datetime.now()
        Ticket.objects.create(nombre=nombre, apellido=apellidos, correo=email, telefono=fono, tipocontacto_id=tipocontacto, subarea_id=subarea, motivo=motivo, estadoticket=estadoticket,
                              fechahoracambioestado=fechahoracambioestado, nombrealumno=nombrealumno, apellidoalumno=apellidosalumno, nivel_id=nivel, curso_id=curso, asignatura_id=asignaturaid)

    return redirect('/registroticket')

@login_required
def index(request):
    return render(request, "index.html")

class Index(LoginRequiredMixin,DetailView):

    template_name = 'mainticket.html'

    def get(self, request, *args, **kwargs):
        colegio_id = 1  # ID del Colegio 1

        nuevos = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=1).order_by('fechacreacion').reverse()
        respuestas = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=2).order_by('fechacreacion').reverse()
        acciones = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=3).order_by('fechacreacion').reverse()
        cerrados = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=4).order_by('fechacreacion').reverse()

        contexto = {
            'nuevos': nuevos,
            'respuestas': respuestas,
            'acciones': acciones,
            'cerrados': cerrados,
        }
        return render(request, self.template_name, contexto)


class VisorTicket(DetailView):

    template_name = 'visorticket.html'

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')
        ticket = Ticket.objects.get(id=pk)
        tespera = date.today() - ticket.fechacreacion.date()
        diastotalespera = tespera.days
        tcambioestado = date.today() - ticket.fechahoracambioestado.date()
        dias_de_cambio_estado = str(tcambioestado.days)  # Días de diferencia
        nivel = get_object_or_404(Nivel, id=ticket.nivel.id)
        responsablessubareanivel = ResponsableSubareaNivel.objects.filter(
            subarea=ticket.subarea, nivel=ticket.nivel)
        coordinadorciclo = CoordinadorCiclo.objects.filter(ciclo=nivel.ciclo)
        responsablesuperior = ResponsableSuperior.objects.filter(
            subarea=ticket.subarea)

        personaresponsable = Personas.objects.filter(
            id__in=[r.persona.id for r in responsablessubareanivel]).first()
        personaciclo = Personas.objects.filter(
            id__in=[r.persona.id for r in coordinadorciclo]).first()
        personasuperior = Personas.objects.filter(
            id__in=[r.persona.id for r in responsablesuperior]).first()

        contexto = {
            'ticket': ticket,
            'diastotalespera': diastotalespera,
            'diascambioestado': dias_de_cambio_estado,
            'segs': Seguimiento.objects.filter(ticket=pk),
            'estados': Estadoticket.objects.all(),
            # 'trx': self.model2.objects.filter(pk=pk),
            'encabezado': 'Visor de Ticket',
            'responsablearea': personaresponsable,
            'responsableciclo': personaciclo,
            'responsablesuperrior': personasuperior,
        }
        return render(request, self.template_name, contexto)

@login_required
def guardacomentario(request):

    # print (request.POST)
    comentario = request.POST['comentario']
    user_str = request.POST['userid']
    idticket_str = request.POST['idticket']

    cambiar_estado = 'cbox1' in request.POST

    crear_tarea = request.POST.get('cbox2', False)
    activar_correo = request.POST.get('cbox3', False)

    user = get_object_or_404(User, username='bridge')
    # user = get_object_or_404(User, id=user_str)

    idticket = get_object_or_404(Ticket, id=idticket_str)
    estado_actual = idticket.estadoticket.nombre

    if comentario:
        seg = Seguimiento.objects.create(
            ticket=idticket, comentario=comentario, user=user)

    if cambiar_estado:
        estado_id = request.POST.get('estadoTicket', None)
        if estado_id:
            # Aquí puedes hacer algo con el estado_id, por ejemplo, actualizar el estado del ticket
            fechahoracambioestado = date.today()
            ticket = Ticket.objects.get(id=request.POST.get('idticket'))
            ticket.estadoticket_id = estado_id
            ticket.fechahoracambioestado = fechahoracambioestado
            ticket.save()

            nuevo_estado = ticket.estadoticket.nombre

            seg = Seguimiento.objects.create(
                ticket=idticket, comentario=f'{user} Cambio de estado {estado_actual} a {nuevo_estado}', user=user)

            return redirect(f'/{idticket_str}')

    if crear_tarea == '2':
        # llamar a la vistra para crear tarea
        return render(request, 'ltr/index.html')

    if activar_correo == '3':
        # grabar dato que permite activar envio de correos
        return render(request, 'ltr/index.html')

    return redirect(f'/{idticket_str}')

@login_required
def zanex(request):
    return render(request, 'ltr/index.html')


def ejemplo_correo(request):
    return render(request, 'ejemplo_correo.html')

def Logout(_request):
    return render(_request,'registration/login.html')

def es_admin(user):
    return user.groups.filter(name='Administrador').exists()

@method_decorator(user_passes_test(es_admin), name='dispatch')
class Listausuarios(LoginRequiredMixin, ListView):
    model = User
    template_name = 'userslist.html'

    def get_queryset(self):

        return self.model.objects.exclude(username = 'root').order_by('first_name')

    def get(self, request, *args, **kwargs):

        contexto = {
            'usuarios': self.get_queryset(),
            'encabezado': 'Listado de Usuarios',
            'menu': 'Usuarios',
            'submenu': 'Configuración / Usuarios',
            'titulo': 'Usuarios'
        }
        return render(request, self.template_name, contexto)

def Registrouser(request):
    data = {
        'form': CustomCreationForm()
    }

    if request.method == 'POST':
        formulario = CustomCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            # messages.success(request,'Usuario creado exitosamente!')
            return redirect(to="list-users")
        data["form"] = formulario

    return render(request, 'registration/registro.html', data)

def edituser(request, pk):
    usuario = User.objects.get(id=pk)
    template_name = 'registration/edit_user.html'
    data = {
        'form': UserForm(instance=usuario)
    }
    #form = UserForm(instance=usuario)

    if request.method == 'POST':
        formulario = UserForm(data=request.POST, instance=usuario)

        if formulario.is_valid():
            formulario.save()
            return redirect('list-users')
        else:
            data = {
                'form': UserForm(instance=usuario),
                'msg': 'Ha ocurrido en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)    
############################################ < xanex > ############################################


def about(request):
    return render(request, 'ltr/about.html')


def accordion(request):
    return render(request, 'ltr/accordion.html')


def alerts(request):
    return render(request, 'alerts.html')


def avatarradius(request):
    return render(request, 'ltr/avatarradius.html')


def avatarround(request):
    return render(request, 'ltr/avatarround.html')


def avatarsquare(request):
    return render(request, 'ltr/avatarsquare.html')


def badge(request):
    return render(request, 'ltr/badge.html')


def blog(request):
    return render(request, 'ltr/blog.html')


def breadcrumbs(request):
    return render(request, 'ltr/breadcrumbs.html')


def buttons(request):
    return render(request, 'buttons.html')


def calendar(request):
    return render(request, 'ltr/calendar.html')


def calendar2(request):
    return render(request, 'ltr/calendar2.html')


def cards(request):
    return render(request, 'ltr/cards.html')


def carousel(request):
    return render(request, 'ltr/carousel.html')


def cart(request):
    return render(request, 'ltr/cart.html')


def chart(request):
    return render(request, 'chart.html')


def chartchartist(request):
    return render(request, 'chartchartist.html')


def chartdonut(request):
    return render(request, 'chartdonut.html')


def chartechart(request):
    return render(request, 'chartechart.html')


def chartflot(request):
    return render(request, 'chartflot.html')


def chartline(request):
    return render(request, 'chartline.html')


def chartmorris(request):
    return render(request, 'chartmorris.html')


def chartnvd3(request):
    return render(request, 'chartnvd3.html')


def chartpie(request):
    return render(request, 'chartpie.html')


def charts(request):
    return render(request, 'charts.html')


def chat(request):
    return render(request, 'chat.html')


def checkout(request):
    return render(request, 'checkout.html')


def colors(request):
    return render(request, 'ltr/colors.html')


def construction(request):
    return render(request, 'ltr/construction.html')


def counters(request):
    return render(request, 'ltr/counters.html')


def cryptocurrencies(request):
    return render(request, 'ltr/cryptocurrencies.html')


def datatable(request):
    return render(request, 'ltr/datatable.html')


def dropdown(request):
    return render(request, 'ltr/dropdown.html')


def editprofile(request):
    return render(request, 'ltr/editprofile.html')


def email(request):
    return render(request, 'ltr/email.html')


def emailservices(request):
    return render(request, 'ltr/emailservices.html')


def empty(request):
    return render(request, 'ltr/empty.html')


def error400(request):
    return render(request, 'ltr/error400.html')


def error401(request):
    return render(request, 'ltr/error401.html')


def error403(request):
    return render(request, 'ltr/error403.html')


def error404(request):
    return render(request, 'ltr/error404.html')


def error500(request):
    return render(request, 'ltr/error500.html')


def error503(request):
    return render(request, 'ltr/error503.html')


def faq(request):
    return render(request, 'ltr/faq.html')


def footers(request):
    return render(request, 'ltr/footers.html')


def forgotpassword(request):
    return render(request, 'ltr/forgotpassword.html')


def formadvanced(request):
    return render(request, 'ltr/formadvanced.html')


def formelements(request):
    return render(request, 'ltr/formelements.html')


def formvalidation(request):
    return render(request, 'ltr/formvalidation.html')


def formwizard(request):
    return render(request, 'ltr/formwizard.html')


def gallery(request):
    return render(request, 'ltr/gallery.html')


def headers(request):
    return render(request, 'ltr/headers.html')


def icons(request):
    return render(request, 'ltr/icons.html')


def icons2(request):
    return render(request, 'ltr/icons2.html')


def icons3(request):
    return render(request, 'ltr/icons3.html')


def icons4(request):
    return render(request, 'ltr/icons4.html')


def icons5(request):
    return render(request, 'ltr/icons5.html')


def icons6(request):
    return render(request, 'ltr/icons6.html')


def icons7(request):
    return render(request, 'ltr/icons7.html')


def icons8(request):
    return render(request, 'ltr/icons8.html')


def icons9(request):
    return render(request, 'ltr/icons9.html')


def icons10(request):
    return render(request, 'ltr/icons10.html')


def invoice(request):
    return render(request, 'ltr/invoice.html')


def listas(request):
    return render(request, 'ltr/list.html')


def loaders(request):
    return render(request, 'ltr/loaders.html')


def lockscreen(request):
    return render(request, 'ltr/lockscreen.html')


# def login(request):
#     return render(request, 'ltr/login.html')


def maps(request):
    return render(request, 'ltr/maps.html')


def maps1(request):
    return render(request, 'ltr/maps1.html')


def maps2(request):
    return render(request, 'ltr/maps2.html')


def mediaobject(request):
    return render(request, 'ltr/mediaobject.html')


def modal(request):
    return render(request, 'ltr/modal.html')


def navigation(request):
    return render(request, 'ltr/navigation.html')


def notify(request):
    return render(request, 'ltr/notify.html')


def pagination(request):
    return render(request, 'ltr/pagination.html')


def panels(request):
    return render(request, 'ltr/panels.html')


def pricing(request):
    return render(request, 'ltr/pricing.html')


def profile(request):
    return render(request, 'ltr/profile.html')


def progress(request):
    return render(request, 'ltr/progress.html')


def rangeslider(request):
    return render(request, 'ltr/rangeslider.html')


def rating(request):
    return render(request, 'ltr/rating.html')


def register(request):
    return render(request, 'ltr/register.html')


def scroll(request):
    return render(request, 'ltr/scroll.html')


def search(request):
    return render(request, 'ltr/search.html')


def services(request):
    return render(request, 'ltr/services.html')


def shop(request):
    return render(request, 'ltr/shop.html')


def shopdescription(request):
    return render(request, 'ltr/shopdescription.html')


def sweetalert(request):
    return render(request, 'ltr/sweetalert.html')


def tables(request):
    return render(request, 'ltr/tables.html')


def tabs(request):
    return render(request, 'ltr/tabs.html')


def tags(request):
    return render(request, 'ltr/tags.html')


def terms(request):
    return render(request, 'ltr/terms.html')


def thumbnails(request):
    return render(request, 'ltr/thumbnails.html')


def timeline(request):
    return render(request, 'ltr/timeline.html')


def tooltipandpopover(request):
    return render(request, 'ltr/tooltipandpopover.html')


def treeview(request):
    return render(request, 'ltr/treeview.html')


def typography(request):
    return render(request, 'ltr/typography.html')


def userslist(request):
    return render(request, 'ltr/userslist.html')


def widgets(request):
    return render(request, 'ltr/widgets.html')


def wishlist(request):
    return render(request, 'ltr/wishlist.html')


def wysiwyag(request):
    return render(request, 'ltr/wysiwyag.html')
