from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # watchlist =
    pass


class Categories(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id}:{self.name}"


class Bids(models.Model):
    pass


class Listing_comments(models.Model):
    pass


class Listing(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image = models.ImageField(null=True, blank=True,
                              upload_to='listings/images/')
    # image = models.CharField(max_length=150)
    categories = models.ManyToManyField(
        Categories, related_name="categories")
    # categories = models.ForeignKey(
    #     Categories, on_delete=models.CASCADE, related_name="categories")
    # comments = models.ForeignKey(
    #     Listing_comments, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.title} with starting bid: {self.starting_bid}"
