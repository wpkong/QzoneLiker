from django.contrib import admin
from models import LikerConfig,AlreadyLiked
# Register your models here.

class AlreadyLikedAdmin(admin.ModelAdmin):
    list_display = ['mood_id','time']

class LikeConfigAdmin(admin.ModelAdmin):
    list_display = ['qq','cookie']

admin.site.register(LikerConfig,LikeConfigAdmin)
admin.site.register(AlreadyLiked,AlreadyLikedAdmin)
