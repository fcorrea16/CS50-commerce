# Generated by Django 5.1 on 2024-09-05 23:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_rename_last_bid_bids_latest_bid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bids',
            old_name='highest_bid',
            new_name='bid',
        ),
    ]
