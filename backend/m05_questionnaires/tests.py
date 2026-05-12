from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from io import BytesIO
from PIL import Image

from accounts.models import User
from m00_onboarding.models import CicloNOM, Trabajador
from tenants.models import Tenant
from .models import Aplicacion, AplicacionFoto, Cuestionario, GuiaLink
from .services import obtener_clave_guia_pendiente


class GuiaPendienteServiceTests(TestCase):
    def setUp(self):
        self.consultor = User.objects.create_user(
            username='consultor',
            email='consultor@example.com',
            password='test',
            first_name='Con',
            last_name='Sultor',
            rol=User.SUPER_ADMIN,
        )
        self.tenant = Tenant.objects.create(
            nombre='Empresa Test',
            rfc='TST010101ABC',
            giro='Servicios',
            num_trabajadores=100,
            consultor=self.consultor,
        )
        self.trabajador = Trabajador.objects.create(
            tenant=self.tenant,
            nombre='Miguel',
            apellido_paterno='Angel',
            num_empleado='EMP-001',
            email='miguel@example.com',
            puesto='Analista',
            area='Operaciones',
        )
        self.ciclo = CicloNOM.objects.create(
            tenant=self.tenant,
            anio=2026,
            fecha_inicio=timezone.localdate(),
        )
        self.guia_v = Cuestionario.objects.create(
            clave='V',
            nombre='Datos del trabajador',
            tamano_min=1,
        )
        self.guia_iii = Cuestionario.objects.create(
            clave='III',
            nombre='Factores de riesgo psicosocial',
            tamano_min=1,
        )
        self.guia_i = Cuestionario.objects.create(
            clave='I',
            nombre='Acontecimientos traumaticos severos',
            tamano_min=1,
        )

    def crear_aplicacion(self, cuestionario, estado):
        return Aplicacion.objects.create(
            tenant=self.tenant,
            ciclo=self.ciclo,
            trabajador=self.trabajador,
            cuestionario=cuestionario,
            estado=estado,
        )

    def test_sin_guias_completadas_devuelve_v(self):
        self.assertEqual(obtener_clave_guia_pendiente(self.trabajador, self.ciclo), 'V')

    def test_v_en_progreso_sigue_devuelve_v(self):
        self.crear_aplicacion(self.guia_v, 'en_progreso')

        self.assertEqual(obtener_clave_guia_pendiente(self.trabajador, self.ciclo), 'V')

    def test_v_completada_devuelve_iii(self):
        self.crear_aplicacion(self.guia_v, 'completado')

        self.assertEqual(obtener_clave_guia_pendiente(self.trabajador, self.ciclo), 'III')

    def test_v_y_iii_completadas_devuelve_i(self):
        self.crear_aplicacion(self.guia_v, 'completado')
        self.crear_aplicacion(self.guia_iii, 'completado')

        self.assertEqual(obtener_clave_guia_pendiente(self.trabajador, self.ciclo), 'I')

    def test_tres_guias_completadas_devuelve_none(self):
        self.crear_aplicacion(self.guia_v, 'completado')
        self.crear_aplicacion(self.guia_iii, 'completado')
        self.crear_aplicacion(self.guia_i, 'completado')

        self.assertIsNone(obtener_clave_guia_pendiente(self.trabajador, self.ciclo))


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='nom035@example.com',
    FRONTEND_URL='http://frontend.test',
)
class EnviarCorreosPendientesTests(TestCase):
    def setUp(self):
        self.consultor = User.objects.create_user(
            username='consultor2',
            email='consultor2@example.com',
            password='test',
            first_name='Con',
            last_name='Sultor',
            rol=User.SUPER_ADMIN,
        )
        self.tenant = Tenant.objects.create(
            nombre='Empresa Correos',
            rfc='COR010101ABC',
            giro='Servicios',
            num_trabajadores=100,
            consultor=self.consultor,
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='test',
            first_name='Admin',
            last_name='Tenant',
            rol=User.TENANT_ADMIN,
            tenant=self.tenant,
        )
        self.ciclo = CicloNOM.objects.create(
            tenant=self.tenant,
            anio=2026,
            fecha_inicio=timezone.localdate(),
        )
        self.guia_v = Cuestionario.objects.create(clave='V', nombre='Datos del trabajador', tamano_min=1)
        self.guia_iii = Cuestionario.objects.create(clave='III', nombre='Factores de riesgo', tamano_min=1)
        self.guia_i = Cuestionario.objects.create(clave='I', nombre='Acontecimientos traumaticos', tamano_min=1)
        for guia in (self.guia_v, self.guia_iii, self.guia_i):
            GuiaLink.objects.create(tenant=self.tenant, ciclo=self.ciclo, cuestionario=guia)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def crear_trabajador(self, nombre, email, num_empleado):
        return Trabajador.objects.create(
            tenant=self.tenant,
            nombre=nombre,
            apellido_paterno='Prueba',
            num_empleado=num_empleado,
            email=email,
            puesto='Analista',
            area='Operaciones',
        )

    def completar(self, trabajador, cuestionario):
        Aplicacion.objects.create(
            tenant=self.tenant,
            ciclo=self.ciclo,
            trabajador=trabajador,
            cuestionario=cuestionario,
            estado='completado',
        )

    def test_envia_un_correo_por_siguiente_guia_pendiente(self):
        sin_avance = self.crear_trabajador('Ana', 'ana@example.com', 'A01')
        solo_v = self.crear_trabajador('Miguel', 'miguel@example.com', 'M01')
        v_y_iii = self.crear_trabajador('Carlos', 'carlos@example.com', 'C01')
        completo = self.crear_trabajador('Laura', 'laura@example.com', 'L01')

        self.completar(solo_v, self.guia_v)
        self.completar(v_y_iii, self.guia_v)
        self.completar(v_y_iii, self.guia_iii)
        self.completar(completo, self.guia_v)
        self.completar(completo, self.guia_iii)
        self.completar(completo, self.guia_i)

        response = self.client.post(f'/api/v1/aplicaciones/enviar-correos-pendientes/?ciclo_id={self.ciclo.id}')

        self.assertEqual(response.status_code, 200)
        data = response.data['data']
        self.assertEqual(data['enviados'], 3)
        self.assertEqual(data['omitidos_completos'], 1)
        self.assertEqual(len(mail.outbox), 3)

        detalle = {item['trabajador_id']: item for item in data['detalle']}
        self.assertEqual(detalle[sin_avance.id]['guia_enviada'], 'V')
        self.assertEqual(detalle[solo_v.id]['guia_enviada'], 'III')
        self.assertEqual(detalle[v_y_iii.id]['guia_enviada'], 'I')
        self.assertEqual(detalle[completo.id]['estado'], 'omitido_completo')
        self.assertIn('/guia/', detalle[sin_avance.id]['link'])


class FotoGuiaIIITests(TestCase):
    def setUp(self):
        self.consultor = User.objects.create_user(
            username='consultor_foto',
            email='consultor_foto@example.com',
            password='test',
            first_name='Con',
            last_name='Sultor',
            rol=User.SUPER_ADMIN,
        )
        self.tenant = Tenant.objects.create(
            nombre='Empresa Foto',
            rfc='FOT010101ABC',
            giro='Servicios',
            num_trabajadores=100,
            consultor=self.consultor,
        )
        self.trabajador = Trabajador.objects.create(
            tenant=self.tenant,
            nombre='Ana',
            apellido_paterno='Foto',
            num_empleado='F01',
            email='ana@example.com',
            puesto='Analista',
            area='Operaciones',
        )
        self.ciclo = CicloNOM.objects.create(
            tenant=self.tenant,
            anio=2026,
            fecha_inicio=timezone.localdate(),
        )
        self.guia_iii = Cuestionario.objects.create(clave='III', nombre='Factores de riesgo', tamano_min=1)
        self.guia_v = Cuestionario.objects.create(clave='V', nombre='Datos del trabajador', tamano_min=1)
        self.aplicacion_iii = Aplicacion.objects.create(
            tenant=self.tenant,
            ciclo=self.ciclo,
            trabajador=self.trabajador,
            cuestionario=self.guia_iii,
        )
        self.aplicacion_v = Aplicacion.objects.create(
            tenant=self.tenant,
            ciclo=self.ciclo,
            trabajador=self.trabajador,
            cuestionario=self.guia_v,
        )
        self.client = APIClient()

    def imagen(self):
        buffer = BytesIO()
        image = Image.new('RGB', (1200, 900), color=(20, 120, 180))
        image.save(buffer, format='PNG')
        return SimpleUploadedFile('foto.png', buffer.getvalue(), content_type='image/png')

    def test_subir_foto_guia_iii_comprime_y_guarda_en_bd(self):
        response = self.client.post(
            f'/api/v1/publica/{self.aplicacion_iii.token}/foto/',
            {'foto': self.imagen()},
            format='multipart',
        )

        self.assertEqual(response.status_code, 200)
        foto = AplicacionFoto.objects.get(aplicacion=self.aplicacion_iii)
        self.assertEqual(foto.estado, 'capturada')
        self.assertEqual(foto.foto_mime, 'image/jpeg')
        self.assertGreater(foto.foto_tamanio, 0)
        self.assertLess(foto.foto_tamanio, 80 * 1024)

    def test_omitir_foto_guia_iii_permite_continuar(self):
        response = self.client.post(
            f'/api/v1/publica/{self.aplicacion_iii.token}/foto/',
            {'omitida': 'true'},
            format='multipart',
        )

        self.assertEqual(response.status_code, 200)
        foto = AplicacionFoto.objects.get(aplicacion=self.aplicacion_iii)
        self.assertEqual(foto.estado, 'omitida')
        self.assertEqual(foto.foto_tamanio, 0)

    def test_rechaza_foto_en_guia_distinta_a_iii(self):
        response = self.client.post(
            f'/api/v1/publica/{self.aplicacion_v.token}/foto/',
            {'foto': self.imagen()},
            format='multipart',
        )

        self.assertEqual(response.status_code, 400)

    def test_aplicacion_publica_devuelve_foto_pendiente(self):
        response = self.client.get(f'/api/v1/publica/{self.aplicacion_iii.token}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['foto_estado'], 'pendiente')
