"""
Serializer for Recipe APIs.
"""
from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient Model."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link',
                  'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_tags(self, recipe, tags):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user

        if tags:
            for tag in tags:
                tag_obj, created = Tag.objects.get_or_create(
                    user=auth_user,
                    **tag
                )
                recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, recipe, ingredients):
        auth_user = self.context['request'].user
        if ingredients:
            for ingredient in ingredients:
                ingredient_obj, created = Ingredient.objects.get_or_create(
                    user=auth_user,
                    **ingredient
                )
                recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a  recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe, tags=tags)
        self._get_or_create_ingredients(recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags',  None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(instance, tags=tags)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(instance, ingredients=ingredients)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipe."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
