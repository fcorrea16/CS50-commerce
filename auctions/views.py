from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Categories, Watchlist, Bids
from django.contrib.auth.decorators import login_required


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


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    watchlist = Watchlist.objects.filter(
        user_watching=request.user, listing_watching=listing).exists()
    # current_bid = Listing.objects.get(current_bid=current_bid)
    highest_bid = 0
    next_bid = listing.starting_bid + 1
    # bid_min = listing.starting_bid + 1
    try:
        bid = Bids.objects.get(bid_listing=listing)
        highest_bid = bid.highest_bid
        next_bid = highest_bid + 1
    except:
        highest_bid = 0
        next_bid = listing.starting_bid + 1
        # bid_min = listing.starting_bid + 1
    return render(request, "auctions/listing.html", {
        "listing": listing, "watchlist": watchlist, "highest_bid": highest_bid, "next_bid": next_bid
    })


def bid(request):
    if request.method == "POST":
        new_bid = request.POST.get('new_bid')
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        print(new_bid)
        print(listing_id)
        print(listing)
        try:
            Bids.objects.filter(bid_listing=listing_id).exists()
            current_bid = Bids.objects.filter(bid_listing=listing_id)
            print(current_bid)
            if current_bid.highest_bid < new_bid:
                current_bid.objects.set(
                    highest_bid=new_bid, bid_user=request.user)
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                return HttpResponseBadRequest("Bad Request: current bid is bigger than your bid")
        except:
            # not sure why it's going here
            print("attribute error")
            Bids.objects.create(highest_bid=new_bid,
                                bid_user=request.user, bid_listing=listing)
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        return render(request, "auctions/bid.html", {"new_bid": new_bid, "listing": listing})


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
