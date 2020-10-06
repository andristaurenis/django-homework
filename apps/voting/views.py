from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
from django.forms.models import model_to_dict
from django.db.models import Q

from apps.voting.models import Restaurant, RestaurantChoiceHistory, Vote


def index(req):
    return render(req, 'base.html')


def addRestaurant(req):
    restaurantName = req.json["restaurantName"]
    restaurant = Restaurant.objects.create(creator=req.user, name=restaurantName)
    return JsonResponse(model_to_dict(restaurant), status=201)


def editRestaurant(req, restaurantId):
    newName = req.json["newName"]
    restaurant = get_object_or_404(Restaurant, pk=restaurantId)
    if restaurant.creator != req.user:
        return JsonResponse({"title": "You can only edit restaurants you create."}, status=401)
    restaurant.name = newName
    restaurant.save()
    return JsonResponse(model_to_dict(restaurant))


def deleteRestaurant(req, restaurantId):
    restaurant = get_object_or_404(Restaurant, pk=restaurantId, deletedAt__isnull=True)
    restaurant.deletedAt = now()
    restaurant.save()
    return JsonResponse({})


def getRestaurants(req, restaurantId=None):
    if not restaurantId:
        restaurants = Restaurant.objects.filter(deletedAt__isnull=True)
        return JsonResponse({"restaurants": list(map(model_to_dict, restaurants))})
    else:
        return JsonResponse(model_to_dict(get_object_or_404(Restaurant, pk=restaurantId)))


def voteForRestaurant(req, restaurantId):
    pendingChoice = RestaurantChoiceHistory.getPendingChoice()
    votesUsed = pendingChoice.vote_set.filter(user__pk=req.user.id).count()
    if not req.user.is_authenticated:
        return JsonResponse({"title": "Log in to vote."}, status=401)
    if votesUsed >= req.user.numberOfVotes:
        return JsonResponse({"title": "No more votes.", "numberOfVotes": req.user.numberOfVotes}, status=403)
    restaurant = get_object_or_404(Restaurant, pk=restaurantId)
    repeated = pendingChoice.vote_set.filter(user__pk=req.user.id, restaurant__pk=restaurantId).count()
    weight = Vote.WEIGHT.first if repeated == 0 else Vote.WEIGHT.second if repeated == 1 else Vote.WEIGHT.default
    pendingChoice.vote_set.create(restaurant=restaurant, user=req.user, weight=weight)
    return JsonResponse({"votesRemaining": req.user.numberOfVotes - votesUsed - 1})


def finalizeRestaurantChoice(req):
    RestaurantChoiceHistory.finalizeRestaurantChoice()
    return JsonResponse({})


def getRestaurantChoiceHistory(req):
    history = RestaurantChoiceHistory.objects.filter(~Q(id=1))
    historyJson = list(map(model_to_dict, history))
    for i, hist in enumerate(historyJson):
        hist["restaurant"] = model_to_dict(history[i].restaurant)
        hist["votes"] = list(map(model_to_dict, history[i].vote_set.all()))
    return JsonResponse({"history": historyJson})
