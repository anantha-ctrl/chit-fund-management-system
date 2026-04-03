from django.urls import path
from . import views

urlpatterns = [
    path('', views.auction_list, name='auction_list'),
    path('create/', views.auction_create, name='auction_create'),
    path('<int:pk>/', views.auction_detail, name='auction_detail'),
    path('guarantor/add/<int:auction_id>/', views.guarantor_add, name='guarantor_add'),
]
