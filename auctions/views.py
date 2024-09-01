from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Categories, Watchlist
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


def listing(request, listing_id):
    if request.method == "POST":
        try:
            current_user = request.user
            listing = Listing.objects.get(pk=listing_id)
        except KeyError:
            return HttpResponseBadRequest("Bad Request")
        watchlist = Watchlist.objects.create(user_watching=current_user)
        watchlist.listings_watched.add(listing)
        watchlist.save()
        print(watchlist)
        print(watchlist.listings_watched)
        return render(request, "auctions/listing.html", {"listing": listing})

    else:
        listing = Listing.objects.get(pk=listing_id)
        return render(request, "auctions/listing.html", {
            "listing": listing
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
