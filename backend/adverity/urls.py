from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('swapi/', include('swapi.urls')),
    path('', lambda request: redirect('static/index.html', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
