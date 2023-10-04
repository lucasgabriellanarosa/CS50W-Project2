from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required

from .models import User


def index(request):
    allActiveListings = Listing.objects.filter(isActive=True).order_by('title')

    return render(request, "auctions/index.html", {
        'allActiveListings': allActiveListings
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

@login_required
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


def listing_page(request, id):
    if request.method == 'GET':
        listing = Listing.objects.get(pk=id)
        currentUser = request.user 

        if currentUser == listing.owner:
            is_currentUser_owner = True
        else:
            is_currentUser_owner = False

        try:
            if listing in currentUser.listingWatchlist.all():
                listing_is_in_userWatchlist = True
            else:
                listing_is_in_userWatchlist = False
        except:
            listing_is_in_userWatchlist = None

        allListingComments = Comment.objects.filter(listing=listing)

        highest_bid_user = listing.bid.user


        return render(request, 'auctions/listing_page.html', {
            'listing': listing,
            'is_currentUser_owner': is_currentUser_owner,
            'listing_is_in_userWatchlist': listing_is_in_userWatchlist,
            'allListingComments': allListingComments,
            'highest_bid_user': highest_bid_user,
            'currentUser': currentUser,
        })


@login_required
def new_listing(request):
    if request.method == 'GET':
        allCategories = Category.objects.all().order_by("categoryName")
        return render(request, 'auctions/new_listing.html', {
            'allCategories': allCategories
        })
    else:
        title = request.POST['title']
        description = request.POST['description']
        imageUrl = request.POST['imageUrl']
        price = request.POST['price']
        category_post = request.POST['category']
        owner = request.user

        category = Category.objects.get(categoryName=category_post)

        newBid = Bid(
            user=request.user,
            bid=price
        )
        newBid.save()

        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageUrl,
            price=price, 
            bid=newBid,
            category=category,
            owner=owner
            )

        newListing.save()

        allActiveListings = Listing.objects.filter(isActive=True).order_by('title')


        return render(request, 'auctions/index.html', {
            'allActiveListings': allActiveListings
        })


def categories_page(request):
    allCategories = Category.objects.all().order_by('categoryName')

    return render(request, 'auctions/categories_page.html', {
        'allCategories': allCategories
    })


def category_page(request, id):
    category = Category.objects.get(pk=id)
    active_listings_in_category = Listing.objects.filter(category=category, isActive=True).order_by('title')

    return render(request, 'auctions/category.html', {
        'active_listings_in_category': active_listings_in_category,
        'category': category
    })


@login_required
def close_action(request, id):
    listing = Listing.objects.get(pk=id)

    if request.user == listing.owner:

        listing.isActive = False

        listing.save()

        return HttpResponseRedirect(reverse("listing_page", args=[id, ]))


@login_required
def watchlist(request):
    if request.method == 'GET':
        currentUser = request.user
        userWatchlist = currentUser.listingWatchlist.all()
        return render(request, 'auctions/watchlist.html', {
            'userWatchlist': userWatchlist,
            'currentUser': currentUser
        })


@login_required
def add_to_watchlist(request,id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=id)
        currentUser = request.user
        listing.watchlist.add(currentUser)
        return HttpResponseRedirect(reverse("listing_page", args=[id, ]))


@login_required
def remove_from_watchlist(request,id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=id)
        currentUser = request.user
        listing.watchlist.remove(currentUser)
        return HttpResponseRedirect(reverse("listing_page", args=[id, ]))


@login_required
def add_comment(request, id):
    if request.method == 'POST':
        comment_input = request.POST['comment_input']
        currentUser = request.user
        listing = Listing.objects.get(pk=id)

        newComment = Comment(
            author=currentUser,
            listing=listing,
            message=comment_input
        )
        newComment.save()
        return HttpResponseRedirect(reverse("listing_page", args=[id, ]))


@login_required
def add_bid(request, id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=id)
        bid_input = request.POST['bid_input']
        
        newBid = Bid(
            bid=bid_input,
            user=request.user
        )

        if int(newBid.bid) > listing.bid.bid and int(newBid.bid) >= listing.price:
            listing.bid.delete()
            newBid.save()
            listing.bid = newBid
            listing.save()

            return HttpResponseRedirect(reverse("listing_page", args=[id, ]))

        else: 
            return render (request, 'auctions/error_message.html', {
                'error_message': "The bid must be at least as large as the starting bid, and must be greater than the highest actual bid."
            })
