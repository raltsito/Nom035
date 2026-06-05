import django, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'intra_nom035.settings.development'
django.setup()
from accounts.models import User
u = User.objects.get(username='pruebabenja')
u.set_password('pruebabenja@1234.com')
u.save()
print('Contrasena restaurada OK')
