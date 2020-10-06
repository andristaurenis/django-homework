from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Sum
from apps.common.models import User
from django.utils.timezone import now
from collections import namedtuple


class Restaurant(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    deletedAt = models.DateTimeField(null=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{'(Deleted) ' if self.deletedAt else ''}{self.name}"


class RestaurantChoiceHistory(models.Model):
    """
    This table has a sentry row for the pending restaurant choice.
    """
    createdAt = models.DateTimeField('date published', default=now)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    @staticmethod
    def getPendingChoice():
        return RestaurantChoiceHistory.objects.get(pk=1)

    @staticmethod
    def finalizeRestaurantChoice():
        pendingChoice = RestaurantChoiceHistory.getPendingChoice()
        weights = (Restaurant.objects.filter(deletedAt__isnull=True, vote__restaurantChoiceHistory__pk=1)
                   .annotate(totalWeight=Sum("vote__weight"), count=Count("vote__pk"))
                   .order_by("-totalWeight", "-count"))
        if not weights:
            raise ValidationError("No votes have been submitted.")
        maxVoted = weights[0]
        newHist = RestaurantChoiceHistory.objects.create(restaurant=maxVoted.restaurant)
        allVotes = pendingChoice.vote_set.all()
        for vote in allVotes:
            vote.restaurantChoiceHistory_id = newHist.id
        Vote.objects.bulk_update(allVotes, ["restaurantChoiceHistory_id"])

    def __str__(self):
        return str(self.createdAt)


class Vote(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    restaurantChoiceHistory = models.ForeignKey(RestaurantChoiceHistory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.IntegerField()  # Using float can introduce a bug in the future.
    # Now it would not be a problem because 1, 0.5 and 0.25 are powers of 2.
    # Suppose there is a change from 0.25 to 0.2 then there is the following problem:
    #  >>> 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5 + 0.5
    #  7.0
    #  >>> 1   + 1   + 1   + 1   + 1   + 1   + 0.2 + 0.2 + 0.2 + 0.2 + 0.2
    #  7.000000000000001

    WEIGHT = namedtuple('Point', 'first second default')(10000, 5000, 2500)

    def clean(self):
        if self.weight not in Vote.WEIGHT:
            raise ValidationError(f"Weight should be one of {Vote.WEIGHT}")

    def __str__(self):
        return f"User={self.user} Restaurant={self.restaurant}"
