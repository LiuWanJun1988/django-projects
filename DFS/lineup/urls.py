from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from DFS import settings

urlpatterns = [
    #url(r'^$', views.login, name='login'),
    url(r'^main/$', views.main, name='main'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # uploaded media
    urlpatterns += static(settings.TEMPLATES_URL, document_root=settings.TEMPLATES_ROOT)

