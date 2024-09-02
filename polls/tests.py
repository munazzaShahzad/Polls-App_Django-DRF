from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Category


class CategoryModelTestCase(TestCase):

    def setUp(self):
        # Set up an initial Category instance for testing
        self.category = Category.objects.create(name='Test Category')

    def tearDown(self):
        # Ensure that no test data remains after the tests
        Category.objects.filter(name='Test Category').delete()
        Category.objects.filter(name='Updated Test Category').delete()
        Category.objects.filter(name='Another Test Category').delete()

    def test_create_category(self):
        # Test creating a new category with a unique name
        category = Category.objects.create(name='Another Test Category')
        self.assertEqual(Category.objects.filter(name='Another Test Category').count(), 1)
        self.assertEqual(category.name, 'Another Test Category')

    def test_create_category_with_short_name(self):
        # Test that creating a category with a name less than 3 characters fails
        with self.assertRaises(ValidationError):
            category = Category(name='AB')
            category.full_clean()

    def test_unique_name_constraint(self):
        # Test that creating a category with a duplicate name raises an error
        with self.assertRaises(ValidationError):
            duplicate_category = Category(name='Test Category')
            duplicate_category.full_clean()

    def test_read_category(self):
        # Test reading a category instance
        category = Category.objects.get(pk=self.category.pk)
        self.assertEqual(category.name, 'Test Category')

    def test_update_category(self):
        # Test updating an existing category with a unique name
        self.category.name = 'Updated Test Category'
        self.category.save()
        updated_category = Category.objects.get(pk=self.category.pk)
        self.assertEqual(updated_category.name, 'Updated Test Category')

    def test_update_category_with_existing_name(self):
        # Create a new category with a unique name
        existing_category = Category.objects.create(name='Existing Category')

        self.category.name = 'Existing Category'

        # Ensure that a ValidationError is raised due to the uniqueness constraint
        with self.assertRaises(ValidationError):
            self.category.full_clean()
            self.category.save()

        existing_category.delete()

    def test_delete_category(self):
        # Test deleting a category
        self.category.delete()
        self.assertEqual(Category.objects.filter(name='Test Category').count(), 0)

    def test_str_method(self):
        # Test the __str__ method
        self.assertEqual(str(self.category), f'{self.category.id}: Test Category')
