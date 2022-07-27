from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django import forms
from django.forms import ModelForm, modelformset_factory

from .models import *

# Forms for the Auction site

# Image Form for the user to input the URL and an alternative name for the listing or image
class ImageForm(ModelForm):
    class Meta:
        # Which model the form is for and from
        model = Images
        # The fields for input from the user
        fields = ['image', 'alt_name']
        # HTML attribute preferences for each field
        widgets = {
            'image': forms.TextInput(attrs={
                'class': 'w-100 form-control bg bg-light',
                'placeholder':'https://www.name.com/image.jpeg',
                'autocomplete': 'off'
            }),
            'alt_name': forms.TextInput(attrs={
                'class': 'w-100 form-control bg bg-light',
                'placeholder':'Alternative Name',
                'autocomplete': 'off'
            }),
        }


class CreateListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_price', 'category']
        widgets= {
            'title': forms.TextInput(attrs={
                'class': 'w-100 form-control bg bg-light',
                'placeholder':'Title',
                'autocomplete': 'off'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-100 form-control bg bg-light',
                'placeholder':'Description',
                'autocomplete': 'off'
            }),
            'starting_price': forms.TextInput(attrs={
                'class': 'w-100 form-control bg bg-light',
                'placeholder':'$0.00',
                'autocomplete': 'off'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control bg bg-light'
            }),
        }


class BidForm(ModelForm):
    class Meta:
        model = Bids
        fields = ['new_bid']
        widgets = {
            'new_bid': forms.TextInput(attrs={
                'class': 'form-control border border-dark',
                'placeholder': '$0.00',
                'autocomplete': 'off'
            })
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.TextInput(attrs={
                'class': 'border border-dark pb-1 pl-2',
                'style': 'width: 400px;',
                'placeholder': 'Type Here',
                'autocomplete': 'off'
            })
        }


# The home page, which merely returns the active_listings function
def index(request):
    return active_listings(request)


# @login_required is a decorator tag which includes the user to be logged in to use the function vertically contiguous to it
# create_listing is the the view function where the user creates a new listing for the auction website
@login_required
def create_listing(request):
    # Default form set for the Images model
    image_formset = modelformset_factory(Images,
                                        form = ImageForm)
    
    # Only run if the user submits information
    if request.method == "POST":
        # Information from these forms are to be sent given the POST condition is met
        form = CreateListingForm(request.POST, 
                                request.FILES)
        image_form = image_formset(request.POST, 
                                request.FILES,
                                queryset = Images.objects.none())

        # If the information the user has input to the fields is valid, then save the new listing into the database
        if form.is_valid() and image_form.is_valid():
            create_listing = form.save(commit=False)
            create_listing.lister = request.user
            create_listing.save()

            for form in image_form.cleaned_data:
                if form:
                    image = form['image']
                    text = form['alt_name']
                    image_data = Images(listing = create_listing, image = image, alt_name = text)
                    image_data.save()
            return render(request, "auctions/create_listing.html", {
                # Mapping context variables to help Python and Django work together
                "form": CreateListingForm(),
                "image_form": image_formset(queryset = Images.objects.none()),
                # Submit turn the success condition to true, which will allow a success message to be relayed if the form is created successfully
                "success": True
            })
        # If the form is not valid, then render the page again for the user to start over
        else:
            return render(request, "auctions/create_listing.html", {
                "form": CreateListingForm(),
                "image_form": image_formset(queryset = Images.objects.none())
            })
    # If the page is refreshed manually or automatically or any other way the user sends a GET for the mere page, then render the page and form to create a new listing
    else:
        return render(request, "auctions/create_listing.html", {
            "form": CreateListingForm(),
            "image_form": image_formset(queryset = Images.objects.none())
        })

# This is for rendering unclosed listings
def active_listings(request):
    # ID for the category from Category in models.py
    cat_id = request.GET.get("category", None)

    # If there is no category ID to be pulled, then return every listing
    if cat_id is None:
        listings = Listing.objects.filter(open_listing = True)
    # If there is a category ID to be pulled, then list those with that specific ID
    else:
        listings = Listing.objects.filter(open_listing = True, category = cat_id)

    # Variable to get all information from the Category model for populating the category name for the page header
    categories = Category.objects.all()

    # Loop that helps with generating information for each individual listing
    for listing in listings:
        # Counts the number of bids on a specified listing
        listing.bid_sum = len(Bids.objects.filter(auction=listing).all())
        # The image of the specified listing (comes from the URL the user provides when creating the listing)
        listing.image = listing.listing_images.first()
        
        # If the user is part of the set of listing watchers for this specific listing, then this value is True, and this is used so the user will see a green eye icon to signal to remind them they're watching the listing.
            # Also, a watchlist button will turn to the color red on the listing page for that specific listing.
        if request.user in listing.watchers.all():
            listing.is_watched = True
        # If they are not part of that set, then they will just see the normal listing and the Watchlist button on the listing page will be blue.
        else:
            listing.is_watched = False
        
    return render(request, "auctions/index.html", {
        # This is a variable used to set the heading for the home page when "active_listings" runs
        "page_header": "💓 Active Listings",
        # Passes the listings information given the conditions and filters above
        "listings": listings,
        # Passes information regarding the Category model in models.py
        "categories": categories
    })

# For the categories.html page which shows the user all of the categories on the Auction website
def categories(request):
    # Gets all of the information from the Category model
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })

# For listings of a specific category
def category_list(request, cat_id):
    # Gets the Category ID from the category model
    category=Category.objects.get(id=cat_id)
    # Gets listings if it is true that they are an open_listing (they are unclosed) and considers category as well
    listings=Listing.objects.filter(open_listing = True, category=category).order_by('-id')
    
    # Loop that helps with generating information for each individual listing
    for listing in listings:
        # Counts the number of bids on a specified listing
        listing.bid_sum = len(Bids.objects.filter(auction=listing).all())
        # The image of the specified listing (comes from the URL the user provides when creating the listing)
        listing.image = listing.listing_images.first()

        # If the user is part of the set of listing watchers for this specific listing, then this value is True, and this is used so the user will see a green eye icon to signal to remind them they're watching the listing.
            # Also, a watchlist button will turn to the color red on the listing page for that specific listing.
        if request.user in listing.watchers.all():
            listing.is_watched = True
        # If they are not part of that set, then they will just see the normal listing and the Watchlist button on the listing page will be blue.
        else:
            listing.is_watched = False
        
    return render(request,'auctions/category_list.html',{
			'listings':listings,
			})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# For rendering the product detail page for the listing.
def listing(request, listing_id):
    # If the user is not logged in, then redirect them to the login page.
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    
    # Gets the ID of the listing from the Listing model
    listing = Listing.objects.get(id=listing_id)

    # Counts the number of bids on a specified listing
    bid_sum = len(Bids.objects.filter(auction=listing).all())

    # If the user is part of the set of listing watchers for this specific listing, then this value is True, and this is used so the user will see a green eye icon to signal to remind them they're watching the listing.
            # Also, a watchlist button will turn to the color red on the listing page for that specific listing.
    if request.user in listing.watchers.all():
        listing.is_watched = True
    # If they are not part of that set, then they will just see the normal listing and the Watchlist button on the listing page will be blue.
    else:
        listing.is_watched = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "listing_images": listing.listing_images.all(),
        "bid_sum":bid_sum,
        "form": BidForm(),
        "comments": listing.listing_comments.all(),
        "comments_form": CommentForm()
    })

# For making bids on listings
@login_required
def take_bid(request, listing_id):
    # Gets the listing ID from the Listing model
    listing = Listing.objects.get(id=listing_id)
    # Takes in a float value for submission of a new bid from the BidForm the user completes and submits
    new_bid = float(request.POST['new_bid'])
    # Counts the number of bids on a specified listing
    bid_sum = len(Bids.objects.filter(auction=listing).all())

    # If the number the user inputs is valid, then save the data
    if is_valid(new_bid, listing):
        listing.current_price = new_bid
        form = BidForm(request.POST)
        new_bid_data = form.save(commit = False)
        new_bid_data.auction = listing
        new_bid_data.user = request.user
        new_bid_data.save()
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    # If it is not valid, because the new_bid is less than the starting price or is less than or equal to the current price, then do this and also pass in new information that says there is an error with the submission because the minimum value condition cannot be met
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "listing_images": listing.listing_images.all(),
            "bid_sum":bid_sum,
            "form": BidForm(),
            "error_min_value": True,
            "comments": listing.listing_comments.all(),
            "comments_form": CommentForm()
        })

# Function to check if the new_bid data in the take_bid function is valid or not
def is_valid(new_bid, listing):
    # It's true that new_bid is valid if it is greater than or equal to the starting_price given by the lister and can also be valid if the listing.current price is greater than the current price
    if new_bid >= listing.starting_price and (listing.current_price is None or new_bid > listing.current_price):
        return True
    # If the above conditions are not met, then it is false that the data for new_bid is valid
    else:
        return False

# Function for comments on specific listings
@login_required
def comment(request, listing_id):
    # Get Listing ID information from the Listing model
    listing = Listing.objects.get(id=listing_id)
    # Specific form for writing comments
    form = CommentForm(request.POST)
    # Save the data in the form and also include with the saving the user and specified listing the comment is for
    new_comment_data = form.save(commit = False)
    new_comment_data.user = request.user
    new_comment_data.listing = listing
    new_comment_data.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

# Function for rendering the user's watchlisted listings
@login_required
def watchlist(request):
    # Get the information of listings being watched
    listings = request.user.watched.all()
    categories = Category.objects.all()

    # Loop that helps with generating information for each individual listing
    for listing in listings:
        # Get information for the image for each listing
        listing.image = listing.listing_images.first()
        # Counts the number of bids on a specified listing
        listing.bid_sum = len(Bids.objects.filter(auction=listing).all())
        # If the user is on the watchlist, then return the user is watching it as true
        if request.user in listing.watchers.all():
            listing.is_watched = True
        else: 
            listing.is_watched = False

    return render(request, "auctions/index.html", {
        "page_header": "🔭 My Watchlist",
        "listings": listings,
        "categories": categories,
    })

# Function for activating/deactivating a listing page's watchlist status for a user
@login_required
def watchlist_switch(request, listing_id, reverse_method):
    # Get the information of listing ID to help ID which listing's watchlist status is changed for the user
    listing_obj = Listing.objects.get(id = listing_id)
    
    # If the user is part of the set that is watching the listing, then remove the user from the set -- a button is provided via Django HTML to execute the path to run this
    if request.user in listing_obj.watchers.all():
        listing_obj.watchers.remove(request.user)
    # Otherwise, pressing the watchlist button on the page will add the user to the set of those watching the listing
    else:
        listing_obj.watchers.add(request.user)
    
    # After adding or removing oneself from the watchlist for the listing, then the user goes back to the page with the user's status changed
    if reverse_method == "listing":
        return listing(request, listing_id)
    else:
        return HttpResponseRedirect(reverse(reverse_method))

# Function for listers to close their listings
def close_listing(request, listing_id):
    # Get Listing ID information from the Listing model
    listing = Listing.objects.get(id=listing_id)

    # if the user is the lister of the listing, then do this
    if request.user == listing.lister:
        # If the user is the lister, and the amount of bids is greater than 0, then close the listing and save the most current bidder as the buyer
        if len(Bids.objects.filter(auction=listing).values_list('user')) > 0:
            listing.open_listing = False
            listing.buyer = Bids.objects.filter(auction=listing).last().user
            listing.save()
            return HttpResponseRedirect(reverse("listing", args = [listing_id]))
        # Otherwise, because there are no bidders, then close the listing and doing nothing about information regarding a buyer
        else:
            listing.open_listing = False
            listing.save()
            return HttpResponseRedirect(reverse("listing", args = [listing_id]))
            
    return HttpResponseRedirect(reverse("listing"))