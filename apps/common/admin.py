from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class ProjectUserAdmin(UserAdmin):
    def __init__(self, *args):
        super().__init__(*args)
        self.fieldsets = (*self.fieldsets, ("Voting App settings", {"fields": ['numberOfVotes']}))


admin.site.register(User, ProjectUserAdmin)
