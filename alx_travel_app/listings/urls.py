from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet
from . import views

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('initiate-payment/', views.initiate_payment),
    path('verify-payment/', views.verify_payment),
]






