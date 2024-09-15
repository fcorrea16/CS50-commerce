from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Categories, Watchlist, Bids, Listing_comments
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.core.exceptions import ValidationError


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Categories.objects.all()
    })


def category(request, category_id):
    category = Categories.objects.get(id=category_id)
    all_listings = Listing.objects.filter(categories=category_id)
    return render(request, "auctions/category.html", {
        "all_listings": all_listings, "category": category
    })


def listings(request):
    if request.method == "POST":
        listing_id = request.META.get('HTTP_REFERER')
        listing_id = listing_id.split('/', 4)[-1]
        listing = Listing.objects.get(pk=listing_id)
        post_status = request.POST.get('status-active')
        if post_status == "active":
            listing.active = False
            listing.save()
        else:
            listing.active = True
            listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        pass


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = Listing_comments.objects.filter(comment_listing=listing_id)
    listed_by_user = False
    watchlist = 0
    highest_bid = 0
    is_user_highest_bidder = 0
    next_bid = listing.starting_bid + 1
    all_bids = Bids.objects.filter(bid_listing=listing_id)
    highest_bid = all_bids.aggregate(Max('bid', default=0))
    highest_bid = highest_bid['bid__max']
    if request.user == listing.listed_by:
        listed_by_user = True
    if request.user.is_authenticated == True:
        if highest_bid > next_bid:
            next_bid = highest_bid + 1
    try:
        is_user_highest_bidder = Bids.objects.filter(
            bid_listing=listing_id, bid_user=request.user, bid=highest_bid)
    except:
        is_user_highest_bidder = 0
    watchlist = Watchlist.objects.filter(
        user_watching=request.user.id, listing_watching=listing).exists()

    if request.method == "POST":
        if request.POST.get('new_bid') == "":
            return render(request, "auctions/listing.html", {
                "listing": listing, "watchlist": watchlist, "highest_bid": highest_bid,
                "next_bid": next_bid, "is_user_highest_bidder": is_user_highest_bidder,
                "listed_by_user": listed_by_user, "comments": comments,
                "message": "Please fill out the form."
            })
        else:
            new_bid = int(request.POST.get('new_bid'))
            listing_id = request.META.get('HTTP_REFERER')
            listing_id = listing_id.split('/', 4)[-1]
            listing = Listing.objects.get(pk=listing_id)
            all_bids = Bids.objects.filter(bid_listing=listing_id)
            highest_bid = all_bids.aggregate(Max('bid', default=0))
            highest_bid = highest_bid['bid__max']
            if listing.starting_bid > highest_bid:
                if new_bid > listing.starting_bid:
                    Bids.objects.create(bid=new_bid,
                                        bid_user=request.user, bid_listing=listing)
                    listing.bid_counter += 1
                    listing.save()
                    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing, "watchlist": watchlist, "highest_bid": highest_bid,
                        "next_bid": next_bid, "is_user_highest_bidder": is_user_highest_bidder,
                        "listed_by_user": listed_by_user, "comments": comments,
                        "message": "Your bid is smaller than current bid or not valid."
                    })
            else:
                if new_bid > highest_bid:
                    Bids.objects.create(bid=new_bid,
                                        bid_user=request.user, bid_listing=listing)
                    listing.bid_counter += 1
                    listing.save()
                    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing, "watchlist": watchlist, "highest_bid": highest_bid,
                        "next_bid": next_bid, "is_user_highest_bidder": is_user_highest_bidder,
                        "listed_by_user": listed_by_user, "comments": comments,
                        "message": "Your bid is smaller than current bid or not valid."
                    })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing, "watchlist": watchlist, "highest_bid": highest_bid,
            "next_bid": next_bid, "is_user_highest_bidder": is_user_highest_bidder,
            "listed_by_user": listed_by_user, "comments": comments, "bid_counter": listing.bid_counter
        })


class AddListing(forms.Form):
    title = forms.CharField(max_length=64, label="Title", widget=forms.TextInput(
        attrs={'class': 'form-control', 'style': 'width: 500px;'}))
    starting_bid = forms.IntegerField(min_value=1, widget=forms.NumberInput(
        attrs={'class': 'textarea_description form-control', 'style': 'width: 300px;'}), label="Starting bid", )
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'textarea_description form-control'}), label="Description")
    image = forms.ImageField(label="Image")
    categories = forms.ModelMultipleChoiceField(
        label="Categories",
        queryset=Categories.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control custom-select'}))


class AddComment(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'textarea_comment'}), label="Comment")


@ login_required(login_url='login')
def add(request):
    if request.method == "POST":
        form = AddListing(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data['description']
            starting_bid = form.cleaned_data['starting_bid']
            image = request.FILES.get('image')
            categories = request.POST.get('categories')
            listed_createdby = request.user
            listing = Listing.objects.create(
                title=title, description=description, starting_bid=starting_bid, image=image, listed_by=listed_createdby)
            listing.categories.set(categories)
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    else:
        return render(request, "auctions/add.html", {
            "form": AddListing()
        })


@ login_required(login_url='login')
def bid(reques):
    pass


@ login_required(login_url='login')
def watchlist(request):
    current_user = request.user
    if request.method == "POST":
        listing_id = request.META.get('HTTP_REFERER')
        listing_id = listing_id.split('/', 4)[-1]
        listing = Listing.objects.get(pk=listing_id)
        watchlist_exists = Watchlist.objects.filter(
            user_watching=current_user, listing_watching=listing).exists()
        if watchlist_exists == True:
            watchlist = Watchlist.objects.filter(listing_watching=listing)
            watchlist.delete()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        else:
            watchlist = Watchlist.objects.create(
                user_watching=current_user, listing_watching=listing)
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    else:

        user_is_watching = Watchlist.objects.filter(
            user_watching=request.user)

        return render(request, "auctions/watchlist.html", {"watchlist": user_is_watching})


@ login_required(login_url='login')
def user(request, user_id):
    user_id = request.user.id
    my_listings = Listing.objects.filter(listed_by=user_id)
    return render(request, "auctions/user.html", {"user_id": user_id, "my_listings": my_listings})


def comment(request):
    if request.method == "POST":
        current_user = request.user
        listing_id = request.META.get('HTTP_REFERER')
        listing_id = listing_id.split('/', 4)[-1]
        listing = Listing.objects.get(pk=listing_id)
        comment = request.POST.get('comment')
        if not comment:
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        else:
            new_comment = Listing_comments.objects.create(
                comment_user=current_user, comment_listing=listing, comment=comment)
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
