from django.utils.decorators import method_decorator
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, Avg, ExpressionWrapper, F, Func, DurationField,IntegerField, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth, Extract
from django.db import connection,transaction

from .form import UserForm, PasswordChangingForm, CustomCreationForm, PersonasForm, CiclosForm, ColegiosForm, NivelesForm, CursosForm,AreasForm, SubareasForm, TiporespuestacolegioForm, ResponsablesubareanivelForm, CoordinadorcicloForm, ProfesorjefeForm, ResponsableasignaturaForm, ResponsablesuperiorForm, AccesoColegioForm
from django.urls import reverse_lazy,reverse

from django.shortcuts import render, redirect, get_object_or_404

#################################################################################################
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import render

from django.template.loader import get_template

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.serializers import serialize

from django.http import HttpResponse, HttpResponseRedirect,JsonResponse

from . models import Nivel, Curso, Tipocontacto, Area, Subarea, Ticket, Seguimiento, Estadoticket, ResponsableSubareaNivel, ResponsableSuperior, CoordinadorCiclo, Personas, ProfesorResponsable, Asignatura, ProfesorJefe, TipoRespuestaColegio, Mensaje, Ciclos, Colegio, Motivocierre, AccesoColegio
from django.views.generic import ListView, DetailView
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView, UserModel, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test

from datetime import date, timedelta, datetime
#################################################################################################
# Create your views here.
#########################
class CustomLogoutView(LogoutView):
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        # Agrega tu lógica personalizada aquí
        current_user = request.user
        if current_user.is_authenticated:  # Asegúrate de que el usuario está autenticado
            accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
            if accesocolegio:
                accesocolegio.colegioactual = accesocolegio.colegiodefault
                accesocolegio.save()
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_next_page(self):
        return '/login'  # Especifica el nombre de la URL a la que deseas redirigir


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

    # ASIGNATURA
    # asignatura = get_object_or_404(Asignatura, id=ticket.asignatura.id)
    # responsableprofesor = ProfesorResponsable.objects.filter(asignatura=ticket.asignatura, nivel=ticket.nivel)

    profesorjefe = ProfesorJefe.objects.filter(nivel=ticket.nivel, curso=ticket.curso)
    responsablessubareanivel = ResponsableSubareaNivel.objects.filter(subarea=ticket.subarea, nivel=ticket.nivel)
    coordinadorciclo = CoordinadorCiclo.objects.filter(ciclo=nivel.ciclo)
    responsablesuperior = ResponsableSuperior.objects.filter(subarea=ticket.subarea)

    todos_responsables = list(responsablessubareanivel) + list(coordinadorciclo) + list(responsablesuperior)
    if subarea.profejefe:
        todos_responsables += list(profesorjefe)

    # if asignatura.id > 1:
    #     todos_responsables += list(responsableprofesor)

    # Lista de todos los destinatarios
    lista_destinatarios = obtener_destinatarios_unicos(todos_responsables)

    ## Define Persona a quien va dirigido el Correo
    persona = None  # Asegurarse de que persona está definida
    ## Primero busca si existe el responsable Subarea-Nivel
    for responsable in responsablessubareanivel:
        persona_obj = get_object_or_404(Personas, id=responsable.persona.id)
        if persona_obj:
            persona = persona_obj
            break  # Salir del bucle si se encuentra una persona

    if persona == None:
        for profjefe in profesorjefe:
            persona_obj = get_object_or_404(Personas, id = profjefe.persona.id)
            if persona_obj:
                persona = persona_obj
                break


    # if asignatura.id > 1:
    #     # Primer Destinatario es el Profesor
    #     for responsable in responsableprofesor:
    #         persona_obj = get_object_or_404(Personas, id=responsable.persona.id)
    #         if persona_obj:
    #             persona = persona_obj
    #             break  # Salir del bucle si se encuentra una persona

    # else:
    #     # Si Destinatrario correo no ha sido asignado antes
    #     for responsable in responsablessubareanivel:
    #         persona_obj = get_object_or_404(Personas, id=responsable.persona.id)
    #         if persona_obj:
    #             persona = persona_obj
    #             break  # Salir del bucle si se encuentra una persona

    return (lista_destinatarios, persona)

### función única para envío de correos ###
def enviar_correo(subject, message, to_adr, ticket,mensaje, ticketnuevo, destinatario_correo, persona_firma, from_email, destino):
    # destino = 1 (COLEGIO) = 2 (APODERADO)
    #######################################
    try:

        #print ('from_email --->', from_email)
        #print (subject, message, to_adr, ticket,mensaje, ticketnuevo, destinatario_correo, persona_firma, from_email, destino)
        
        email_config = settings.EMAIL_BACKENDS.get(from_email)
        print ('email_config -->', email_config)
        print ('destino -->', destino)
        colegio = Colegio.objects.get(id=ticket.id)
        logoprincipal = colegio.logoprincipal
        logofirma = colegio.logofirma

        if not email_config:
            raise ValueError(f"No se encontró la configuración de correo para '{from_email}'")
        
        if destino == 1:
            # correo al Colegio
            template = get_template('correo_colegio.html')
            content = template.render({
                'destinatario': destinatario_correo,
                'ticket': ticket,
                'mensaje': mensaje,
                'message': message,
                'ticketnuevo': ticketnuevo, # 0 o 1
                'logoprincipal': logoprincipal,
            })

        if destino == 2:
            # correo al apoderado
            template = get_template('correo_apoderado.html')
            content = template.render({
                'ticket': ticket,
                'mensaje': mensaje,
                'persona': persona_firma,
                'texto': message,
                'logoprincipal': logoprincipal,
                'logofirma': logofirma,
            })
    
        connection = get_connection(
            backend=email_config['EMAIL_BACKEND'],
            host=email_config['EMAIL_HOST'],
            port=email_config['EMAIL_PORT'],
            username=email_config['EMAIL_HOST_USER'],
            password=email_config['EMAIL_HOST_PASSWORD'],
            use_tls=email_config['EMAIL_USE_TLS']
        )

        #print ('to_adr -->', to_adr)

        mail = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=email_config['EMAIL_HOST_USER'],
            to=to_adr,
            connection=connection
        )
        mail.attach_alternative(content, 'text/html')
        mail.send()

        return True

    except Exception as e:
        print (e)
        return False

@login_required
@transaction.atomic
def envia_primer_correo_colegio(request):
    ###########################################################
    #           PRIMER ENVIO DE CORREO AL COLEGIO             #
    # Prepara los datos para llamar a la función envio_correo #
    ###########################################################

    # Prepara los datos para llamar al enviar_correo

    ticket = Ticket.objects.get(id=request.POST.get('idticket'))
    colegio = ticket.subarea.area.colegio
    #emisor = colegio.correo
    email_config = settings.EMAIL_BACKENDS.get(colegio.setting_name)

    #print ("email_config['EMAIL_HOST_USER'] --> ", email_config['EMAIL_HOST_USER'])

    user = get_object_or_404(User, username='bridge')
    area = ticket.subarea.area.nombre

    personas_destinatarias, principal = obtener_destinatarios_ticket(ticket.id)
   
    if principal == None:
        # Crea Seguimiento
        Seguimiento.objects.create(
            ticket=ticket,
            comentario='No fue posible enviar correo, falta definir Destinatario Principal.',
            user=user,
            fechahora=fec
        )

        return redirect(f'/{ticket.id}')
        
    to_adr = [persona.correo for persona in personas_destinatarias]

    asunto = ticket.tipocontacto.nombre+' - '+ticket.subarea.nombre+' - '+ticket.nombre+' '+ticket.apellido

    #emisor = 'bienestar@colegiolaabadia.cl'
    emisor = email_config['EMAIL_HOST_USER']
    #print ('envia_primer_correo_colegio: emisor -->', emisor)

    message = f"De: {emisor}\n Para: {principal.correo}\n Asunto: {asunto}\n Mensaje: {ticket.motivo}"
    try:
        # Crear Mensaje
        nuevo_mensaje = Mensaje.objects.create(
            ticket=ticket,
            correoemisor=emisor,
            correodestino=principal.correo,
            respondido=0,
            asunto=asunto,
            message=message,
            persona=principal
        )

        print ('nuevo_mensaje -->', nuevo_mensaje)

        # Envia Primer Correo al colegio
        envio = enviar_correo(
            asunto,
            message,
            to_adr,
            ticket,
            nuevo_mensaje,
            1,
            principal,
            [],
            colegio.setting_name,
            1
        )

        if not envio:
            return redirect(f'/{ticket.id}')

        # Actualiza Ticket
        nuevo_estado = get_object_or_404(Estadoticket, id=2)
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
        print ('colegio.setting_name -->', colegio.setting_name)


    except Exception as e:
        return redirect(f'/{ticket.id}')

    return redirect(f'/{ticket.id}')

def formulariorespuesta_colegio(request, ticket_id, mensaje_id):
    ##############################################################################
    #               L I N K    CORREO COLEGIO                                    #
    # Vista que se presenta luego de presionar el Link en el correo del Colegio  #
    # desde aquí se dará respuesta al Apoderado al presionar el botón ENVIAR     #
    ##############################################################################
    template_name = "formulario_respuesta_colegio.html"

    ticket = get_object_or_404(Ticket, id=ticket_id)
    mensaje = get_object_or_404(Mensaje,id = mensaje_id)
    colegio = get_object_or_404(Colegio, id = ticket.subarea.area.colegio.id)
    logoprincipal = colegio.logoprincipal
    logofirma = colegio.logofirma
    print (logoprincipal)

    try:
        mensaje_respondido = Mensaje.objects.get(mensajerespondidoid=mensaje.id)
    except Mensaje.DoesNotExist:
        mensaje_respondido = None

    # Validar que correo no haya sido respondido
    if mensaje.respondido == 1:
        # mensaje ya fue respondido
        contexto = {
            'mensaje': mensaje_respondido,
            'logoprincipal': logoprincipal,
            'logofirma':logofirma,
        }

        return render(request, 'correo_respondido.html', contexto)

    tiporespuesta = TipoRespuestaColegio.objects.all().order_by('id')
    # Obtener todos los destinatarios sin duplicados, en este caso el principal es el Apoderado (no se usa)
    personas_destinatarios,principal = obtener_destinatarios_ticket(ticket.id)
    # Crear una lista de IDs de personas_destinatarios
    ids_destinatarios = [p.id for p in personas_destinatarios]

    # Filtrar los objetos Personas con los IDs obtenidos
    destinatarios = Personas.objects.filter(id__in=ids_destinatarios)

    contexto = {
        'ticket': ticket,
        'mensaje': mensaje,
        'destinatarios': destinatarios,
        'tiporespuestas': tiporespuesta,
        'logoprincipal': logoprincipal,
        'logofirma':logofirma,

    }
    return render(request, template_name, context=contexto)


def formulariorespuesta_apoderado(request, ticket_id, mensaje_id):
    ###############################################################################
    # Vista que se presenta luego de presionar el Link en el correo del Apoderado #
    # desde aquí se dará respuesta al Colegio una vez presione el botón ENVIAR    #
    ###############################################################################
    template_name = "formulario_respuesta_apoderado.html"

    ticket = get_object_or_404(Ticket, id=ticket_id)
    mensaje = get_object_or_404(Mensaje,id = mensaje_id)
    colegio = get_object_or_404(Colegio, id = ticket.subarea.area.colegio.id)
    logoprincipal = colegio.logoprincipal

    contexto = {
        'ticket': ticket,
        'mensaje': mensaje,
        'logoprincipal': logoprincipal

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
            colegio = ticket.subarea.area.colegio
            logoprincipal = colegio.logoprincipal
            email_config = settings.EMAIL_BACKENDS.get(colegio.setting_name)

            # Actualiza estado del mensaje anterior como Respondido
            mensaje = get_object_or_404(Mensaje, id=currentmensaje)
            mensaje.respondido = 1
            mensaje.save()

            fechahoracambioestado = datetime.today()
            if tiporespuesta == '1':
                # da respuesta al Apoderado
                estado = 4
                estadoticket = Estadoticket.objects.get(id=estado)

                if ticket.estadoticket_id == 2:
                    # guardar fecha y hora de primera respuesta del colegio
                    ticket.fechaprimerarespuesta = fechahoracambioestado

            if tiporespuesta == '2':
                # se mantiene el caso del lado del Colegio
                estado = 3
                estadoticket = Estadoticket.objects.get(id=estado)

            if tiporespuesta == '3':
                estado=5
                estadoticket = Estadoticket.objects.get(id=estado)


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
            envio = enviar_correo(
                mensaje.asunto,
                respuesta,
                destinatarios_str,
                ticket,
                nuevo_mensaje,
                0,
                '',
                personaemisor,
                colegio.setting_name,
                2
            )

            # envio = envio_correo_apoderado(
            #     request,
            #     destinatarios_str,
            #     mensaje.asunto,
            #     respuesta,
            #     personaemisor,
            #     ticket,
            #     nuevo_mensaje
            # )

            if envio:
                contexto = {
                    'texto': 'Se enviará una copia a su correo.',
                    'logoprincipal': logoprincipal
                    }
                return render(request,'correo_enviado.html',contexto)
            else:
                contexto = {
                    'texto': 'Ha ocurrido un error en el envío del Correo, verifique la casilla, sino intente nuevamente',
                    'logoprincipal': logoprincipal
                }
                return render(request,'correo_enviado.html',contexto)

        except Exception as e:
            #print(f"Error: {e}")
            contexto = {
                'texto': 'Ha ocurrido un error con el envío del Mensaje, por favor vuelva a intentarlo.',
                'logoprincipal': logoprincipal
                }
            return render(request,'correo_enviado.html',contexto)
    else:
        # Redireccionar o mostrar un error si se accede al método incorrecto
        contexto = {
            'texto': 'No es posible ingresar a este formulario. Contacte al administrador',
            'logoprincipal': logoprincipal
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
            colegio = ticket.subarea.area.colegio
            logoprincipal = colegio.logoprincipal
            email_config = settings.EMAIL_BACKENDS.get(colegio.setting_name)

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

            envio = enviar_correo(
                    mensaje.asunto,
                    respuesta,
                    destinatarios_str,
                    ticket,
                    nuevo_mensaje,
                    0,
                    principal,
                    "",
                    colegio.setting_name,
                    1
            )
         

            if envio:
                contexto = {
                    'texto': 'Le responderemos a la brevedad',
                    'logoprincipal': logoprincipal
                    }
                return render(request,'correo_enviado.html',contexto)
            else:
                contexto = {
                    'texto': 'Ha ocurrido un error en el envío del Correo, verifique la casilla, sino intente nuevamente',
                    'logoprincipal': logoprincipal
                }
                return render(request,'correo_enviado.html',contexto)



        except Exception as e:
            print(f"Error: {e}")
            contexto = {
                'texto': 'Ha ocurrido un error con el envío del Mensaje, por favor vuelva a intentarlo.',
                'logoprincipal': logoprincipal
                }
            return render(request,'correo_enviado.html',contexto)
    else:
        # Redireccionar o mostrar un error si se accede al método incorrecto
        contexto = {
            'texto': 'No es posible ingresar a este formulario,contacte al Administrador.',
            'logoprincipal': logoprincipal
                }
        return render(request,'correo_enviado.html',contexto)

# def enviacorreoalapoderado(request):
#     # Envío correo de respuesta al Apoderado
#     ticket = Ticket.objects.get(id=request.POST.get('idticket'))

#     print(ticket)
#     envio_correo_apoderado(ticket.id)
#     return redirect(f'/{ticket.id}')

class VisorHistorialcaso(DetailView):

    template_name = 'visorHistorialticket.html'

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')
        ticket = Ticket.objects.get(id=pk)
        colegio = Colegio.objects.get(id=ticket.subarea.area.colegio.id)
        logoprincipal = colegio.logoprincipal
        tespera = date.today() - ticket.fechacreacion.date()
        diastotalespera = tespera.days
        tcambioestado = date.today() - ticket.fechahoracambioestado.date()
        dias_de_cambio_estado = str(tcambioestado.days)  # Días de diferencia
        nivel = get_object_or_404(Nivel, id=ticket.nivel.id)

        responsableprofesor = ProfesorResponsable.objects.filter(
            asignatura=ticket.asignatura, nivel=ticket.nivel)
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
        personaresponsableasignatura = Personas.objects.filter(
            id__in=[r.persona.id for r in responsableprofesor]).first()

        profesorjefe = []
        if ticket.subarea.profejefe:
            profesorjefe = ProfesorJefe.objects.filter(nivel=nivel, curso=ticket.curso)
        
        responsable_asignatura = []
        if ticket.asignatura.id > 1:
            responsable_asignatura = personaresponsableasignatura
            #print ()


        contexto = {
            'ticket': ticket,
            'diastotalespera': diastotalespera,
            'diascambioestado': dias_de_cambio_estado,
            'segs': Mensaje.objects.filter(ticket=pk),
            'estados': Estadoticket.objects.all(),
            'encabezado': 'Visor de Caso',
            'responsablearea': personaresponsable,
            'responsableciclo': personaciclo,
            'responsablesuperrior': personasuperior,
            'responsableasignatura': responsable_asignatura,
            'profesorjefe': profesorjefe,
            'logoprincipal': logoprincipal,
        }
        return render(request, self.template_name, contexto)


def consulta_cierre_caso(request,pk):
    template_name = 'confirma_cierre.html'
    ticket = get_object_or_404(Ticket, id=pk)

    # Obtener todos los destinatarios sin duplicados, en este caso el principal es el Apoderado (no se usa)
    personas_destinatarios,principal = obtener_destinatarios_ticket(ticket.id)
    # Crear una lista de IDs de personas_destinatarios
    ids_destinatarios = [p.id for p in personas_destinatarios]

    # Filtrar los objetos Personas con los IDs obtenidos
    destinatarios = Personas.objects.filter(id__in=ids_destinatarios)
    print ('estadoticket_id -->', ticket.estadoticket)

    contexto = {
        'ticket': ticket,
        'motivos': Motivocierre.objects.all(),
        'personascierres': destinatarios,
    }

    return render(request, template_name, contexto)

def confirma_cierre_caso(request):
    if request.method == 'POST':
        idticket = request.POST['idticket']
        tipocierre = request.POST['motivocierre']
        persona = request.POST['persona']
        ticket = get_object_or_404(Ticket, id = idticket)
        motivocierre = get_object_or_404(Motivocierre, id = tipocierre)
        personaemisor = get_object_or_404(Personas, id=persona)

        print ('ticket a cerrar -->', idticket)
        estado = 5
        estadoticket = Estadoticket.objects.get(id=estado)
        fechahoracambioestado = datetime.today()
        ticket.fechahoracambioestado = fechahoracambioestado
        ticket.estadoticket_id = estadoticket.id
        ticket.personacierre_id = personaemisor.id
        ticket.motivocierre_id = motivocierre.id
        ticket.save()

        ### crear Mensaje ###
        motivocierre = motivocierre.nombre
        Mensaje.objects.create(
            ticket=ticket,
            correoemisor=personaemisor.correo,
            correodestino="",
            respondido=1,
            asunto="CIERRA CASO",
            message=f'{personaemisor.nombre} ha cerrado el caso, con el siguiente motivo: {motivocierre}',
            persona=personaemisor
        )
        ### crear Seguimiento ###
        user = get_object_or_404(User, username='bridge')
        fec = datetime.today()
        Seguimiento.objects.create(
            ticket=ticket,
            comentario=f'{personaemisor.nombre} Cierra el caso, motivo: {motivocierre}',
            user=user,
            fechahora=fec
        )

        contexto = {
            'ticket': ticket,
            'mensaje': 'Caso ha sido cerrado con éxito. Puedes cerrar esta pestaña.'
        }

        return render(request,'cierra_pantalla.html', contexto)
    else:
        contexto = {
        'mensaje': 'Proceso cancelado. Puedes cerrar esta pestaña.'
    }
        return render(request,'cierra_pantalla.html', contexto)
        

def cierrapantalla(request):
    contexto = {
        'mensaje': 'Proceso cancelado. Puedes cerrar esta pestaña.'
    }
    return render(request,'cierra_pantalla.html', contexto)


def registroticket(request):
    # Registro Ticket Colegio Abadía Id=1
    # Vista Personalizada para Colegio Id = 1
    ' Colegio 1'
    colegio_id = 1  # ID del Colegio 1
    niveles = Nivel.objects.filter(ciclo__colegio_id=colegio_id).order_by('orden')
    cursos = Curso.objects.filter(colegio_id=colegio_id).order_by('orden')
    tipocontactos = Tipocontacto.objects.filter(colegio_id=colegio_id)
    # areas = Area.objects.filter(colegio_id = colegio_id)
    subareas = Subarea.objects.filter(area__colegio_id=colegio_id).order_by('area')
    # asignatura = Asignatura.objects.filter(colegio_id=colegio_id).order_by('orden')

    template_name = "formulario_ticket.html"
    contexto = {
        'niveles': niveles,
        'cursos': cursos,
        'tipocontactos': tipocontactos,
        'subareas': subareas,
        # 'asignaturas': asignatura,

    }
    return render(request, template_name, contexto)

def registrocasos(request):
    # Registro Ticket Colegio 2
    # Vista Personalizada para Colegio Id = 2
    ' Colegio 2'
    colegio_id = 2
    colegio = get_object_or_404(Colegio, id = colegio_id)
    niveles = Nivel.objects.filter(ciclo__colegio_id=colegio_id).order_by('orden')
    cursos = Curso.objects.filter(colegio_id=colegio_id).order_by('orden')
    tipocontactos = Tipocontacto.objects.filter(colegio_id=colegio_id)
    logoprincipal = colegio.logoprincipal

    # areas = Area.objects.filter(colegio_id = colegio_id)
    subareas = Subarea.objects.filter(area__colegio_id=colegio_id).order_by('area')
    asignatura = Asignatura.objects.filter(colegio_id=colegio_id).order_by('orden')

    template_name = "formulario_ticket2.html"
    contexto = {
        'niveles': niveles,
        'cursos': cursos,
        'tipocontactos': tipocontactos,
        'subareas': subareas,
        'asignaturas': asignatura,
        'colegio': colegio,
        'logoprincipal': logoprincipal

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
    colegio = []
    logo = ""
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
        #asignaturaid = request.POST['asignatura']
        fechahoracambioestado = datetime.now()

        nuevoticket = Ticket.objects.create(
            nombre=nombre,
            apellido=apellidos,
            correo=email,
            telefono=fono,
            tipocontacto_id=tipocontacto,
            subarea_id=subarea,
            motivo=motivo,
            estadoticket=estadoticket,
            fechahoracambioestado=fechahoracambioestado,
            nombrealumno=nombrealumno,
            apellidoalumno=apellidosalumno,
            nivel_id=nivel,
            curso_id=curso)
            #asignatura_id=asignaturaid)

        ## Enviar Correo ##
        # Prepara los datos para llamar al enviar_correo
        ticket = nuevoticket
        colegio = get_object_or_404(Colegio, id = ticket.subarea.area.colegio.id)
        
        email_config = settings.EMAIL_BACKENDS.get(colegio.setting_name)
        logoprincipal = colegio.logoprincipal


        user = get_object_or_404(User, username='bridge')
        area = ticket.subarea.area.nombre

        personas_destinatarias, principal = obtener_destinatarios_ticket(ticket.id)

        if principal == None:
            # Crea Seguimiento
            Seguimiento.objects.create(
                ticket=ticket,
                comentario='No fue posible enviar correo, falta definir Destinatario Principal.',
                user=user,
                fechahora=fechahoracambioestado
            )
            contexto = {
                'texto': 'Le responderemos a la brevedad',
                'colegio': colegio,
                'logoprincipal': logoprincipal
            }
            return render(request,'correo_enviado.html',contexto)

        to_adr = [persona.correo for persona in personas_destinatarias]
        asunto = ticket.tipocontacto.nombre+' - '+ticket.subarea.nombre+' - '+ticket.nombre+' '+ticket.apellido

        #emisor = 'bienestar@colegiolaabadia.cl'
        emisor = email_config['EMAIL_HOST_USER']
        #print ('envia_primer_correo_colegio: emisor -->', emisor)

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
            # Envia Primer Correo al colegio
            envio = enviar_correo(
                asunto,
                message,
                to_adr,
                ticket,
                nuevo_mensaje,
                1,
                principal,
                [],
                colegio.setting_name,
                1
            )

            if not envio:
                Seguimiento.objects.create(
                    ticket=ticket,
                    comentario='Ha ocurrido un error en el envío del Correo, función enviar_correo.',
                    user=user,
                    fechahora=fechahoracambioestado
                )
                contexto = {
                    'texto': 'Le responderemos a la brevedad',
                    'colegio': colegio,
                    'logoprincipal': logoprincipal
                }
                return render(request,'correo_enviado.html',contexto)

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
            nuevo_estado = get_object_or_404(Estadoticket, id=2)
          
            ticket.fechaprimerenvio = fechahoracambioestado
            ticket.estadoticket = nuevo_estado
            ticket.fechahoracambioestado = fechahoracambioestado
            ticket.save()

            # Crea Seguimiento
            Seguimiento.objects.create(
                ticket=ticket,
                comentario=f'Primer envío al Colegio. Se deriva caso al área {area}',
                user=user,
                fechahora=fechahoracambioestado
            )
          

        except Exception as e:
            Seguimiento.objects.create(
                ticket=ticket,
                comentario=f'Has ocurrido un error de excepción en el primer envío al Colegio. Error:{e}',
                user=user,
                fechahora=fechahoracambioestado
            )
            contexto = {
                'texto': 'Le responderemos a la brevedad',
                'colegio': colegio,
                'logoprincipal': logoprincipal
            }
            return render(request,'correo_enviado.html',contexto)

            ###################
    
    contexto = {
        'texto': 'Le responderemos a la brevedad',
        'colegio': colegio,
        'logoprincipal': logoprincipal
    }

    return render(request,'correo_enviado.html',contexto)
    

@login_required
def index(request):
    return render(request, "index.html")

class Index(LoginRequiredMixin,DetailView):
    
    template_name = 'index.html'
    def get(self, request, *args, **kwargs):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegioactual = accesocolegio.colegioactual_id  # ID del Colegio Actual
        colegio = get_object_or_404(Colegio, id = colegioactual)
        print (colegioactual)

        nuevos = Ticket.objects.filter(
            subarea__area__colegio_id=colegioactual, estadoticket_id = 1).count()

        colegio1 = Ticket.objects.filter(
            subarea__area__colegio_id=colegioactual, estadoticket_id = 2).count()

        conversacioncolegio = Ticket.objects.filter(
            subarea__area__colegio_id=colegioactual, estadoticket_id = 3).count()

        conversacionapoderado = Ticket.objects.filter(
            subarea__area__colegio_id=colegioactual, estadoticket_id = 4).count()

        cerrado = Ticket.objects.filter(
            subarea__area__colegio_id=colegioactual, estadoticket_id = 5).count()


        contexto = {
            'nuevos': nuevos,
            'colegio1': colegio1,
            'conversacioncolegio': conversacioncolegio,
            'conversacionapoderado': conversacionapoderado,
            'cerrado': cerrado,
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

class Listadocasos(LoginRequiredMixin,DetailView):

    template_name = 'mainticket.html'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        print ('current_user -->', current_user)
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegioactual = accesocolegio.colegioactual_id  # ID del Colegio Actual
        colegio = get_object_or_404(Colegio, id = colegioactual)
        logoprincipal = colegio.logoprincipal

        colegio_id = colegioactual  # ID del Colegio Actual
        
        print ('colegio_id -->', colegio_id)

        nuevos = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=1).order_by('fechacreacion').reverse()
        primeraresp = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=2).order_by('fechacreacion').reverse()
        convercolegio = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=3).order_by('fechacreacion').reverse()
        converapoderado = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=4).order_by('fechacreacion').reverse()
        cerrado = Ticket.objects.filter(
            subarea__area__colegio_id=colegio_id, estadoticket_id=5).order_by('fechacreacion').reverse()

        contexto = {
            'nuevos': nuevos,
            'primeraresp': primeraresp,
            'convercolegio': convercolegio,
            'converapoderado': converapoderado,
            'cerrado': cerrado,
            'colegio': colegio,
            'logoprincipal': logoprincipal
        }
        return render(request, self.template_name, contexto)


class VisorTicket(LoginRequiredMixin,DetailView):

    template_name = 'visorticket.html'

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')
        current_user = request.user
        user_id = current_user.id
        ticket = Ticket.objects.get(id=pk)
        tespera = date.today() - ticket.fechacreacion.date()
        diastotalespera = tespera.days
        tcambioestado = date.today() - ticket.fechahoracambioestado.date()
        dias_de_cambio_estado = str(tcambioestado.days)  # Días de diferencia
        nivel = get_object_or_404(Nivel, id=ticket.nivel.id)
        colegio = Colegio.objects.get(id=ticket.subarea.area.colegio.id)
        logoprincipal = colegio.logoprincipal


##########
        responsableprofesor = ProfesorResponsable.objects.filter(
            asignatura=ticket.asignatura, nivel=ticket.nivel)
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
        personaresponsableasignatura = Personas.objects.filter(
            id__in=[r.persona.id for r in responsableprofesor]).first()

        profesorjefe = []
        if ticket.subarea.profejefe:
            profesorjefe = ProfesorJefe.objects.filter(nivel=nivel, curso=ticket.curso)
        
        responsable_asignatura = []
        if ticket.asignatura.id > 1:
            responsable_asignatura = personaresponsableasignatura
            #print ()

        contexto = {
            'ticket': ticket,
            'diastotalespera': diastotalespera,
            'diascambioestado': dias_de_cambio_estado,
            'segs': Seguimiento.objects.filter(ticket=pk),
            'estados': Estadoticket.objects.all(),
            'encabezado': 'Visor de Caso',
            'responsablearea': personaresponsable,
            'responsableciclo': personaciclo,
            'responsablesuperrior': personasuperior,
            'responsableasignatura': responsable_asignatura,
            'profesorjefe': profesorjefe,
            'user_id':user_id,
            'logoprincipal': logoprincipal
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

    user = get_object_or_404(User, id=user_str)

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
        return render(request, 'index.html')

    if activar_correo == '3':
        # grabar dato que permite activar envio de correos
        return render(request, 'index.html')

    return redirect(f'/{idticket_str}')

@login_required
def zanex(request):
    return render(request, 'index.html')

@login_required
def Logout(_request):
    print ('logout')
    return render(_request,'registration/login.html')

def es_admin(user):
    return user.groups.filter(name='Administrador').exists()

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_admin), name='dispatch')
class Listausuarios(LoginRequiredMixin, ListView):
    model = User
    template_name = 'userslist.html'

    def get_queryset(self):

        return self.model.objects.exclude(username = 'bridge').order_by('first_name')

    def get(self, request, *args, **kwargs):

        contexto = {
            'usuarios': self.get_queryset(),
            'encabezado': 'Listado de Usuarios',
            'menu': 'Usuarios',
            'submenu': 'Configuración / Usuarios',
            'titulo': 'Usuarios'
        }
        return render(request, self.template_name, contexto)

@login_required
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

@login_required
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
                'msg': 'Ha ocurrido un error en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

############################################ < Gráficos > #########################################
def reporte_directorio(request):
    return render(request,'chartpie.html')

def chart_casosarea(request):
    #####################
    # Reclamos por AREA #
    #####################
    ## Falta filtrar por Colegio
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual

    start_date = date.today().replace(day=1) - timedelta(days=1) - relativedelta(months=11)
    start_date = start_date.replace(day=1)
    end_date = date.today()
    end_of_day = end_date + timedelta(days=1)

    results = Ticket.objects.filter(subarea__area__colegio_id=colegio_id,
        fechacreacion__gte=start_date,
        fechacreacion__lte=end_of_day
        ).values('subarea__area__nombre').annotate(
            total=Count('id')
            ).order_by('subarea__area__nombre')

    if (len(results) > 0):
        # Crear listas para los valores y nombres
        values = []
        names = []
        for dato in results:
            values.append(dato['total'])
            names.append(dato['subarea__area__nombre'])

        # Crear el objeto de gráfico en el formato esperado por eCharts
        chart_data = {
            'title': {
                'text': ''
            },
            'tooltip': {
                'trigger': 'item'
            },
            'legend': {
                'orient': 'vertical',
                'left': 'left'
            },
            'series': [
                {
                    'type': 'pie',
                    'radius': '80%',
                    'data': [{'value': value, 'name': name} for value, name in zip(values, names)],

                    'label': {
                        'show': False
                    },
                }
            ]
           
        }
        
        return JsonResponse(chart_data)


def chart_tpromedioprimrespuesta(request):
    #####################################
    # Tiempo promedio primera respuesta #
    #####################################
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual

    start_date = date.today().replace(day=1) - timedelta(days=1) - relativedelta(months=11)
    start_date = start_date.replace(day=1)
    end_date = date.today()
    end_of_day = end_date + timedelta(days=1)

    # recoger los promedios de los tiempos de respuesta para los casos que hayan tenido primerarespuesta
    results = Ticket.objects.filter(subarea__area__colegio_id = colegio_id,
        fechacreacion__gte=start_date,
        fechacreacion__lte=end_of_day,
        fechaprimerarespuesta__isnull=False
        ).annotate(
            response_time=ExpressionWrapper(
                F('fechaprimerarespuesta') - F('fechaprimerenvio'),
                output_field=DurationField()
            )).values(
                'subarea__area__nombre').annotate(
                    average_response_time=Avg('response_time')).order_by('subarea__area__nombre')

    # Convertir duración promedio a días en Python
    for result in results:
        result['average_response_time_days'] = round(result['average_response_time'].total_seconds() / 86400,1)

    #print (len(results))
    chart_data = {}

    if (len(results) > 0):
        # Crear listas para los valores y nombres
        values = []
        names = []
        for dato in results:
            values.append(dato['average_response_time_days'])
            names.append(dato['subarea__area__nombre'])

        # Crear el objeto de gráfico en el formato esperado por eCharts
        chart_data = {
            'legend': {
                'orient': 'horizontal',
                'left': 'center'
                },
            'xAxis': {
                'type': 'value',
                'boundaryGap': '[0.8, 0]'
                },
            'yAxis': {
                'type': 'category',
                'data': names
                },
            'label': {
                'show': 'true',
                'position': 'inside'
                },
            'series': [{ 'data': values, 'type': 'bar' }]
        }

    return JsonResponse(chart_data)

def chart_casostipocontacto(request):
    #####################################
    # Casos por AñoMes y Tipo Contacto  #
    #####################################
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual

    start_date = date.today().replace(day=1) - timedelta(days=1) - relativedelta(months=11)
    start_date = start_date.replace(day=1)
    # start_of_day = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))


    end_date = date.today()
    # end_of_day = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    end_of_day = end_date + timedelta(days=1)


    results = Ticket.objects.filter(subarea__area__colegio_id = colegio_id,
        fechacreacion__gte = start_date,
        fechacreacion__lte = end_of_day
    ).annotate(
        agno=ExtractYear('fechacreacion'),  # Extrae el año de la fecha de creación
        mes=ExtractMonth('fechacreacion'),  # Extrae el mes de la fecha de creación
        tipo=F('tipocontacto__nombre')  # tipocontacto
    ).values(
        'agno',
        'mes',
        'tipo'  # Agrupar por año, mes y tipo de contacto
    ).annotate(
        count=Count('id')  # Contar el número de tickets por grupo
    ).order_by('agno', 'mes', 'tipo')  # Ordenar los resultados por año, mes y tipo de contacto

    # Organizar los datos
    periodos = sorted(set(f"{dato['mes']:02}/{dato['agno']}" for dato in results))
    tipos = sorted(set(dato['tipo'] for dato in results))

    # Crear una estructura para los datos
    data = {tipo: [0] * len(periodos) for tipo in tipos}
    periodo_indices = {periodo: i for i, periodo in enumerate(periodos)}


    # Llenar la estructura con los conteos
    for dato in results:
        periodo = f"{dato['mes']:02}/{dato['agno']}"
        tipo = dato['tipo']
        index = periodo_indices[periodo]
        data[tipo][index] = dato['count']

    # Crear la estructura JSON
    chart_data = {}
    if (len(results) > 0):
        chart_data = {
            "legend": {
                "data": tipos
            },
            'grid': {
                'left': '3%',
                'right': '4%',
                'bottom': '3%',
                'containLabel': 'true'
            },
            'xAxis': {
                'type': 'category',
                'boundaryGap': 'false',
                'data': periodos
            },
            'yAxis': {
                    'type': 'value'
            },
            "series": [
                {
                    "name": tipo,
                    "type": "line",
                    "data": counts
                } for tipo, counts in data.items()
            ]
        }

    return JsonResponse(chart_data)
############################################ < Tablas > ###########################################
class Vista_Personas(LoginRequiredMixin, ListView):
    template_name = 'vistaPersonas.html'
    model = Personas
    

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        return self.model.objects.filter(colegio__id=colegio_id).order_by('nombre')
        

    def get(self, request, *args, **kwargs):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'personas': self.get_queryset(request),
            'encabezado': 'Listado de Docentes',
            'menu': 'Tabla Docentes',
            'submenu': 'Tablas / Docentes',
            'titulo': 'Docentes',
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

@login_required
def editarpersona(request,pk):
    persona = Personas.objects.get(id=pk)
    template_name = 'editar_persona.html'
    data = {
        'form': PersonasForm(instance=persona)
    }

    if request.method == 'POST':
        formulario = PersonasForm(data=request.POST, instance=persona)

        if formulario.is_valid():
            formulario.save()
            return redirect('listapersonas')
        else:
            data = {
                'form': PersonasForm(instance=persona),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creapersona(request):
    template_name = 'editar_persona.html'
    data = {
        'form': PersonasForm()
    }

    if request.method == 'POST':
        formulario = PersonasForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listapersonas")
        data["form"] = formulario

    return render(request,template_name, data)

class Vista_Ciclos(LoginRequiredMixin, ListView):
    template_name = 'vistaCiclos.html'
    model = Ciclos

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual

        return self.model.objects.filter(colegio__id=colegio_id).order_by('nombre')

    def get(self, request, *args, **kwargs):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'ciclos': self.get_queryset(request),
            'encabezado': 'Listado de Ciclos Colegio',
            'menu': 'Tablas Ciclos',
            'submenu': 'Tablas fijas / Ciclos',
            'titulo': 'Ciclos',
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

@login_required
def editarciclo(request,pk):
    ciclo = Ciclos.objects.get(id=pk)
    template_name = 'editar_ciclo.html'
    data = {
        'form': CiclosForm(instance=ciclo)
    }

    if request.method == 'POST':
        formulario = CiclosForm(data=request.POST, instance=ciclo)

        if formulario.is_valid():
            formulario.save()
            return redirect('listaciclos')
        else:
            data = {
                'form': CiclosForm(instance=ciclo),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creaciclo(request):
    template_name = 'editar_ciclo.html'
    data = {
        'form': CiclosForm()
    }

    if request.method == 'POST':
        formulario = CiclosForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listaciclos")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminarciclo(request,pk):
    msg = ""
    ciclo = get_object_or_404(Ciclos,id=pk)
    template_name = 'vistaCiclos.html'

    try:
     
        ciclo.delete()
        return redirect(to="listaciclos")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})

class Vista_Colegios(LoginRequiredMixin, ListView):
    template_name = 'vistaColegios.html'
    model = Colegio

    def get_queryset(self):

        return self.model.objects.order_by('nombre')

    def get(self, request, *args, **kwargs):
        

        contexto = {
            'colegios': self.get_queryset(),
            'encabezado': 'Listado de Colegios',
            'menu': 'Tablas Colegios',
            'submenu': 'Tablas fijas / Colegios',
            'titulo': 'Colegios'
        }
        return render(request, self.template_name, contexto)

@login_required
def editarcolegio(request,pk):
    colegio = Colegio.objects.get(id=pk)
    template_name = 'editar_colegio.html'
    data = {
        'form': ColegiosForm(instance=colegio)
    }

    if request.method == 'POST':
        formulario = ColegiosForm(data=request.POST, instance=colegio)

        if formulario.is_valid():
            formulario.save()
            return redirect('listacolegios')
        else:
            data = {
                'form': ColegiosForm(instance=colegio),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

def lista_niveles(_request):
    niveles = list(Nivel.objects.values('id', 'nombre', 'ciclo__nombre','orden'))
    data = {'niveles': niveles}
    return JsonResponse(data)

class Vista_Niveles(LoginRequiredMixin, ListView):
    template_name = 'vistaNiveles.html'
    model = Nivel

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual

        return self.model.objects.filter(ciclo__colegio__id = colegio_id).order_by('orden')

    def get(self, request, *args, **kwargs):
        niveles = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'niveles': niveles,
            'encabezado': 'Listado de Niveles',
            'menu': 'Tablas Niveles',
            'submenu': 'Tablas fijas / Niveles',
            'titulo': 'Niveles',
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

@login_required
def editarnivel(request,pk):
    nivel = Nivel.objects.get(id=pk)
    template_name = 'editar_nivel.html'
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual

    data = {
        'form': NivelesForm(instance=nivel,colegio_id=colegio_id)
    }

    if request.method == 'POST':
        formulario = NivelesForm(data=request.POST, instance=nivel,colegio_id=colegio_id)

        if formulario.is_valid():
            formulario.save()
            return redirect('listaniveles')
        else:
            data = {
                'form': NivelesForm(instance=nivel, colegio_id=colegio_id),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creanivel(request):
    template_name = 'editar_nivel.html'
    data = {
        'form': NivelesForm()
    }

    if request.method == 'POST':
        formulario = NivelesForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listaniveles")
        data["form"] = formulario

    return render(request,template_name, data)

def eliminarnivel(request,pk):
    msg = ""
    nivel = get_object_or_404(Nivel,id=pk)
    template_name = 'vistaNiveles.html'

    try:
        print ('nivel encontrado-->', nivel)
        nivel.delete()
        return redirect(to="listaniveles")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})


class Vista_Cursos(LoginRequiredMixin, ListView):
    template_name = 'vistaCursos.html'
    model = Curso

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual

        return self.model.objects.filter(colegio__id = colegio_id).order_by('orden')

    def get(self, request, *args, **kwargs):
        cursos = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'cursos': cursos,
            'encabezado': 'Listado de Cursos',
            'menu': 'Tablas Cursos',
            'submenu': 'Tablas fijas / Cursos',
            'titulo': 'Cursos',
            'colegio': colegio
        }
        return render(request, self.template_name, contexto)

@login_required
def editarcurso(request,pk):
    curso = Curso.objects.get(id=pk)
    template_name = 'editar_curso.html'
    data = {
        'form': CursosForm(instance=curso)
    }

    if request.method == 'POST':
        formulario = CursosForm(data=request.POST, instance=curso)

        if formulario.is_valid():
            formulario.save()
            return redirect('listacursos')
        else:
            data = {
                'form': CursosForm(instance=curso),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creacurso(request):
    template_name = 'editar_curso.html'
    data = {
        'form': CursosForm()
    }

    if request.method == 'POST':
        formulario = CursosForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listacursos")
        data["form"] = formulario

    return render(request,template_name, data)

def eliminarcurso(request,pk):
    msg = ""
    curso = get_object_or_404(Curso,id=pk)
    template_name = 'vistaCursos.html'

    try:
        curso.delete()
        return redirect(to="listacursos")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})

class Vista_Areas(LoginRequiredMixin, ListView):
    template_name = 'vistaAreas.html'
    model = Area

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        return self.model.objects.filter(colegio__id = colegio_id).order_by('nombre')

    def get(self, request, *args, **kwargs):
        
        areas = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'areas': areas,
            'encabezado': 'Listado de Areas',
            'menu': 'Tablas Areas',
            'submenu': 'Tablas fijas / Areas',
            'titulo': 'Areas',
            'colegio': colegio
        }
        return render(request, self.template_name, contexto)

@login_required
def editararea(request,pk):
    area = Area.objects.get(id=pk)
    template_name = 'editar_area.html'
    data = {
        'form': AreasForm(instance=area)
    }

    if request.method == 'POST':
        formulario = AreasForm(data=request.POST, instance=area)

        if formulario.is_valid():
            formulario.save()
            return redirect('listaareas')
        else:
            data = {
                'form': AreasForm(instance=area),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creaarea(request):
    template_name = 'editar_area.html'
    data = {
        'form': AreasForm()
    }

    if request.method == 'POST':
        formulario = AreasForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listaareas")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminararea(request,pk):
    msg = ""
    area = get_object_or_404(Area,id=pk)
    template_name = 'vistaAreas.html'

    try:
        area.delete()
        return redirect(to="listaareas")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})

class Vista_Subareas(LoginRequiredMixin, ListView):
    template_name = 'vistaSubareas.html'
    model = Subarea

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual        

        return self.model.objects.filter(area__colegio__id = colegio_id).order_by('area')

    def get(self, request, *args, **kwargs):
        subareas = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'subareas': subareas,
            'encabezado': 'Listado de Subareas',
            'menu': 'Tablas Subareas',
            'submenu': 'Tablas fijas / Subareas',
            'titulo': 'Subareas',
            'colegio': colegio
        }
        return render(request, self.template_name, contexto)

@login_required
def editarsubarea(request,pk):
    subarea = Subarea.objects.get(id=pk)
    template_name = 'editar_subarea.html'
    data = {
        'form': SubareasForm(instance=subarea)
    }

    if request.method == 'POST':
        formulario = SubareasForm(data=request.POST, instance=subarea)

        if formulario.is_valid():
            formulario.save()
            return redirect('listasubareas')
        else:
            data = {
                'form': SubareasForm(instance=subarea),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creasubarea(request):
    template_name = 'editar_subarea.html'
    data = {
        'form': SubareasForm()
    }

    if request.method == 'POST':
        formulario = SubareasForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listasubareas")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminarsubarea(request,pk):
    msg = ""
    subarea = get_object_or_404(Subarea,id=pk)
    template_name = 'vistaSubareas.html'

    try:
        subarea.delete()
        return redirect(to="listasubareas")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})

class Vista_Tiporespuesta(LoginRequiredMixin, ListView):
    template_name = 'vistaTiporespuestacolegio.html'
    model = TipoRespuestaColegio

    def get_queryset(self):
        return self.model.objects.order_by('nombre')

    def get(self, request, *args, **kwargs):
        tiporespuesta = self.get_queryset()

        contexto = {
            'tiporespuesta': tiporespuesta,
            'encabezado': 'Listado Tipo _Respuestas Colegio',
            'menu': 'Tablas Tipo Respuesta Colegio',
            'submenu': 'Tablas fijas / Tipo Respuesta Colegio',
            'titulo': 'Tipo Respuesta Colegio'
        }
        return render(request, self.template_name, contexto)

@login_required
def editartiporespuesta(request,pk):
    tiporespuesta = TipoRespuestaColegio.objects.get(id=pk)
    template_name = 'editar_tiporespuesta.html'
    data = {
        'form': TiporespuestacolegioForm(instance=tiporespuesta)
    }

    if request.method == 'POST':
        formulario = TiporespuestacolegioForm(data=request.POST, instance=tiporespuesta)

        if formulario.is_valid():
            formulario.save()
            return redirect('listatiporespuestas')
        else:
            data = {
                'form': TiporespuestacolegioForm(instance=tiporespuesta),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creatiporespuesta(request):
    template_name = 'editar_tiporespuesta.html'
    data = {
        'form': TiporespuestacolegioForm()
    }

    if request.method == 'POST':
        formulario = TiporespuestacolegioForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listatiporespuestas")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminartiporespuesta(request,pk):
    msg = ""
    tiporespuesta = get_object_or_404(TipoRespuestaColegio,id=pk)
    template_name = 'vistaTiporespuestacolegio.html'

    try:
        tiporespuesta.delete()
        return redirect(to="listatiporespuestas")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})


class Vista_Responsablesubareanivel(LoginRequiredMixin, ListView):
    template_name = 'vistaResponsablesubareanivel.html'
    model = ResponsableSubareaNivel

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual        

        return self.model.objects.filter(subarea__area__colegio__id=colegio_id).order_by('subarea', 'nivel')

    def get(self, request, *args, **kwargs):
        responsablesubareanivel = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'responsablesubareanivel': responsablesubareanivel,
            'encabezado': 'Listado Responsables SubArea y Nivel',
            'menu': 'Tablas Responsables SubArea y Nivel',
            'submenu': 'Tablas fijas / Responsables SubArea y Nivel',
            'titulo': 'Responsables SubArea y Nivel',
            'colegio': colegio,
        
        }
        return render(request, self.template_name, contexto)

@login_required
def editarresponsablesubareanivel(request,pk):
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual     

    responsablesubareanivel = ResponsableSubareaNivel.objects.get(id=pk)
    template_name = 'editar_responsablesubareanivel.html'
    data = {
        'form': ResponsablesubareanivelForm(instance=responsablesubareanivel, colegio_id=colegio_id)
    }

    if request.method == 'POST':
        formulario = ResponsablesubareanivelForm(data=request.POST, instance=responsablesubareanivel,colegio_id=colegio_id)

        if formulario.is_valid():
            formulario.save()
            return redirect('listaresponsablesubareaniveles')
        else:
            data = {
                'form': ResponsablesubareanivelForm(instance=responsablesubareanivel, colegio_id=colegio_id),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def crearesponsablesubareanivel(request):

    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual        

    template_name = 'editar_responsablesubareanivel.html'

    if request.method == 'POST':
        form = ResponsablesubareanivelForm(request.POST, colegio_id=colegio_id)
        if form.is_valid():
            form.save()
            return redirect(to="listaresponsablesubareaniveles")
    else:
        form = ResponsablesubareanivelForm(colegio_id=colegio_id)
    
    return render(request, template_name, {'form': form})

@login_required
def eliminarresponsablesubareanivel(request,pk):
    msg = ""
    responsablesubareanivel = get_object_or_404(ResponsableSubareaNivel,id=pk)
    template_name = 'vistaResponsablesubareanivel.html'

    try:
        responsablesubareanivel.delete()
        return redirect(to="listaresponsablesubareaniveles")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})

class Vista_Coordinadorciclo(LoginRequiredMixin, ListView):
    template_name = 'vistaCoordinadorciclo.html'
    model = CoordinadorCiclo

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual           

        return self.model.objects.filter(ciclo__colegio__id = colegio_id).order_by('persona')

    def get(self, request, *args, **kwargs):
        coordinadorciclo = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'coordinadorciclos': coordinadorciclo,
            'encabezado': 'Listado Coordinador Ciclo',
            'menu': 'Tablas Coordinador Ciclo',
            'submenu': 'Tablas fijas / Coordinador Ciclo',
            'titulo': 'Coordinador Ciclo',
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

@login_required
def editarcoordinadorciclo(request,pk):
    coordinadorciclo = CoordinadorCiclo.objects.get(id=pk)
    template_name = 'editar_coordinadorciclo.html'
    data = {
        'form': CoordinadorcicloForm(instance=coordinadorciclo)
    }

    if request.method == 'POST':
        formulario = CoordinadorcicloForm(data=request.POST, instance=coordinadorciclo)

        if formulario.is_valid():
            formulario.save()
            return redirect('listacoordinadorciclos')
        else:
            data = {
                'form': CoordinadorcicloForm(instance=coordinadorciclo),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creacoordinadorciclo(request):
    template_name = 'editar_coordinadorciclo.html'
    data = {
        'form': CoordinadorcicloForm()
    }

    if request.method == 'POST':
        formulario = CoordinadorcicloForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listacoordinadorciclos")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminarcoordinadorciclo(request,pk):
    msg = ""
    coordinadorciclo = get_object_or_404(CoordinadorCiclo,id=pk)
    template_name = 'vistaCoordinadorciclo.html'

    try:
        coordinadorciclo.delete()
        return redirect(to="listacoordinadorciclos")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})

class Vista_Profesorjefe(LoginRequiredMixin, ListView):
    template_name = 'vistaProfesorjefe.html'
    model = ProfesorJefe

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual           

        return self.model.objects.filter(curso__colegio__id = colegio_id).order_by('persona')

    def get(self, request, *args, **kwargs):
        profesorjefe = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'profesorjefes': profesorjefe,
            'encabezado': 'Listado Profesor Jefe',
            'menu': 'Tablas Profesor Jefe',
            'submenu': 'Tablas fijas / Profesor Jefe',
            'titulo': 'Profesor Jefe',
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

@login_required
def editarprofesorjefe(request,pk):
    profesorjefe = ProfesorJefe.objects.get(id=pk)
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual 

    template_name = 'editar_profesorjefe.html'
    data = {
        'form': ProfesorjefeForm(instance=profesorjefe, colegio_id=colegio_id)
    }

    if request.method == 'POST':
        formulario = ProfesorjefeForm(data=request.POST, instance=profesorjefe,colegio_id=colegio_id)

        if formulario.is_valid():
            formulario.save()
            return redirect('listaprofesorjefes')
        else:
            data = {
                'form': ProfesorjefeForm(instance=profesorjefe,colegio_id=colegio_id),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def creaprofesorjefe(request):
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
    colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual 
    template_name = 'editar_profesorjefe.html'
    data = {
        'form': ProfesorjefeForm(colegio_id=colegio_id)
    }

    if request.method == 'POST':
        formulario = ProfesorjefeForm(data=request.POST,colegio_id=colegio_id)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listaprofesorjefes")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminarprofesorjefe(request,pk):
    msg = ""
    profesorjefe = get_object_or_404(ProfesorJefe,id=pk)
    template_name = 'vistaProfesorjefe.html'

    try:
        profesorjefe.delete()
        return redirect(to="listaprofesorjefes")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})


class Vista_Responsableasignatura(LoginRequiredMixin, ListView):
    template_name = 'vistaResponsableasignatura.html'
    model = ProfesorResponsable

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual         

        return self.model.objects.filter(asignatura__colegio__id = colegio_id).order_by('persona')

    def get(self, request, *args, **kwargs):
        profesorresponsable = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'profesorresponsables': profesorresponsable,
            'encabezado': 'Listado Responsable Asignatura',
            'menu': 'Tablas Responsable Asignatura',
            'submenu': 'Tablas fijas / Responsable Asignatura',
            'titulo': 'Responsable Asignatura',
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

@login_required
def editarresponsableasignatura(request,pk):
    profesorresponsable = ProfesorResponsable.objects.get(id=pk)
    template_name = 'editar_responsableasignatura.html'
    data = {
        'form': ResponsableasignaturaForm(instance=profesorresponsable)
    }

    if request.method == 'POST':
        formulario = ResponsableasignaturaForm(data=request.POST, instance=profesorresponsable)

        if formulario.is_valid():
            formulario.save()
            return redirect('listaresponsableasignaturas')
        else:
            data = {
                'form': ResponsableasignaturaForm(instance=profesorresponsable),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def crearesponsableasignatura(request):
    template_name = 'editar_responsableasignatura.html'
    data = {
        'form': ResponsableasignaturaForm()
    }

    if request.method == 'POST':
        formulario = ResponsableasignaturaForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listaresponsableasignaturas")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminarresponsableasignatura(request,pk):
    msg = ""
    profesorresponsable = get_object_or_404(ProfesorJefe,id=pk)
    template_name = 'vistaResponsableasignatura.html'

    try:
        profesorresponsable.delete()
        return redirect(to="listaresponsableasignaturas")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})


class Vista_Responsablesuperior(LoginRequiredMixin, ListView):
    template_name = 'vistaResponsablesuperior.html'
    model = ResponsableSuperior

    def get_queryset(self, request):
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user = current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual         

        return self.model.objects.filter(subarea__area__colegio__id = colegio_id).order_by('persona')

    def get(self, request, *args, **kwargs):
        responsablesuperior = self.get_queryset(request)
        current_user = request.user
        accesocolegio = AccesoColegio.objects.filter(user=current_user.id).first()
        colegio_id = accesocolegio.colegioactual_id  # ID del Colegio Actual
        
        # Obtener el objeto Colegio
        colegio = Colegio.objects.get(id=colegio_id)

        contexto = {
            'responsablesuperiores': responsablesuperior,
            'encabezado': 'Listado Responsable Superior',
            'menu': 'Tablas Responsable Superior',
            'submenu': 'Tablas fijas / Responsable Superior',
            'titulo': 'Responsable Superior',
            'colegio': colegio,
        }
        return render(request, self.template_name, contexto)

@login_required
def editarresponsablesuperior(request,pk):
    responsablesuperior = ResponsableSuperior.objects.get(id=pk)
    template_name = 'editar_responsableasignatura.html'
    data = {
        'form': ResponsablesuperiorForm(instance=responsablesuperior)
    }

    if request.method == 'POST':
        formulario = ResponsablesuperiorForm(data=request.POST, instance=responsablesuperior)

        if formulario.is_valid():
            formulario.save()
            return redirect('listaresponsablesuperiores')
        else:
            data = {
                'form': ResponsablesuperiorForm(instance=responsablesuperior),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)

@login_required
def crearesponsablesuperior(request):
    template_name = 'editar_responsablesuperior.html'
    data = {
        'form': ResponsablesuperiorForm()
    }

    if request.method == 'POST':
        formulario = ResponsablesuperiorForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listaresponsablesuperiores")
        data["form"] = formulario

    return render(request,template_name, data)

@login_required
def eliminarresponsablesuperior(request,pk):
    msg = ""
    responsablesuperior = get_object_or_404(ResponsableSuperior,id=pk)
    template_name = 'vistaResponsablesuperior.html'

    try:
        responsablesuperior.delete()
        return redirect(to="listaresponsablesuperiores")

    except Exception as e:
        msg = 'ERROR: No es posible eliminar, revise el resto de la información!!'
        return render(request, template_name, {'msg': msg})

################################## < opciones principales > #######################################
@login_required
def cambiarcolegio(request):
    current_user = request.user
    accesocolegio = AccesoColegio.objects.filter(user = current_user).first()

    template_name = 'cambio_colegio.html'
    data = {
        'form': AccesoColegioForm(instance=accesocolegio)
    }

    if request.method == 'POST':
        formulario = AccesoColegioForm(data=request.POST, instance=accesocolegio)

        if formulario.is_valid():
            formulario.save()
            return redirect('index')
        else:
            data = {
                'form': AccesoColegioForm(instance=accesocolegio),
                'msg': 'Ha ocurrido un eror en el formulario revise los datos'
            }
            return render(request,template_name,context=data)

    return render(request,template_name, data)
############################################ < xanex > ############################################

def about(request):
    return render(request, 'about.html')


def accordion(request):
    return render(request, 'accordion.html')


def alerts(request):
    return render(request, 'alerts.html')


def avatarradius(request):
    return render(request, 'avatarradius.html')


def avatarround(request):
    return render(request, 'avatarround.html')


def avatarsquare(request):
    return render(request, 'avatarsquare.html')


def badge(request):
    return render(request, 'badge.html')


def blog(request):
    return render(request, 'blog.html')


def breadcrumbs(request):
    return render(request, 'breadcrumbs.html')


def buttons(request):
    return render(request, 'buttons.html')


def calendar(request):
    return render(request, 'calendar.html')


def calendar2(request):
    return render(request, 'calendar2.html')


def cards(request):
    return render(request, 'cards.html')


def carousel(request):
    return render(request, 'carousel.html')


def cart(request):
    return render(request, 'cart.html')


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
    return render(request, 'colors.html')


def construction(request):
    return render(request, 'construction.html')


def counters(request):
    return render(request, 'counters.html')


def cryptocurrencies(request):
    return render(request, 'cryptocurrencies.html')


def datatable(request):
    return render(request, 'datatable.html')


def dropdown(request):
    return render(request, 'dropdown.html')


def editprofile(request):
    return render(request, 'editprofile.html')


def email(request):
    return render(request, 'email.html')


def emailservices(request):
    return render(request, 'emailservices.html')


def empty(request):
    return render(request, 'empty.html')


def error400(request):
    return render(request, 'error400.html')


def error401(request):
    return render(request, 'error401.html')


def error403(request):
    return render(request, 'error403.html')


def error404(request):
    return render(request, 'error404.html')


def error500(request):
    return render(request, 'error500.html')


def error503(request):
    return render(request, 'error503.html')


def faq(request):
    return render(request, 'faq.html')

def footers(request):
    return render(request, 'footers.html')


def forgotpassword(request):
    return render(request, 'forgotpassword.html')


def formadvanced(request):
    return render(request, 'formadvanced.html')


def formelements(request):
    return render(request, 'formelements.html')


def formvalidation(request):
    return render(request, 'formvalidation.html')


def formwizard(request):
    return render(request, 'formwizard.html')


def gallery(request):
    return render(request, 'gallery.html')


def headers(request):
    return render(request, 'headers.html')


def icons(request):
    return render(request, 'icons.html')


def icons2(request):
    return render(request, 'icons2.html')


def icons3(request):
    return render(request, 'icons3.html')


def icons4(request):
    return render(request, 'icons4.html')


def icons5(request):
    return render(request, 'icons5.html')


def icons6(request):
    return render(request, 'icons6.html')


def icons7(request):
    return render(request, 'icons7.html')


def icons8(request):
    return render(request, 'icons8.html')


def icons9(request):
    return render(request, 'icons9.html')


def icons10(request):
    return render(request, 'icons10.html')


def invoice(request):
    return render(request, 'invoice.html')


def listas(request):
    return render(request, 'list.html')


def loaders(request):
    return render(request, 'loaders.html')


def lockscreen(request):
    return render(request, 'lockscreen.html')


# def login(request):
#     return render(request, 'login.html')


def maps(request):
    return render(request, 'maps.html')


def maps1(request):
    return render(request, 'maps1.html')


def maps2(request):
    return render(request, 'maps2.html')


def mediaobject(request):
    return render(request, 'mediaobject.html')


def modal(request):
    return render(request, 'modal.html')


def navigation(request):
    return render(request, 'navigation.html')


def notify(request):
    return render(request, 'notify.html')


def pagination(request):
    return render(request, 'pagination.html')


def panels(request):
    return render(request, 'panels.html')


def pricing(request):
    return render(request, 'pricing.html')


def profile(request):
    return render(request, 'profile.html')


def progress(request):
    return render(request, 'progress.html')


def rangeslider(request):
    return render(request, 'rangeslider.html')


def rating(request):
    return render(request, 'rating.html')


def register(request):
    return render(request, 'register.html')


def scroll(request):
    return render(request, 'scroll.html')


def search(request):
    return render(request, 'search.html')


def services(request):
    return render(request, 'services.html')


def shop(request):
    return render(request, 'shop.html')


def shopdescription(request):
    return render(request, 'shopdescription.html')


def sweetalert(request):
    return render(request, 'sweetalert.html')


def tables(request):
    return render(request, 'tables.html')


def tabs(request):
    return render(request, 'tabs.html')


def tags(request):
    return render(request, 'tags.html')


def terms(request):
    return render(request, 'terms.html')


def thumbnails(request):
    return render(request, 'thumbnails.html')


def timeline(request):
    return render(request, 'timeline.html')


def tooltipandpopover(request):
    return render(request, 'tooltipandpopover.html')


def treeview(request):
    return render(request, 'treeview.html')


def typography(request):
    return render(request, 'typography.html')


def userslist(request):
    return render(request, 'userslist.html')


def widgets(request):
    return render(request, 'widgets.html')


def wishlist(request):
    return render(request, 'wishlist.html')


def wysiwyag(request):
    return render(request, 'wysiwyag.html')
