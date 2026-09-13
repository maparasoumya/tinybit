from django.urls import path
from .views import CreateURLView, RedirectURLView, URLDetailView

urlpatterns = [
    path('api/urls/', CreateURLView.as_view()),
    path('api/urls/<str:code>/', URLDetailView.as_view()),
    path('<str:code>/', RedirectURLView.as_view()),
]