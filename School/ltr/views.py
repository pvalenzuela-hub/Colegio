from django.shortcuts import render, redirect,get_object_or_404
from django.db import connection
from django.db import transaction
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
from . models import Nivel, Curso, Tipocontacto, Area, Subarea, Ticket, Seguimiento, Estadoticket, ResponsableSubareaCiclo, ResponsableSuperior, CoordinadorCiclo, Personas
from django.views.generic import ListView, DetailView
from django.core.serializers import serialize
from datetime import date, timedelta,datetime
from django.contrib.auth.models import User

#################################################################################################

# Create your views here.
#########################

def envia_correo(request):
    # remitente
    remitente = 'bienestar@colegiolaabadia.cl'
    password = 'Abadia2024'

    #remitente = 'negocio.paulo@gmail.com'
    #password = 'paulo_2106'


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

@transaction.atomic
def envio_correo_colegio(idticket):
    try:
        ticket = get_object_or_404(Ticket, id=idticket)
        nivel = get_object_or_404(Nivel, id=ticket.nivel.id)
        nuevo_estado = get_object_or_404(Estadoticket, id=2)
        user = get_object_or_404(User,username='admin')
        area = ticket.subarea.area.nombre
        subarea = ticket.subarea.nombre
        nombreapoderado = " ".join((ticket.nombre + " " + ticket.apellido).split())
        nombrealumno = " ".join((ticket.nombrealumno + " " + ticket.apellidoalumno).split())

        # Define Destinatario del Correo
        responsablessubareaciclo = ResponsableSubareaCiclo.objects.filter(subarea=ticket.subarea, ciclo=nivel.ciclo)
        coordinadorciclo = CoordinadorCiclo.objects.filter(ciclo=nivel.ciclo)
        responsablesuperior = ResponsableSuperior.objects.filter(subarea=ticket.subarea)
    
        # Lista para guardar los objetos de destinatarios de correos
        to_adr = []
        for responsable in responsablessubareaciclo:
            persona = get_object_or_404(Personas, id=responsable.persona.id)
            destinatario_correo = persona.nombre
            to_adr.append(persona.correo)

        for responsable in coordinadorciclo:
            persona = get_object_or_404(Personas, id=responsable.persona.id)
            to_adr.append(persona.correo)

        for responsable in responsablesuperior:
            persona = get_object_or_404(Personas,id=responsable.persona.id)
            to_adr.append(persona.correo)


        print (to_adr)

        fec = datetime.now()
        ticket.estadoticket = nuevo_estado
        ticket.fechahoracambioestado = fec
        ticket.save()

        # Crear un nuevo registro en Seguimiento
        Seguimiento.objects.create(
            ticket=ticket,
            comentario=f'se deriva caso al área {area}',
            user=user,
            fechahora=fec
        )

        template = get_template('envio_correo_colegio.html')
        content = template.render({
            'destinatario': destinatario_correo,
            'apoderado': nombreapoderado,
            'alumno': nombrealumno,
            'area': area,
            'subarea': subarea,
            'ticket': ticket,
        })

        mail = EmailMultiAlternatives(
            subject="Nuevo Caso en Sistema de Bienestar",
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
    
def pruebacorreo(request):
    # botón desde Descripción para envío de correo

    envio_correo_colegio(3)
    return render(request,'exito.html')

def formulariorespuesta_colegio(request,ticket_id):
    template_name = "formulario_respuesta_colegio.html"

    # recuperar la lista de destinatarios según subarea
    ticket = get_object_or_404(Ticket, id=ticket_id)
    nivel = get_object_or_404(Nivel, id=ticket.nivel.id)

    # Obtener responsables según subárea y ciclo
    responsablessubareaciclo = ResponsableSubareaCiclo.objects.filter(subarea=ticket.subarea, ciclo=nivel.ciclo)
    coordinadorciclo = CoordinadorCiclo.objects.filter(ciclo=nivel.ciclo)
    responsablesuperior = ResponsableSuperior.objects.filter(subarea=ticket.subarea)
    
    # Lista para guardar los objetos de destinatarios
    destinatarios = []
    for responsable in responsablessubareaciclo:
        persona = get_object_or_404(Personas, id=responsable.persona.id)
        destinatarios.append(persona)

    for responsable in coordinadorciclo:
        persona = get_object_or_404(Personas, id=responsable.persona.id)
        destinatarios.append(persona)

    for responsable in responsablesuperior:
        persona = get_object_or_404(Personas,id=responsable.persona.id)
        destinatarios.append(persona)

    contexto = {
        'ticket_id': ticket_id,
        'destinatarios': destinatarios,
    }
    return render(request, template_name, context=contexto)
    
def respuesta_colegio(request):
    if request.method == 'POST':
        idticket = request.POST.get('idticket')

    
        return render(request, 'respuesta_ok.html')
    else:
        # Redireccionar o mostrar un error si se accede al método incorrecto
        return redirect('error_url')

def registroticket(request):
    
    if request.method == 'POST':
        print (request.POST['nombre'])

    
    ' Colegio 1'
    colegio_id = 1  # ID del Colegio 1
    niveles = Nivel.objects.filter(ciclo__colegio_id=colegio_id).order_by('orden')
    cursos = Curso.objects.filter(colegio_id = colegio_id).order_by('orden')
    tipocontactos = Tipocontacto.objects.filter(colegio_id = colegio_id)
    areas = Area.objects.filter(colegio_id = colegio_id)
    

    template_name = "formulario_ticket.html"
    contexto = {
        'niveles': niveles,
        'cursos': cursos,
        'tipocontactos': tipocontactos,
        'areas': areas
    
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
    fechahoracambioestado = datetime.now()

    Ticket.objects.create(nombre=nombre,apellido=apellidos,correo=email,telefono=fono,tipocontacto_id=tipocontacto,subarea_id=subarea,motivo=motivo,estadoticket_id=1,fechahoracambioestado=fechahoracambioestado,nombrealumno=nombrealumno,apellidoalumno=apellidosalumno,nivel_id=nivel,curso_id=curso)

    # print(nombre)
    # print(apellidos)
    # print(email)
    # print(fono)
    # print(nombrealumno)
    # print(apellidosalumno)
    # print(nivel)
    # print(curso)
    # print(tipocontacto)
    # print(area)
    # print(subarea)
    # print(motivo)
    
    return redirect('/registroticket')
    

class Index(DetailView):
    
    template_name = 'mainticket.html'

    def get(self, request, *args, **kwargs):
        colegio_id = 1  # ID del Colegio 1

        nuevos = Ticket.objects.filter(subarea__area__colegio_id=colegio_id, estadoticket_id=1).order_by('fechacreacion').reverse()
        respuestas = Ticket.objects.filter(subarea__area__colegio_id=colegio_id,estadoticket_id = 2).order_by('fechacreacion').reverse()
        acciones = Ticket.objects.filter(subarea__area__colegio_id=colegio_id,estadoticket_id = 3).order_by('fechacreacion').reverse()
        cerrados = Ticket.objects.filter(subarea__area__colegio_id=colegio_id,estadoticket_id = 4).order_by('fechacreacion').reverse()

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
       
        contexto = {
            'ticket': ticket,
            'diastotalespera': diastotalespera,
            'diascambioestado': dias_de_cambio_estado,
            'segs': Seguimiento.objects.filter(ticket=pk),
            'estados': Estadoticket.objects.all(),
            # 'trx': self.model2.objects.filter(pk=pk),
            'encabezado': 'Visor de Ticket',
        }
        return render(request, self.template_name, contexto)

def guardacomentario(request):

    #print (request.POST)
    comentario = request.POST['comentario']
    user_str = request.POST['userid']
    idticket_str = request.POST['idticket']
  
    cambiar_estado = 'cbox1' in request.POST

    crear_tarea = request.POST.get('cbox2', False)
    activar_correo = request.POST.get('cbox3', False)

    user = get_object_or_404(User, username='admin')
    #user = get_object_or_404(User, id=user_str)
    
    idticket = get_object_or_404(Ticket, id=idticket_str)
    estado_actual = idticket.estadoticket.nombre

    if comentario:
        seg = Seguimiento.objects.create(ticket=idticket,comentario=comentario,user=user)

    if cambiar_estado:
        estado_id = request.POST.get('estadoTicket', None)
        if estado_id:
            # Aquí puedes hacer algo con el estado_id, por ejemplo, actualizar el estado del ticket
            ticket = Ticket.objects.get(id=request.POST.get('idticket'))
            ticket.estadoticket_id = estado_id
            ticket.save()

            nuevo_estado = ticket.estadoticket.nombre

            seg = Seguimiento.objects.create(ticket=idticket,comentario=f'{user} Cambio de estado {estado_actual} a {nuevo_estado}',user=user)
       
            return redirect(f'/ticket/{idticket_str}')


    if crear_tarea == '2':
        # llamar a la vistra para crear tarea
        return render(request, 'ltr/index.html')
        
    if activar_correo == '3':
        # grabar dato que permite activar envio de correos
        return render(request, 'ltr/index.html')

    return redirect(f'/ticket/{idticket_str}')


def zanex(request):
    return render(request, 'ltr/index.html')

  
def truncar_tabla_con_reset(request):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM Ticket;')  
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="Ticket";')  # Esto reseteará el contador de ID
    return render(request)
############################################ < xanex > ############################################

def about(request):
    return render(request, 'ltr/about.html')

def accordion(request):
    return render(request, 'ltr/accordion.html')

def alerts(request):
    return render(request, 'ltr/alerts.html')

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
    return render(request, 'ltr/buttons.html')

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
    return render(request, 'ltr/chart.html')

def chartchartist(request):
    return render(request, 'ltr/chartchartist.html')

def chartdonut(request):
    return render(request, 'ltr/chartdonut.html')

def chartechart(request):
    return render(request, 'ltr/chartechart.html')

def chartflot(request):
    return render(request, 'ltr/chartflot.html')

def chartline(request):
    return render(request, 'ltr/chartline.html')

def chartmorris(request):
    return render(request, 'ltr/chartmorris.html')

def chartnvd3(request):
    return render(request, 'ltr/chartnvd3.html')

def chartpie(request):
    return render(request, 'ltr/chartpie.html')

def charts(request):
    return render(request, 'ltr/charts.html')

def chat(request):
    return render(request, 'ltr/chat.html')

def checkout(request):
    return render(request, 'ltr/checkout.html')

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

def login(request):
    return render(request, 'ltr/login.html')

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
