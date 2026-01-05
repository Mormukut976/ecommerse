from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Shope in home Admin'
admin.site.site_title = 'Shope in home Admin'
admin.site.index_title = 'Dashboard'
admin.site.enable_nav_sidebar = False


def healthz(request):
    return HttpResponse('ok', content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', healthz, name='healthz'),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('', include('catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
