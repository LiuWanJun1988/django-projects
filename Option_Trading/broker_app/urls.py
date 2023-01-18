from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from Option_Trading import settings
#from django.conf import settings
from django.shortcuts import redirect

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name='login'),
    url(r'^login_account/$', views.login_account, name='login_account'),
    url(r'^dashboard/(?P<id>\w+)$', views.dashboard, name='dashboard'),
    url(r'^admin_dashboard/(?P<id>\w+)$', views.admin_dashboard, name='admin_dashboard'),
    url(r'^admin_user_setting/$', views.admin_user_setting, name='admin_user_setting'),
    url(r'^add_user/$', views.add_user, name='add_user'),
    url(r'^get_user_info/$', views.get_user_info, name='get_user_info'),
    url(r'^update_user/$', views.update_user, name='update_user'),
    url(r'^add_security/$', views.add_security, name='add_security'),
    url(r'^get_security_info/$', views.get_security_info, name='get_security_info'),
    url(r'^update_security/$', views.update_security, name='update_security'),
    url(r'^delete_security/(?P<id>\w+)$', views.delete_security, name='delete_security'),
    url(r'^percentile_filter/$', views.percentile_filter, name='percentile_filter'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # uploaded media
    urlpatterns += static(settings.TEMPLATES_URL, document_root=settings.TEMPLATES_ROOT)