from django.conf.urls import url, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name='redirect_login'),
    url(r'^login_account/$', views.login_account, name='login_account'),
    url(r'^greyhound_data/$', views.greyhound_data, name='greyhound_data'),
    url(r'^greyhound_search/$', views.greyhound_search, name='greyhound_search'),
    #url(r'^remove_symbol_from_watch/$', views.remove_symbol_from_watch, name='remove_symbol_from_watch'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # uploaded media
    urlpatterns += static(settings.TEMPLATES_URL, document_root=settings.TEMPLATES_ROOT)


