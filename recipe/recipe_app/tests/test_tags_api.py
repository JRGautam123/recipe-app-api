"""
Tests for the Tag API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from core.models import Tag, Recipe
from recipe_app.serializers import TagSerializer


Tags_URL = reverse('recipe_app:tag-list')


def detali_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe_app:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass111'):
    user = get_user_model().objects.create_user(email=email, password=password)
    return user


class PublicTagApiTests(TestCase):
    """Test unauthenticated user requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_users(self):
        """Test auth is required for retrieving tags."""
        create_user()

        res = self.client.get(Tags_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    """Tests for Authenticated users."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_tag_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(Tags_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(Tags_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a Tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {'name': 'Dessert'}
        res = self.client.patch(detali_url(tag.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_tag_deleted(self):
        """Test deleting tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        url = detali_url(tag_id=tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tag_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')

        recipe = Recipe.objects.create(
            title='Eggs on Tost',
            time_minutes=10,
            price=Decimal('120'),
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(Tags_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtred_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')

        recipe1 = Recipe.objects.create(
            title='Pancake',
            time_minutes=20,
            price=Decimal('120'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Daal Bhat and Tarkari',
            time_minutes=10,
            price=Decimal('129'),
            user=self.user
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(Tags_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data), 1)
