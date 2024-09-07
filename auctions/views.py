from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Categories, Watchlist, Bids
from django.contrib.auth.decorators import login_required
from django.db.models import Max


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


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    watchlist = 0
    highest_bid = 0
    is_user_highest_bidder = 0
    next_bid = listing.starting_bid + 1
    all_bids = Bids.objects.filter(bid_listing=listing_id)
    highest_bid = all_bids.aggregate(Max('bid', default=0))
    highest_bid = highest_bid['bid__max']
    if request.user.is_authenticated == True:
        if highest_bid > next_bid:
            next_bid = highest_bid + 1
            is_user_highest_bidder = Bids.objects.filter(
                bid_listing=listing_id, bid_user=request.user, bid=highest_bid)
        watchlist = Watchlist.objects.filter(
            user_watching=request.user.id, listing_watching=listing).exists()
    return render(request, "auctions/listing.html", {
        "listing": listing, "watchlist": watchlist, "highest_bid": highest_bid, "next_bid": next_bid, "is_user_highest_bidder": is_user_highest_bidder
    })


class AddListing(forms.Form):
    title = forms.CharField(max_length=64, label="Title")
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'textarea_description'}), label="Description")
    starting_bid = forms.IntegerField(label="Starting bid")
    image = forms.ImageField(label="Image")
    categories = forms.ModelMultipleChoiceField(
        queryset=Categories.objects.all())


@login_required(login_url='login')
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
            print(listed_createdby)
            listing = Listing.objects.create(
                title=title, description=description, starting_bid=starting_bid, image=image, listed_by=listed_createdby)
            listing.categories.set(categories)
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    else:
        return render(request, "auctions/add.html", {
            "form": AddListing()
        })


@login_required(login_url='login')
def bid(request):
    if request.method == "POST":
        new_bid = int(request.POST.get('new_bid'))
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        all_bids = Bids.objects.filter(bid_listing=listing_id)
        highest_bid = all_bids.aggregate(Max('bid', default=0))
        highest_bid = highest_bid['bid__max']
        if new_bid > highest_bid:
            Bids.objects.create(bid=new_bid,
                                bid_user=request.user, bid_listing=listing)
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else:
            message = "Your bid is smaller than current bid or not valid."
            print(message)
            #  erro message?
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)), {"message": message})
    else:
        all_user_bids = Bids.objects.filter(bid_user=request.user)
        # show only the highest bid of each item
        # all_bids = Bids.objects.filter(bid_listing=listing_id)
        # highest_bid = all_bids.aggregate(Max('bid', default=0))
        # highest_bid = highest_bid['bid__max']
        return render(request, "auctions/bid.html", {"all_user_bids": all_user_bids})


@login_required(login_url='login')
def watchlist(request):
    if request.method == "POST":
        current_user = request.user
        listing = Listing.objects.get(pk=request.POST.get('listing_id'))
        watchlist_exists = Watchlist.objects.filter(
            user_watching=current_user, listing_watching=listing).exists()
        if watchlist_exists == True:
            watchlist = Watchlist.objects.get(listing_watching=listing)
            watchlist_id = watchlist.id
            Watchlist.objects.get(id=watchlist_id).delete()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        else:
            watchlist = Watchlist.objects.create(
                user_watching=current_user, listing_watching=listing)
            print(watchlist)
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    else:
        user_is_watching = Watchlist.objects.filter(
            user_watching=request.user)
        return render(request, "auctions/watchlist.html", {"watchlist": user_is_watching})
