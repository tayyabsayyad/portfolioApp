# trades/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('add/', views.add_trade, name='add_trade'),
    path('<int:trade_id>/close/', views.close_trade, name='close_trade'),
    path('<int:trade_id>/', views.trade_detail, name='trade_detail'),
    path('', views.trade_list, name='trade_list'),

    # dashboard + API
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/portfolio/value/', views.portfolio_value_api, name='portfolio_value_api'),

    # reports
    path('reports/', views.reports, name='reports'),
    path('reports/export/csv/', views.export_closed_csv, name='export_closed_csv'),

    # rules
    path('rules/', views.rules_page, name='rules_page'),
    path('login/', auth_views.LoginView.as_view(template_name='trades/templates/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]