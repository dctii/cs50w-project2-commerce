from django.contrib.auth.models import AbstractUser
from django.utils.html import mark_safe
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

# Model for Listing Categories
class Category(models.Model):
    # title of the category
    category = models.CharField(max_length=30)
    # image upload that represents the category
    image = models.ImageField(upload_to='categories')

    class Meta:
        verbose_name_plural='01. Categories'
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

    def __str__(self):
        return f"{self.category}"

# Model for Individual Listings
class Listing(models.Model):
    title = models.CharField(max_length=100)
    # 'lister' represents the creator of the specified listing
    lister = models.ForeignKey(User, on_delete=models.PROTECT, related_name="lister")
    # Open listings are active, unclosed listings
    open_listing = models.BooleanField(default=True)
    # Description for the listing
    description = models.CharField(null=True, max_length=300)
    # The starting price is the floor price for the auction.
    starting_price = models.FloatField(verbose_name="Starting Price")
    # The most recent price of the auction for the listing
    current_price = models.FloatField(blank=True, null=True)
    # ForeignKey to the Category Model to typify the listing
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # Date the listing was made
    created_date = models.DateTimeField(default=timezone.now)
    # For users who put the listing on their watchlist
    watchers = models.ManyToManyField(User, blank=True, related_name="watched")
    # The individual who wins the the auction of the listing
    buyer = models.ForeignKey(User, null=True, on_delete=models.PROTECT, related_name="buyer")

    class Meta:
        # Sets the plural naming to avoid misspellings when Django auto-pluralizes.
        verbose_name_plural='02. Listings'

    def __str__(self):
        return f"{self.title} - {self.starting_price}"

# Model for user bids on listings
class Bids(models.Model):
    # ForeignKey to the Listing Model
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)
    # ForeignKey to the User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Collects bids from users on the listing
    new_bid = models.FloatField(verbose_name="Bid Amount")
    # Counts the time the bid occurs
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural='03. Bids'

# Model for Listing images
class Images(models.Model):
    # ForeignKey to the Listing Model
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_images")
    # If users enter a URL to an image file that is working, it will plug it into an <img> tag and present it for the listing
    image = models.CharField(max_length=2048)
    # Allows user to provide alternative information for the image
    alt_name = models.CharField(verbose_name="Alternative Name", max_length=140)

    class Meta:
        verbose_name_plural='04. Images'
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50">' % (self.image))

class Comment(models.Model):
    # ForeignKey to User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ForeignKey to Listing model
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    # For comments entered on a specified listing by a user
    comment = models.CharField(max_length=250)
    # Recorded date the user commented on the listing
    date_created = models.DateTimeField(verbose_name="Date Created", default=timezone.now)

    class Meta:
        verbose_name_plural='05. Comments'

    # Returns the date in the specified format below
    def get_creation_date(self):
        return self.date_created.strftime('%B %d %Y')
