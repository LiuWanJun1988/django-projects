from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.generic import RedirectView
from accounts import views as account_views
from main import views as main_views
from vendor import views as vendor_views

urlpatterns = [
    path('alibaba/', admin.site.urls),
    path('support/', include('support.urls')),
    path('vendor/', include('vendor.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^signup/$', account_views.signup, name='signup'),
    url(r'^signin/$', account_views.LoginView.as_view(), name='signin'),
    url(r'^signin/gpgauth/$', account_views.gpgauth, name='gpgauth'),
    url(r'^signin/gpgverify/$', account_views.gpgverify, name='gpgverify'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/login/$', RedirectView.as_view(url='/signin')),
    url(r'^profile/usetfalogin', account_views.usetfalogin, name='usetfalogin'),
    url(r'^vendor/', vendor_views.UserVendorView.as_view(), name='user_vendor'),
    # path('accounts/', include('django.contrib.auth.urls')),

    path('account/', include('accounts.urls')),
    url(r'^accounts/$', RedirectView.as_view(url='/account')),  # Redirects url "/accounts" to "/account"
    # url(r'^accounts/', include("accounts.passwords.urls")),

    # path('accounts/', include("accounts.passwords.urls")),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('', include('main.urls')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
