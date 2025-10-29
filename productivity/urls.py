from django.urls import path
from . import views
from .views import EntryListView, EntryCreateView, EntryUpdateView  # ✅ add imports


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('entries/', EntryListView.as_view(), name='entry_list'),
    path('entries/add/', EntryCreateView.as_view(), name='entry_add'),
    path('entries/<int:pk>/edit/', EntryUpdateView.as_view(), name='entry_edit'),
    path('entries/<int:pk>/update-field/', views.update_entry_field, name='update_entry_field'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.login_view),
]
