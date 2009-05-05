from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from models import UserProfile

admin.site.unregister(User)
admin.site.unregister(Group)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class MyUserAdmin(UserAdmin):
    inlines = [UserProfileInline,]

admin.site.register(User, MyUserAdmin)

