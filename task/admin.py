from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Game)
admin.site.register(User)
admin.site.register(Rating)
admin.site.register(Feedback)