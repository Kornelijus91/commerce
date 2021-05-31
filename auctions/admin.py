from django.contrib import admin
from .models import Listings, Bids, Comments, Watchlist

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "imgurl", "category")
# Register your models here.
admin.site.register(Listings, ListingAdmin)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)