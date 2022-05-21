from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Bid, Comment, Listing, User, Watch, Closed_listing
from django.forms.models import model_to_dict


def index(request):
    listings = Listing.objects.all()
    bids = []
    message = False
    user = request.user
    for listing in listings:
        bids.append(Bid.objects.filter(listing=listing).last())
    
    # See if this user won an auction
    closed_listings = Closed_listing.objects.all()
    for closed_listing in closed_listings:
        if closed_listing.last_bid_user == user.username:
            message = f"You Won the Auction for {(closed_listing.title).capitalize()}, now you just need to pay USD {closed_listing.value} and {closed_listing.user_who_created} will send you your purchase!"
        break

    return render(request, "auctions/index.html", {
        "listings": listings,
        "bids": bids,
        "message":  message,
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
        starting_bid = float(request.POST["starting_bid"].replace(",", "."))
        url = request.POST["url"]
        l = Listing(user=request.user, title=title, description=description, url=url,
                     category=category)
        l.save()
        b = Bid(user=request.user, value=starting_bid, listing=l)
        b.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html")


def listing(request, id):
    current_listing = Listing.objects.get(id=id)
    user = request.user
    user = None if not user.is_authenticated else user
    message = False
    watch_list_user = Watch.objects.filter(user=user, listing=current_listing)
    comments = Comment.objects.filter(listing=current_listing)
    bids = Bid.objects.filter(listing=current_listing)
    start_bid, last_bid = bids.first(), bids.last()
    if request.method == "POST":
        if "bid" in request.POST:
            bid_value = float(request.POST["bid"].replace(",", "."))
            if float(bid_value) > last_bid.value:
                bid = Bid(user=user, value=bid_value, listing=current_listing)
                bid.save()
                last_bid = bid
                message = False
            else:
                message = True
        if "comment" in request.POST:
            comment = request.POST["comment"]
            c = Comment(username=user, comment=comment, listing=current_listing)
            c.save()
        if "watchlist" in request.POST:
            w = Watch(listing=current_listing, user=user)
            w.save()
        if "remove_watchlist" in request.POST:
            watch_list_user.first().delete()
        if "close" in request.POST:
            last_bid = Bid.objects.filter(listing=current_listing).last()
            closed_listing = Closed_listing(user_who_created=current_listing.user.username, last_bid_user=last_bid.user.username, title=current_listing.title, value=last_bid.value)
            closed_listing.save()
            current_listing.delete()
            return HttpResponseRedirect(reverse("index"))

    on_watch_list = True if len(watch_list_user) == 1 else False
    
    return render(request, "auctions/listing.html", {
        "current_listing": current_listing,
        "bids": bids,
        "last_bid": last_bid,
        "comments": comments,
        "user": user,
        "on_watch_list": on_watch_list,
        "message": message,
        "start_bid": start_bid,
    })


def watchlist(request):
    w_list = Watch.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "w_list": w_list
    })


def categories(request, category):
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "listings": listings
    })
