from cms.models.pagemodel import Page
from django.shortcuts import redirect
from .models import PageRating


def update_page_rating(request):
    if request.method == 'POST':
        rating = int(request.POST.get("rating", ""))
        page_id = int(request.POST.get("page_id", ""))
        return_url = request.POST.get("return_url", "")
        page = Page.objects.get(pk=page_id)
        page_rating, created = PageRating.objects.get_or_create(page_obj=page)
        page_rating.update_rating_average(rating)
        return redirect(return_url)
