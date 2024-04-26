from django.urls import path
from . import views


urlpatterns = [
    path("search", views.search_results, name="search_results"),
    path("show-more", views.search_results_show_more, name="logShowMore"),
    path("link-click", views.linkClick, name="logLinkClick"),
]
