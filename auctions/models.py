from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Categories(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id}:{self.name}"


class Listing_comments(models.Model):
    pass


class Listing(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image = models.ImageField(null=True, blank=True,
                              upload_to='listings/images/')
    categories = models.ManyToManyField(
        Categories, related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    listed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listed_by")

    def __str__(self):
        return f"{self.id}: {self.title} with starting bid: {self.starting_bid}"


class Watchlist(models.Model):
    user_watching = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_watching", blank=True, null=True)
    listing_watching = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listing_watching", blank=True, null=True)

    def __str__(self):
        return f"{self.id}: {self.user_watching} {self.listing_watching}"


class Bids(models.Model):
    bid_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bid_user", blank=True, null=True)
    bid_listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bid_listing", blank=True, null=True)
    bid = models.IntegerField(default=0)
    latest_bid = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.bid} {self.bid_user}"
