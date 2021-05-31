from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listings, Bids, Comments, Watchlist


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all().filter(active=True)
    })

def inactive(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all().filter(active=False)
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

@login_required
def newlisting(request):
    if request.method == "POST":
        formInput = NewListingForm(request.POST)
        current_user = request.user
        if formInput.is_valid():
            title = formInput.cleaned_data["title"]
            description = formInput.cleaned_data["description"]
            bid = formInput.cleaned_data["bid"]
            imgurl = formInput.cleaned_data["imgurl"]
            category = formInput.cleaned_data["category"]
            saveBid = Bids(bidderid=current_user.id, bid=bid)
            saveBid.save()
            listing = Listings(
                title=title, 
                description=description, 
                imgurl=imgurl, 
                listing_bid=saveBid, 
                category=category.lower(),
                ownerid = current_user.id,
                winnerid = current_user.id,
                active = True
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/newlisting.html", {
            "form": NewListingForm
        })

def if_in_watchlist(userid, listingid):
    listing = Listings.objects.filter(id = listingid).first()
    watchlist = Watchlist.objects.filter(userid = userid , listingid=listingid).first()
    if watchlist != None:
        if listingid == int(watchlist.listingid):
            inwatchlist = "Remove from watchlist"
    else:
        inwatchlist = "Add to watchlist"
    return inwatchlist

def listing(request, listingid):
    listing = Listings.objects.filter(id = listingid).first()
    comments = Comments.objects.all().filter(listing_id=listing)
    current_user = request.user
    watchlist = Watchlist.objects.filter(userid = current_user.id, listingid=listingid).first()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "inwatchlist": if_in_watchlist(current_user.id, listingid),
        "bidform": BidForm,
        "commentform": CommentForm
    })

def watchlist(request, listingid):
    if request.method == "POST":
        current_user = request.user
        watchlist = Watchlist.objects.filter(userid = current_user.id, listingid=listingid).first()
        if watchlist != None:
            if listingid == int(watchlist.listingid):
                Watchlist.objects.filter(userid = current_user.id, listingid=listingid).delete()
        else:
            watchlist_item = Watchlist(userid = current_user.id, listingid=listingid)
            watchlist_item.save()
    return HttpResponseRedirect(reverse("listing", args=(listingid,)))

def bid(request, listingid):
    if request.method == "POST":
        current_user = request.user
        formInput = BidForm(request.POST)
        if formInput.is_valid():
            bid = formInput.cleaned_data["bid"]
        listing = Listings.objects.filter(id=listingid).first()
        comments = Comments.objects.all().filter(listing_id=listing)
        if bid <= listing.listing_bid.bid:
            message = "Your bid must be bigger than the current bid"
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "bidform": BidForm,
                "commentform": CommentForm,
                "inwatchlist": if_in_watchlist(current_user.id, listingid),
                "message": message
            })
        else:
            listing.listing_bid.bidderid = current_user.id
            listing.listing_bid.bid = bid
            listing.listing_bid.save()
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "inwatchlist": if_in_watchlist(current_user.id, listingid),
            "bidform": BidForm,
            "commentform": CommentForm
        })

def closelisting(request, listingid):
    if request.method == "POST":
        current_user = request.user
        listing = Listings.objects.filter(id=listingid, ownerid=current_user.id).first()
        winnerid = listing.listing_bid.bidderid
        listing.active = False
        listing.winnerid = winnerid
        listing.save()
        return HttpResponseRedirect(reverse("index"))

def comment(request, listingid):
    if request.method == "POST":
        current_user = request.user
        listing = Listings(id=listingid)
        formInput = CommentForm(request.POST)
        if formInput.is_valid():
            cmt = Comments(
                commenterName=current_user.username,
                comment=str(formInput.cleaned_data["comment"]),
                listing_id=listing
            )
            cmt.save()
        return HttpResponseRedirect(reverse("listing", args=(listingid,)))

@login_required
def showwatchlist(request):
    current_user = request.user
    items = Watchlist.objects.all().filter(userid=current_user.id)
    items_ids = []
    for x in items:
        items_ids.append(x.listingid)
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all().filter(id__in=items_ids)
    })

def showcategories(request):
    listing = Listings.objects.all()
    cats = []
    for x in listing:
        if x.category.lower() not in cats:
            cats.append(x.category.lower())
    return render(request, "auctions/categories.html", {
        "categories": cats
    })

def showlistingbycat(request, category):
    return render(request, "auctions/index.html", {
            "listings": Listings.objects.all().filter(category=category)
    })

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title:")
    description = forms.CharField(label="Description:", widget=forms.Textarea)
    bid = forms.FloatField(label="Starting bid:")
    imgurl = forms.URLField(label="Image URL:", required=False)
    category = forms.CharField(label="Category:", required=False)

class BidForm(forms.Form):
    bid = forms.FloatField(label="Place bid:")

class CommentForm(forms.Form):
    comment = forms.CharField(label="Leave comment:", widget=forms.Textarea)