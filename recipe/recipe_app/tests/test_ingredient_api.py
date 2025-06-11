"""
Tests for Ingredient API.
"""
from django.test import TestCase
from core.models import Ingredient, Recipe
from rest_framework import status
from decimal import Decimal

from rest_framework.test import APIClient
from recipe_app.serializers import IngredientSerializer
from django.urls import reverse

from django.contrib.auth import get_user_model


INGREDIENT_UTL = reverse('recipe_app:ingredient-list')


def create_user(email='user@exampl.com', password='testpass111'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(ingredient_id):
    """Create and return ingredient detail url."""
    return reverse("recipe_app:ingredient-detail", args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API request."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENT_UTL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated api requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_ingredinents(self):
        """Test retrieving a  list of ingredinets."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vannila')

        res = self.client.get(INGREDIENT_UTL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test only authenticated user can create ingredients."""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENT_UTL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_update_ingredient(self):
        """Test updating an Ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Test Ingredient'
        )
        payload = {'name': "Updated Ingredient."}

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(res.data['name'], payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Test Ingredient.'
        )
        url = detail_url(ingredient_id=ingredient.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipe(self):
        """Test listing ingredients to those assigned to recipe."""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
                 title='Apple Crumble',
                 time_minutes=30,
                 price=Decimal("140"),
                 user=self.user
        )
        recipe.ingredients.add(in1)
        res = self.client.get(INGREDIENT_UTL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_retrns_unique(self):
        """Test filter ingredients returns a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Eggs Curry',
            time_minutes=20,
            price=Decimal('120'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Egg Bhurji',
            time_minutes=10,
            price=Decimal('129'),
            user=self.user
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_UTL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
