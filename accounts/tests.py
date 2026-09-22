from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
)


User = get_user_model()


class UserSerializerTests(APITestCase):

    def test_user_registration_creates_user_with_hashed_password(self):
        data = {
            "username": "olwethu",
            "email": "olwethu@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "Olwethu",
            "last_name": "Manqola",
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertEqual(user.username, "olwethu")
        self.assertEqual(user.email, "olwethu@example.com")

        # Password must be hashed, not stored as plain text.
        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_registration_rejects_different_passwords(self):
        data = {
            "username": "olwethu",
            "email": "olwethu@example.com",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass123!",
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="olwethu@example.com",
            password="StrongPass123!",
        )

        data = {
            "username": "newuser",
            "email": "olwethu@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_is_write_only(self):
        user = User.objects.create_user(
            username="olwethu",
            email="olwethu@example.com",
            password="StrongPass123!",
        )

        serializer = UserSerializer(user)

        self.assertNotIn("password", serializer.data)