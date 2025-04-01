# from django.urls import path
# from .views import login_view, register_view, dashboard_view, logout_view, accounts_view

# urlpatterns = [
#     path("login/", login_view, name="login"),
#     path("register/", register_view, name="register"),
#     path("dashboard/", dashboard_view, name="dashboard"),  # Ensure this line exists
#     path('accounts/', accounts_view, name='accounts'),
#     path("logout/", logout_view, name="logout"),
#     ]

# from django.urls import path
# from .views import login_view, register_view, logout_view, accounts_view

# urlpatterns = [
#     path('login/', login_view, name='login'),  # /login/
#     path('register/', register_view, name='register'),
#     path('logout/', logout_view, name='logout'),
#     path('accounts/', accounts_view, name='accounts'),  # /accounts/ -> Accounts page
# ]

from django.urls import path
from django.views.generic.base import RedirectView  # Add this import
from users.views import (
    RegisterUserView,
    login_view,
    register_view,
    dashboard_view,
    accounts_view,
    logout_view
)

# urlpatterns = [
#     # API endpoints
#     path('register/', RegisterUserView.as_view(), name='api-register'),
    
#     # Web views
#     path('login/', login_view, name='login'),
#     path('register/', register_view, name='register'),
#     path('dashboard/', dashboard_view, name='dashboard'),
#     path('accounts/', accounts_view, name='accounts'),
#     path('logout/', logout_view, name='logout'),
    
#     # Redirect root to login
#     path('', RedirectView.as_view(url='/login/')),  # Now properly imported
# ]

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),  # Ensure this line exists
    path('accounts/', accounts_view, name='accounts'),
    path("logout/", logout_view, name="logout"),
]
