from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Bids, Comments, Listings, User, Watch


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all()
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


def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        category = request.POST["category"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        url = request.POST["url"]
        l = Listings(user=request.user, title=title, description=description, url=url,
                     category=category, starting_bid=starting_bid)
        l.save()
        return render(request, "auctions/index.html", {
            "listings": Listings.objects.all()
        })
    return render(request, "auctions/create.html")


def listing(request, id):
    item = Listings.objects.get(id=id)
    user = request.user
    user = None if not user.is_authenticated else user
    message = False
    watch_list_user = Watch.objects.filter(user=user, listing=item)
    bids = Bids.objects.filter(listing=item)
    last_bid = bids.last()
    if request.method == "POST":
        if "bid" in request.POST:
            bid_value = request.POST["bid"]
            if last_bid is None:
                if float(bid_value) > float(item.starting_bid):
                    bid = Bids(user=user, bid=bid_value, listing=item)
                    bid.save()
                    message = False
                else:
                    message = True
            elif float(bid_value) > float(last_bid.bid):
                bid = Bids(user=user, bid=bid_value, listing=item)
                bid.save()
                message = False
            else:
                message = True
        if "comment" in request.POST:
            comment = request.POST["comment"]
            c = Comments(username=user, comment=comment, listing=item)
            c.save()
        if "watchlist" in request.POST:
            w = Watch(listing=item, user=user)
            w.save()
        if "remove_watchlist" in request.POST:
            watch_list_user.first().delete()
        if "close" in request.POST:
            item.delete()
            return HttpResponseRedirect(reverse("index"))
    bids = Bids.objects.filter(listing=item)
    last_bid = bids.last()
    lenght_bids = len(bids)
    comments = Comments.objects.filter(listing=item)
    if len(watch_list_user) == 1:
        on_watch_list = True
    else:
        on_watch_list = False
    return render(request, "auctions/listing.html", {
        "item": item,
        "bids": bids,
        "last_bid": last_bid,
        "comments": comments,
        "user": user,
        "on_watch_list": on_watch_list,
        "message": message,
        "lenght_bids": lenght_bids,
    })


def watchlist(request):
    w_list = Watch.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "w_list": w_list
    })


def categories(request, category):
    listings = Listings.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "listings": listings
    })
