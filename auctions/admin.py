from django.contrib import admin
from .models import User, Listing, Categories, Watchlist, Bids

# Register your models here.

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Categories)
admin.site.register(Watchlist)
admin.site.register(Bids)
