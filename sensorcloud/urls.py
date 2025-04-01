# from django.contrib import admin
# from django.urls import path, include
# from django.views.generic.base import RedirectView
# from users.views import (  # Import all required views
#     dashboard_view,
#     login_view,
#     register_view,
#     logout_view,
#     accounts_view
# )

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/users/', include('users.urls')),
#     path('api/devices/', include('devices.urls')),
#     path('dashboard/', dashboard_view, name='dashboard'),
    
#     # Authentication URLs
#     path('login/', login_view, name='login'),
#     path('register/', register_view, name='register'),
#     path('logout/', logout_view, name='logout'),
#     path('accounts/', accounts_view, name='accounts'),
    
#     # Redirects
#     path('', RedirectView.as_view(url='/login/')),
#     path('accounts/login/', RedirectView.as_view(url='/login/')),
# ]

# from django.contrib import admin
# from django.urls import path, include
# from django.views.generic.base import RedirectView

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/users/', include('users.urls')),
#     path('api/devices/', include('devices.urls')),
    
#     # Redirect root URL to login
#     path('', RedirectView.as_view(url='/login/')),
# ]
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
# from .views import (  # Import your web views directly
#     login_view,
#     register_view,
#     dashboard_view,
#     accounts_view,
#     logout_view
# )
from users.views import login_view, register_view, dashboard_view, accounts_view, logout_view


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/users/', include('users.urls')),  # For API routes
    path('api/devices/', include('devices.urls')),
    
    # Web interface routes
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('accounts/', accounts_view, name='accounts'),
    path('logout/', logout_view, name='logout'),
    
    # Redirect root to login
    path('', RedirectView.as_view(url='/login/')),
]