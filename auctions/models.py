from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
import json


class User(AbstractUser):
    def __str__(self) -> str:
        return f"{self.username}"


class Listing(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=35)
    description = models.TextField()
    url = models.TextField()
    category = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"user:{self.user}; title:{self.title}; description:{self.description}; category:{self.category};"


class Comment(models.Model):
    username = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self) -> str:
        return f"{self.username}: ({self.comment})"


class Bid(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    value = models.FloatField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self) -> str:
        return f"{self.user}: ({self.value}); listing:{self.listing}"

class Closed_listing(models.Model):
    user_who_created = models.CharField(max_length=35)
    last_bid_user = models.CharField(max_length=35)
    title = models.CharField(max_length=35)
    value = models.FloatField()

    def __str__(self) -> str:
        return f"user_who_created: {self.user_who_created}; last_bid_user: {self.last_bid_user}; title: {self.title}; value: {self.value}"

class Watch(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="watch_list")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watch_list")

    def __str__(self) -> str:
        return f"Listing:{self.listing}; user:{self.user} "
