"""
URL mappings for the recipe_app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe_app import views


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('tag', views.TagViewSet)
router.register('ingredient', views.IngredientViewSet)
app_name = 'recipe_app'

urlpatterns = [
    path('', include(router.urls)),
]
