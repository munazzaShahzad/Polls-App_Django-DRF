from django.test import TestCase
from django.core.exceptions import ValidationError
from polls.models import Tag


class TagModelTestCase(TestCase):

    def setUp(self):
        # Set up an initial Tag instance for testing
        self.tag = Tag.objects.create(name='Test Tag')

    def tearDown(self):
        # Ensure that no test data remains after the tests
        Tag.objects.filter(name='Test Tag').delete()
        Tag.objects.filter(name='Updated Test Tag').delete()
        Tag.objects.filter(name='Another Test Tag').delete()
        Tag.objects.filter(name='Existing Tag').delete()

    def test_create_tag(self):
        # Test creating a new tag with a unique name
        tag = Tag.objects.create(name='Another Test Tag')
        self.assertEqual(Tag.objects.filter(name='Another Test Tag').count(), 1)
        self.assertEqual(tag.name, 'Another Test Tag')

    def test_create_tag_with_short_name(self):
        # Test that creating a tag with a name less than 3 characters fails
        with self.assertRaises(ValidationError):
            tag = Tag(name='AB')
            tag.full_clean()

    def test_unique_name_constraint(self):
        # Test that creating a tag with a duplicate name raises an error
        with self.assertRaises(ValidationError):
            duplicate_tag = Tag(name='Test Tag')
            duplicate_tag.full_clean()

    def test_read_tag(self):
        # Test reading a tag instance
        tag = Tag.objects.get(pk=self.tag.pk)
        self.assertEqual(tag.name, 'Test Tag')

    def test_update_tag(self):
        # Test updating an existing tag with a unique name
        self.tag.name = 'Updated Test Tag'
        self.tag.save()
        updated_tag = Tag.objects.get(pk=self.tag.pk)
        self.assertEqual(updated_tag.name, 'Updated Test Tag')

    def test_update_tag_with_existing_name(self):
        # Test updating a tag to an existing name should raise a ValidationError
        existing_tag = Tag.objects.create(name='Existing Tag')

        self.tag.name = 'Existing Tag'

        with self.assertRaises(ValidationError):
            self.tag.full_clean()
            self.tag.save()

        existing_tag.delete()

    def test_delete_tag(self):
        # Test deleting a tag
        self.tag.delete()
        self.assertEqual(Tag.objects.filter(name='Test Tag').count(), 0)

    def test_str_method(self):
        # Test the __str__ method
        self.assertEqual(str(self.tag), f'{self.tag.id}: Test Tag')
