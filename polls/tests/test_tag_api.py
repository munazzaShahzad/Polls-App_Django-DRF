from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from polls.models import Tag, User
from polls.serializers import TagSerializer


class TagSerializerTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name='Test Tag')

    def test_serializer_contains_expected_fields(self):
        serializer = TagSerializer(instance=self.tag)
        data = serializer.data
        self.assertEqual(set(data.keys()), {'id', 'name'})

    def test_serializer_field_content(self):
        serializer = TagSerializer(instance=self.tag)
        data = serializer.data
        self.assertEqual(data['id'], self.tag.id)
        self.assertEqual(data['name'], self.tag.name)

    def test_serializer_validation(self):
        data = {'name': 'New Tag'}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], data['name'])

    def test_serializer_invalid_data(self):
        data = {'name': ''}  # Empty name, assuming it is not allowed
        serializer = TagSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class TagAPIViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpass', is_staff=True)

        self.tag2 = Tag.objects.create(name='Tag 2')
        self.tag1 = Tag.objects.create(name='Tag 1')

        self.list_url = reverse('polls:tag-list-create')
        self.detail_url = lambda pk: reverse('polls:tag-detail', args=[pk])

    def test_get_tags_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_single_tag(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.tag1.pk))

        tag = Tag.objects.get(pk=self.tag1.pk)
        serializer = TagSerializer(tag)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], serializer.data)

    def test_create_tag_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Tag'}
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], 'New Tag')
        self.assertTrue(Tag.objects.filter(name='New Tag').exists())

    def test_create_tag_as_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'New Tag'}
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_tag_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Updated Tag'}
        response = self.client.put(self.detail_url(self.tag1.pk), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Updated Tag')
        self.tag1.refresh_from_db()
        self.assertEqual(self.tag1.name, 'Updated Tag')

    def test_partial_update_tag_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Partially Updated Tag'}
        response = self.client.patch(self.detail_url(self.tag1.pk), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Partially Updated Tag')
        self.tag1.refresh_from_db()
        self.assertEqual(self.tag1.name, 'Partially Updated Tag')

    def test_delete_tag_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url(self.tag1.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(pk=self.tag1.pk).exists())

    def test_filter_tags(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'name': 'Tag 1'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Tag 1')

    def test_search_tags(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'search': 'Tag 1'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Tag 1')

    def test_order_tags(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'ordering': 'name'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'Tag 1')
        self.assertEqual(response.data['results'][1]['name'], 'Tag 2')
