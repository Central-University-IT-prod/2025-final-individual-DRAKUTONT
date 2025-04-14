from django.contrib import admin

from advertisers import models

admin.site.register(models.Advertiser)
admin.site.register(models.Targeting)
admin.site.register(models.Campaign)
admin.site.register(models.Click)
admin.site.register(models.Impression)

