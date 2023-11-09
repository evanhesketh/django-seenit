from django.contrib import admin
from .models import User, Channel, Post, Comment


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)


admin.site.register(User, UserAdmin)
admin.site.register(Channel)
admin.site.register(Post)
admin.site.register(Comment)
