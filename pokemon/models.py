# models.py

from django.db import models
from django.contrib.auth.models import User

class VersionGroup(models.Model):
    """Represents a group of game versions (e.g., Red/Blue, Gold/Silver)"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    generation = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.generation})"

class Pokemon(models.Model):
    """Basic Pokémon information"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    sprite_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.id} {self.name}"

class CaughtPokemon(models.Model):
    """Tracks which Pokémon are caught by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pokemon_id = models.IntegerField()  # Just store the ID that matches PokeAPI
    version_group_id = models.IntegerField()  # Same for version groups
    caught_at = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ['user', 'pokemon_id', 'version_group_id']
        indexes = [
            models.Index(fields=['user', 'version_group_id']),
        ]

    def __str__(self):
        return f"{self.user.username}'s Pokemon #{self.pokemon_id}"

class Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    version_group_id = models.IntegerField()
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    pokemon_id = models.IntegerField()
    position = models.IntegerField()
    nickname = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(position__gte=1) & models.Q(position__lte=6),
                name='valid_position'
            ),
            models.UniqueConstraint(
                fields=['team', 'position'],
                name='unique_team_position'
            )
        ]