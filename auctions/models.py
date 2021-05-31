from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Bids(models.Model):
    bidderid = models.IntegerField(blank=True)
    bid = models.FloatField()

class Listings(models.Model):
    title = models.CharField(max_length=64)
    ownerid = models.IntegerField()
    winnerid = models.IntegerField(blank=True)
    description = models.TextField()
    imgurl = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    active = models.BooleanField()
    listing_bid = models.ForeignKey(Bids, on_delete=models.CASCADE, related_name="listingBid")

class Comments(models.Model):
    commenterName = models.CharField(max_length=64, blank=True)
    comment = models.TextField(blank=True)
    listing_id = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listingID")

class Watchlist(models.Model):
    userid = models.IntegerField(blank=True)
    listingid = models.IntegerField(blank=True)

    