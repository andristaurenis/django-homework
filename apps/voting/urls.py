from django.urls import path
from django.http import HttpResponse
import json

from . import views


def rest(get=None, post=None, put=None, delete=None, patch=None):
    def method_switch(req, *args, **kwargs):
        if req.body:
            setattr(req, 'json', json.loads(req.body))
        if req.method == "GET" and get:
            return get(req, *args, **kwargs)
        if req.method == "POST" and post:
            return post(req, *args, **kwargs)
        if req.method == "PUT" and put:
            return put(req, *args, **kwargs)
        if req.method == "DELETE" and delete:
            return delete(req, *args, **kwargs)
        if req.method == "PATCH" and patch:
            return patch(req, *args, **kwargs)
        return HttpResponse(status_code=400)
    return method_switch


urlpatterns = [
    path('', views.index, name='index'),
    path('restaurants', rest(
        get=views.getRestaurants,
        post=views.addRestaurant)),
    path('restaurants/<int:restaurantId>', rest(
        get=views.getRestaurants,
        put=views.editRestaurant,
        delete=views.deleteRestaurant)),
    path('vote/<int:restaurantId>', views.voteForRestaurant),
    path('endVoting', views.finalizeRestaurantChoice),
    path('restaurantChoiceHistory', views.getRestaurantChoiceHistory),
]
