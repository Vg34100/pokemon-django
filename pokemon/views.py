from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from .models import Pokemon, VersionGroup, CaughtPokemon

logger = logging.getLogger(__name__)

# AUTHENTICATION VIEWS

@api_view(['POST'])
def register_user(request):
    """
    Handles user registration by creating a new user and returning JWT tokens.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.create_user(username=username, password=password)
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_user(request):
    """
    Logs in a user and provides JWT tokens.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'username': user.username,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_session(request):
    """
    Checks if the user is authenticated using the provided JWT token.
    """
    return Response({'username': request.user.username})


# LOGOUT VIEW (Token Blacklist Example)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Invalidates a user's refresh token by blacklisting it.
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        # token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# POKÉMON TRACKING VIEWS

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def catch_pokemon(request):
    """Mark a Pokémon as caught"""
    try:
        pokemon_id = request.data.get('pokemonId')
        version_group_id = request.data.get('gameId')

        if not pokemon_id or not version_group_id:
            return Response(
                {'error': 'Pokemon ID and game ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or get the caught record
        _, created = CaughtPokemon.objects.get_or_create(
            user=request.user,
            pokemon_id=pokemon_id,
            version_group_id=version_group_id
        )

        if not created:
            return Response(
                {'error': 'Pokemon already caught'},
                status=status.HTTP_409_CONFLICT
            )

        return Response({'success': True}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error catching Pokemon: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def uncatch_pokemon(request, pokemon_id, version_group_id):
    """Remove a caught Pokémon"""
    try:
        caught = CaughtPokemon.objects.filter(
            user=request.user,
            pokemon_id=pokemon_id,
            version_group_id=version_group_id
        ).first()

        if not caught:
            return Response(
                {'error': 'Pokemon not found in caught list'},
                status=status.HTTP_404_NOT_FOUND
            )

        caught.delete()
        return Response({'success': True})

    except Exception as e:
        logger.error(f"Error uncatching Pokemon: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_caught_pokemon(request, version_group_id):
    """Get all caught Pokémon for a version group"""
    try:
        caught = CaughtPokemon.objects.filter(
            user=request.user,
            version_group_id=version_group_id
        ).values_list('pokemon_id', flat=True)

        return Response({'pokemon': list(caught)})

    except Exception as e:
        logger.error(f"Error getting caught Pokemon: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_pokemon_caught(request, pokemon_id, version_group_id):
    """Check if a specific Pokémon is caught"""
    try:
        is_caught = CaughtPokemon.objects.filter(
            user=request.user,
            pokemon_id=pokemon_id,
            version_group_id=version_group_id
        ).exists()

        return Response({'caught': is_caught})

    except Exception as e:
        logger.error(f"Error checking Pokemon status: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )