from django.conf.urls import url, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.analysis, name='analysis'),
    #url(r'^login_account/$', views.login_account, name='login_account'),
    url(r'^chart_display/$', views.chart_display, name='chart_display'),
]