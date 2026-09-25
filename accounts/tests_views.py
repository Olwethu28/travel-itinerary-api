from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AccountViewTests(APITestCase):

    def test_user_can_register(self):
        url = reverse("register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!",
            "password_confirm": "Password123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )
        self.assertTrue(
            User.objects.filter(username="newuser").exists()
            )

    def test_authenticated_user_can_view_profile(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Password123!",
        )

        self.client.force_authenticate(user=user)

        url = reverse("user-detail")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["username"],
            "testuser",
        )

    def test_unauthenticated_user_cannot_view_profile(self):
        url = reverse("user-detail")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_update_profile(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Password123!",
        )

        self.client.force_authenticate(user=user)

        url = reverse("user-detail")

        data = {
            "first_name": "Updated",
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()

        self.assertEqual(
            user.first_name,
            "Updated",
        )