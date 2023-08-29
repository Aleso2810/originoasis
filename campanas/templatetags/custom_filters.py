from django import template

register = template.Library()

@register.filter
def has_donated(campaign, user):
    return campaign.contribution_set.filter(user=user).exists()
