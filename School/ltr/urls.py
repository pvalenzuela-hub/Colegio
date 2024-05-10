"""zanex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from . views import PasswordsChangeView, password_success, Registrouser
from . import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('prueba/', views.pruebacorreo, name = 'envia_correo_colegio'),
    # path('enviocolegio/', views.envio_correo_colegio, name = 'envia_correo'),
    #path('formulario_respuesta_colegio/<int:ticket_id>', views.formulariorespuesta_colegio, name='formulario_respuesta'),
    path('formulario_respuesta_colegio/<int:ticket_id>/<int:mensaje_id>/', views.formulariorespuesta_colegio, name='formulario_respuesta_colegio'),
    path('formulario_respuesta_apoderado/<int:ticket_id>/<int:mensaje_id>/', views.formulariorespuesta_apoderado, name='formulario_respuesta_apoderado'),
    path('registroticket', views.registroticket, name='registroticket'),
    path('ajax/cargar-subareas/', views.cargar_subareas, name='ajax_cargar_subareas'),
    path('creaticket', views.creaticket, name = 'crearticket'),
    path('index', views.Index.as_view(),name="index"),
    
    
    path('', views.Index.as_view(),name="index"),
    path('listacasos', views.Listadocasos.as_view(), name='lista-casos'),
    path("<int:pk>", views.VisorTicket.as_view(), name="visor-ticket"),
    path('ticket/guardacomentario', views.guardacomentario,name="graba-comentario"),
    path('respuestacolegio', views.respuesta_colegio, name = 'respuesta_colegio'),
    path('respuestaapoderado', views.respuesta_apoderado, name = 'respuesta_apoderado'),
    path('enviacorreocolegio', views.envia_primer_correo_colegio, name = 'enviacorreocolegio'),
####################################### graficos #########################################################
    path('api/casosporarea', views.chart_casosarea, name = 'chart1'),
    path('api/tiempopromedio', views.chart_tpromedioprimrespuesta, name = 'chart2'),
    path('api/casotipocontacto', views.chart_casostipocontacto, name = 'chart3'),
    path('reportedirectorio', views.reporte_directorio, name = 'reportedirectorio'),
# ########################################################################################################    
#####################################< control de usuarios >###############################################
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('edituser/<int:pk>', views.edituser, name='edit-user'),
    path('listausers',views.Listausuarios.as_view(),name='list-users'),
    path('registro/', views.Registrouser,  name='registro-usuario'),
    path('password/', PasswordsChangeView.as_view(template_name='registration/change-password.html')),
    # path('logout', views.Logout, name='logout'),
    path('password_success', views.password_success, name='password-success'),

    # path('login', LoginView.as_view(), name='login'),

       # Password Reset Process
   path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
        name = 'reset_password'),
   path('accounts/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset/password_reset_sent.html"),
        name = 'password_reset_done'),
   path('accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"),
        name = 'password_reset_confirm'),
   path('accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"),
        name = 'password_reset_complete'),
# ###############################################################################################    
    
    path('ejemplo', views.ejemplo_correo, name='ejemplo-correo'),
    path('difdias', views.prueba_dif_dias, name='prueba_dif_dias'),
###################################################< Zanex >######################################

    # path("", views.Index, name='index'),
    
    path("about", views.about, name='about'),

    path("accordion", views.accordion, name='accordion'),

    path("alerts", views.alerts, name='alerts'),

    path("avatarradius", views.avatarradius, name='avatarradius'),

    path("avatarround", views.avatarround, name='avatarround'),

    path("avatarsquare", views.avatarsquare, name='avatarsquare'),

    path("badge", views.badge, name='badge'),

    path("blog", views.blog, name='blog'),

    path("breadcrumbs", views.breadcrumbs, name='breadcrumbs'),

    path("buttons", views.buttons, name='buttons'),

    path("calendar", views.calendar, name='calendar'),

    path("calendar2", views.calendar2, name='calendar2'),

    path("cards", views.cards, name='cards'),

    path("carousel", views.carousel, name='carousel'),

    path("cart", views.cart, name='cart'),

    path("chart", views.chart, name='chart'),

    path("chartchartist", views.chartchartist, name='chartchartist'),

    path("chartdonut", views.chartdonut, name='chartdonut'),

    path("chartechart", views.chartechart, name='chartechart'),

    path("chartflot", views.chartflot, name='chartflot'),

    path("chartline", views.chartline, name='chartline'),

    path("chartmorris", views.chartmorris, name='chartmorris'),

    path("chartnvd3", views.chartnvd3, name='chartnvd3'),

    path("chartpie", views.chartpie, name='chartpie'),

    path("charts", views.charts, name='charts'),

    path("chat", views.chat, name='chat'),

    path("checkout", views.checkout, name='checkout'),

    path("colors", views.colors, name='colors'),

    path("construction", views.construction, name='construction'),

    path("counters", views.counters, name='counters'),

    path("cryptocurrencies", views.cryptocurrencies, name='cryptocurrencies'),

    path("datatable", views.datatable, name='datatable'),

    path("dropdown", views.dropdown, name='dropdown'),

    path("editprofile", views.editprofile, name='editprofile'),

    path("email", views.email, name='email'),

    path("emailservices", views.emailservices, name='emailservices'),

    path("empty", views.empty, name='empty'),

    path("error400", views.error400, name='error400'),

    path("error401", views.error401, name='error401'),

    path("error403", views.error403, name='error403'),

    path("error404", views.error404, name='error404'),

    path("error500", views.error500, name='error500'),

    path("error503", views.error503, name='error503'),

    path("faq", views.faq, name='faq'),

    path("footers", views.footers, name='footers'),

    path("forgotpassword", views.forgotpassword, name='forgotpassword'),

    path("formadvanced", views.formadvanced, name='formadvanced'),

    path("formelements", views.formelements, name='formelements'),

    path("formvalidation", views.formvalidation, name='formvalidation'),

    path("formwizard", views.formwizard, name='formwizard'),

    path("gallery", views.gallery, name='gallery'),

    path("headers", views.headers, name='headers'),

    path("icons", views.icons, name='icons'),

    path("icons2", views.icons2, name='icons2'),

    path("icons3", views.icons3, name='icons3'),

    path("icons4", views.icons4, name='icons4'),

    path("icons5", views.icons5, name='icons5'),

    path("icons6", views.icons6, name='icons6'),

    path("icons7", views.icons7, name='icons7'),

    path("icons8", views.icons8, name='icons8'),

    path("icons9", views.icons9, name='icons9'),

    path("icons10", views.icons10, name='icons10'),

    #path("index", views.Index, name='index'),

    path("invoice", views.invoice, name='invoice'),

    path("listas", views.listas, name='list'),

    path("loaders", views.loaders, name='loaders'),

    path("lockscreen", views.lockscreen, name='lockscreen'),

    # path("login", views.login, name='login'),

    path("maps", views.maps, name='maps'),

    path("maps1", views.maps1, name='maps1'),

    path("maps2", views.maps2, name='maps2'),

    path("mediaobject", views.mediaobject, name='mediaobject'),

    path("modal", views.modal, name='modal'),

    path("navigation", views.navigation, name='navigation'),

    path("notify", views.notify, name='notify'),

    path("pagination", views.pagination, name='pagination'),

    path("panels", views.panels, name='panels'),

    path("pricing", views.pricing, name='pricing'),

    path("profile", views.profile, name='profile'),

    path("progress", views.progress, name='progress'),

    path("rangeslider", views.rangeslider, name='rangeslider'),

    path("rating", views.rating, name='rating'),

    path("register", views.register, name='register'),

    path("scroll", views.scroll, name='scroll'),

    path("search", views.search, name='search'),

    path("services", views.services, name='services'),

    path("shop", views.shop, name='shop'),

    path("shopdescription", views.shopdescription, name='shopdescription'),

    path("sweetalert", views.sweetalert, name='sweetalert'),

    path("tables", views.tables, name='tables'),

    path("tabs", views.tabs, name='tabs'),

    path("tags", views.tags, name='tags'),

    path("terms", views.terms, name='terms'),

    path("thumbnails", views.thumbnails, name='thumbnails'),

    path("timeline", views.timeline, name='timeline'),

    path("tooltipandpopover", views.tooltipandpopover, name='tooltipandpopover'),

    path("treeview", views.treeview, name='treeview'),

    path("typography", views.typography, name='typography'),

    path("userslist", views.userslist, name='userslist'),

    path("widgets", views.widgets, name='widgets'),

    path("wishlist", views.wishlist, name='wishlist'),

    path("wysiwyag", views.wysiwyag, name='wysiwyag'),
]
