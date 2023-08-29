from django.contrib import admin

from .models import Category, Campaign, Comment, Contribution

@admin.register(Category)# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display=('id', 'name', 'description')




@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display=('id', 'name', 'description')
    list_filter=('category',)


@admin.register(Comment)# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    list_display=('id', 'comment_text', 'date', 'campaign','user')



@admin.register(Contribution)# Register your models here.
class ContributionAdmin(admin.ModelAdmin):
    list_display=('id', 'amount', 'date', 'campaign','user')