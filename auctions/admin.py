from django.contrib import admin
from .models import User, Listing, Categories, Watchlist, Bids, Listing_comments

# Register your models here.


class BidsAdmin(admin.ModelAdmin):
    list_display = ("bid_user", "bid", "bid_listing", "bid_time")


class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "starting_bid", "active",
                    "created_at", "listed_by", "bid_counter")


admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Categories)
admin.site.register(Watchlist)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Listing_comments)
