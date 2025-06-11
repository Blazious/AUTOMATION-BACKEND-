from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CollectionViewSet, CollectionItemViewSet, ExpenseViewSet, GeneralExpenseViewSet

router = DefaultRouter()
router.register(r'collections', CollectionViewSet, basename='collections')
router.register(r'collection-items', CollectionItemViewSet, basename='collection-items')
router.register(r'expenses', ExpenseViewSet, basename='expenses')
router.register(r'general-expenses', GeneralExpenseViewSet, basename='general-expenses')

urlpatterns = [
    path('api/', include(router.urls)),
]
