# tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Pokemon, VersionGroup, CaughtPokemon

class PokemonTrackingTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()

        # Create test version group (Red/Blue)
        self.version_group = VersionGroup.objects.create(
            id=1,
            name='Red/Blue',
            generation='generation-i'
        )

        # Create test Pokémon
        self.pokemon = Pokemon.objects.create(
            id=25,
            name='pikachu',
            sprite_url='http://example.com/pikachu.png'
        )

    def test_catch_pokemon(self):
        """Test catching a Pokémon"""
        # Login
        self.client.force_authenticate(user=self.user)

        # Attempt to catch Pikachu
        response = self.client.post(reverse('catch_pokemon'), {
            'pokemonId': self.pokemon.id,
            'gameId': self.version_group.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            CaughtPokemon.objects.filter(
                user=self.user,
                pokemon=self.pokemon,
                version_group=self.version_group
            ).exists()
        )

    def test_uncatch_pokemon(self):
        """Test removing a caught Pokémon"""
        self.client.force_authenticate(user=self.user)

        # First catch the Pokémon
        CaughtPokemon.objects.create(
            user=self.user,
            pokemon=self.pokemon,
            version_group=self.version_group
        )

        # Now uncatch it
        response = self.client.delete(
            reverse('uncatch_pokemon', kwargs={
                'pokemon_id': self.pokemon.id,
                'version_group_id': self.version_group.id
            })
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            CaughtPokemon.objects.filter(
                user=self.user,
                pokemon=self.pokemon,
                version_group=self.version_group
            ).exists()
        )

    def test_get_caught_pokemon(self):
        """Test getting list of caught Pokémon"""
        self.client.force_authenticate(user=self.user)

        # Catch a Pokémon
        CaughtPokemon.objects.create(
            user=self.user,
            pokemon=self.pokemon,
            version_group=self.version_group
        )

        response = self.client.get(
            reverse('get_caught_pokemon', kwargs={
                'version_group_id': self.version_group.id
            })
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pokemon'], [self.pokemon.id])

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access endpoints"""
        # Try to catch without login
        response = self.client.post(reverse('catch_pokemon'), {
            'pokemonId': self.pokemon.id,
            'gameId': self.version_group.id
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123'
        }

    def test_registration(self):
        """Test user registration"""
        response = self.client.post(
            reverse('register'),
            self.test_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(
            username=self.test_user['username']
        ).exists())

    def test_login(self):
        """Test user login"""
        # Create user first
        User.objects.create_user(**self.test_user)

        # Try to login
        response = self.client.post(
            reverse('login'),
            self.test_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.test_user['username'])

    def test_logout(self):
        """Test user logout"""
        # Create and login user
        User.objects.create_user(**self.test_user)
        self.client.login(**self.test_user)

        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)