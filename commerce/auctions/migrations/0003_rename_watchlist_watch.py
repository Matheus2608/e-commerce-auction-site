# Generated by Django 3.2.8 on 2021-11-05 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_bids_comments_listings_watchlist'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WatchList',
            new_name='Watch',
        ),
    ]
