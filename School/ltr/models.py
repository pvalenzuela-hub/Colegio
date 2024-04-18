from django.db import models
from django.contrib.auth.models import User
from datetime import date


# Create your models here.
class Colegio(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ["nombre"]
        verbose_name = 'Colegio'
        verbose_name_plural = 'Colegios'
        db_table = 'Colegio'

class Estadoticket(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre+' - '+str(self.id)

    class Meta:
        ordering = ["nombre"]
        db_table = 'EstadoTicket'

class Area(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    colegio = models.ForeignKey(Colegio,on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        db_table = 'Area'

class Subarea(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    area = models.ForeignKey(Area,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.area)+' - '+self.nombre

    class Meta:
        ordering = ["area"]
        db_table = 'SubArea'


class Personas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=80)
    cargo = models.CharField(max_length=80,default="")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        db_table = 'Personas'

class Ciclos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    colegio = models.ForeignKey(Colegio,on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.nombre+' '+str(self.colegio)

    class Meta:
        ordering = ["id"]
        db_table = 'Ciclos'

class ResponsableSubareaCiclo(models.Model):
    id = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Personas,on_delete=models.CASCADE)
    subarea = models.ForeignKey(Subarea,on_delete=models.DO_NOTHING)
    ciclo = models.ForeignKey(Ciclos,on_delete=models.DO_NOTHING)

    def __str__(self):
        return 'CICLO : '+str(self.ciclo)+' - '+str(self.persona)+' AREA : '+str(self.subarea)
    
    class Meta:
        ordering = ['id']
        db_table = 'ResponsableSubareasCiclos'

class ResponsableSuperior(models.Model):
    id = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Personas,on_delete=models.CASCADE)
    subarea = models.ForeignKey(Subarea,on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.subarea)+' - '+str(self.persona)

    class Meta:
        ordering = ['id']
        db_table = 'ResponsableSuperior'

class CoordinadorCiclo(models.Model):
    id = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Personas,on_delete=models.CASCADE)
    ciclo = models.ForeignKey(Ciclos,on_delete=models.DO_NOTHING)

    def __str__(self):
        return 'CICLO : '+str(self.ciclo)+' - '+str(self.persona)

    class Meta:
        ordering = ['id']
        db_table = 'CoordinadorCiclos'

class Tipocontacto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    colegio = models.ForeignKey(Colegio,on_delete=models.DO_NOTHING,default=1)
    color = models.CharField(max_length=10,default='#FFFFFF')

    def __str__(self):
        return str(self.id)+':'+self.nombre

    class Meta:
        ordering = ["nombre"]
        db_table = 'TipoContacto'

class Nivel(models.Model):
    id =models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    ciclo = models.ForeignKey(Ciclos,on_delete=models.DO_NOTHING,default=1)
    orden = models.IntegerField()

    def __str__(self):
        return self.nombre+' - '+str(self.ciclo)

    class Meta:
        ordering = ["ciclo","orden"]
        db_table = 'Nivel'

class Curso(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    colegio = models.ForeignKey(Colegio,on_delete=models.CASCADE,default=1)
    orden = models.IntegerField(default=1)

    def __str__(self):
        return self.nombre+' COLEGIO: '+str(self.colegio)

    class Meta:
        ordering = ["colegio","orden"]
        db_table = 'Curso'

class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=80,null=False)
    apellido = models.CharField(max_length=80,null=False)
    correo = models.EmailField(max_length=100,null=False)
    telefono = models.CharField(max_length=80,null=True)
    tipocontacto = models.ForeignKey(Tipocontacto,on_delete=models.DO_NOTHING)
    subarea = models.ForeignKey(Subarea,on_delete=models.DO_NOTHING)
    motivo = models.TextField(blank=False,null=False)
    fechaactualizacion = models.DateTimeField(auto_now=True)
    fechahoracambioestado = models.DateTimeField(null=True,blank=True)
    estadoticket = models.ForeignKey(Estadoticket,on_delete=models.DO_NOTHING)
    nombrealumno = models.CharField(max_length=80,default="")
    apellidoalumno = models.CharField(max_length=80,default="")
    nivel = models.ForeignKey(Nivel,on_delete=models.DO_NOTHING,default=1)
    curso = models.ForeignKey(Curso,on_delete=models.DO_NOTHING,default=1)

    class Meta:
        ordering = ['id']
        db_table = ''

    def __str__(self):
        return str(self.id)+':'+self.fechacreacion.strftime('%d/%m/%Y')+' - '+self.nombre+' '+self.apellido

    class Meta:
        ordering = ["id"]
        db_table = 'Ticket'


class TipoTarea(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        db_table = 'TipoTarea'

class EstadoTarea(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        db_table = 'EstadoTarea'

class Tarea(models.Model):
    id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE)
    fechacreacion = models.DateTimeField(auto_now=True)
    fechavencimiento = models.DateField(null=False)
    detalle = models.CharField(max_length=80)
    tipotarea = models.ForeignKey(TipoTarea,on_delete=models.CASCADE)
    estadotarea = models.ForeignKey(EstadoTarea,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.id)+':'+str(self.ticket)+':'+self.detalle

    class Meta:
        ordering = ["id"]
        db_table = 'Tarea'

class Seguimiento(models.Model):
    id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE)
    fechahora = models.DateTimeField(auto_now=True)
    comentario = models.TextField(null=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.id)+':'+self.fechahora.strftime('%d/%m/%Y %H:%M')+' : '+self.comentario

    class Meta:
        ordering = ["id"]
        db_table = 'Seguimiento'


