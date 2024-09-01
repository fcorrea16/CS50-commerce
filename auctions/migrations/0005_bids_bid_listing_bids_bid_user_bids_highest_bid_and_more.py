# Generated by Django 5.1 on 2024-09-01 22:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_remove_watchlist_listings_watched_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bids',
            name='bid_listing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bid_listing', to='auctions.listing'),
        ),
        migrations.AddField(
            model_name='bids',
            name='bid_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bid_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bids',
            name='highest_bid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='bids',
            name='last_bid',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
