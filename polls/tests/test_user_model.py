from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from polls.models import User
from django.db import IntegrityError


class UserModelTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser', password='password123')

    def tearDown(self):
        User.objects.all().delete()

    def test_create_user(self):
        # Test creating a new user with a unique username
        user = User.objects.create(username='anotheruser', password='password123', user_type=User.UserTypeEnum.REGULAR.value)
        self.assertEqual(User.objects.filter(username='anotheruser').count(), 1)
        self.assertEqual(user.user_type, User.UserTypeEnum.REGULAR.value)
        self.assertFalse(user.is_staff)

    def test_create_user_with_invalid_user_type(self):
        # Test that creating a user with an invalid user_type fails
        user = User(username='invalidusertype', password='password123', user_type=3)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_unique_username_constraint(self):
        # Test the unique username constraint
        User.objects.create(username='duplicateuser', password='password123')
        with self.assertRaises(IntegrityError):
            User.objects.create(username='duplicateuser', password='anotherpassword')

    def test_read_user(self):
        # Test reading a user instance
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.user_type, User.UserTypeEnum.REGULAR.value)

    def test_update_user(self):
        # Test updating an existing user
        self.user.username = 'updateduser'
        self.user.save()
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.username, 'updateduser')

    def test_update_user_type(self):
        # Test updating the user_type and its effect on is_staff
        self.user.user_type = User.UserTypeEnum.ADMIN.value
        self.user.save()
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.user_type, User.UserTypeEnum.ADMIN.value)
        self.assertTrue(updated_user.is_staff)

        # Test updating back to regular user
        self.user.user_type = User.UserTypeEnum.REGULAR.value
        self.user.save()
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.user_type, User.UserTypeEnum.REGULAR.value)
        self.assertFalse(updated_user.is_staff)

    def test_delete_user(self):
        # Test deleting a user
        self.user.delete()
        self.assertEqual(User.objects.filter(username='testuser').count(), 0)

    def test_str_method(self):
        # Test the __str__ method
        self.assertEqual(str(self.user), f'{self.user.id}: {self.user.username}')
