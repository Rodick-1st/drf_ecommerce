from django.contrib import admin
from .models import User
from django.contrib.auth import get_user_model

admin.site.register(get_user_model())