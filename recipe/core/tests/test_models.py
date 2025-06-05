"""
Tests for Models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models


class ModelTest(TestCase):
    """Test Models."""
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = "test@example.com"
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_email_normalized(self):
        """Test email is normalized for new users"""
        sample_email = [
            ['test1@EXAMPLE.com', "test1@example.com"],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test3@example.COM', 'test3@example.com']
        ]

        for email, expected in sample_email:
            user = get_user_model().objects. \
                   create_user(email=email, password='test111')
            self.assertEqual(user.email, expected)

    def test_new_user_with_empty_raises_error(self):
        """
        Test that creating a new user without an email raises a ValueError
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating super user."""
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='test111'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating recipe is successful."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description="Sample recipe description"
        )

        self.assertEqual(str(recipe), recipe.title)
