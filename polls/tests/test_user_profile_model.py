from django.db import IntegrityError
from django.test import TestCase
from polls.models import UserProfile, User


class UserProfileSignalTestCase(TestCase):

    def setUp(self):
        # Create a User and corresponding UserProfile
        self.user = User.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            user_type=User.UserTypeEnum.REGULAR.value
        )
        self.user_profile = UserProfile.objects.get(user=self.user)

    def test_user_profile_creation(self):
        # Ensure the UserProfile is created correctly
        self.assertEqual(self.user_profile.name, 'Test User')
        self.assertEqual(self.user_profile.email, 'testuser@example.com')
        self.assertEqual(self.user_profile.role, 'Regular')

    def test_update_user_profile_on_user_update(self):
        # Update the User and check that the UserProfile updates accordingly
        self.user.first_name = 'Updated'
        self.user.last_name = 'Name'
        self.user.save()  # Trigger the signal
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.name, 'Updated Name')
        self.assertEqual(self.user_profile.email, 'testuser@example.com')
        self.assertEqual(self.user_profile.role, 'Regular')

    def test_user_profile_role_on_user_type_update(self):
        # Update the user's type and ensure the UserProfile's role is updated
        self.user.user_type = User.UserTypeEnum.ADMIN.value
        self.user.save()  # Trigger the signal
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.role, 'Admin')

    def test_manual_user_profile_creation_raises_error(self):
        # Attempt to create another UserProfile manually for the same user
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(
                user=self.user,
                name='Duplicate User',
                email='duplicate@example.com',
                role='REGULAR'
            )

    def test_profile_deleted_on_user_deletion(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.user.delete()
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())
