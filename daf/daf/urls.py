from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def index(_) -> HttpResponse:
    return HttpResponse('Django Audio Feed')


urlpatterns = [
    path('', index, name='index'),
    path('podcast/', include('podcast.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
