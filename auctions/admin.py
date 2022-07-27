from django.contrib import admin
from .models import Listing, Comment, Bids, Category, Images

# Register your models here.

# Admin Models for the Django /admin panel

# CategoryAdmin helps set up display preferences for the Django Admin panel
class CategoryAdmin(admin.ModelAdmin):
    list_display=('id', 'image_tag', 'category')
    list_editable=('category', 'category')

# Both the Category and CategoryAdmin models are registered into Django admin or so they will appear -- the same follows for the models below
admin.site.register(Category, CategoryAdmin)


class ListingAdmin(admin.ModelAdmin):
    list_display=('id', 'title', 'lister', 'starting_price', 'current_price', 'created_date', 'buyer')
    list_editable=('title', 'lister')
admin.site.register(Listing, ListingAdmin)


class BidsAdmin(admin.ModelAdmin):
    list_display=('id', 'auction', 'user', 'new_bid', 'date')
admin.site.register(Bids, BidsAdmin)

class ImagesAdmin(admin.ModelAdmin):
    list_display=('id', 'image_tag', 'listing', 'image', 'alt_name')
admin.site.register(Images, ImagesAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display=('id', 'user', 'listing', 'comment', 'date_created')
admin.site.register(Comment, CommentAdmin)



