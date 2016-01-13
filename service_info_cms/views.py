from cms.models.pagemodel import Page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render
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


def page_ratings(request):
    """Listing of all page ratings."""
    pr_list = PageRating.objects.all()
    paginator = Paginator(pr_list, 20)
    page = request.GET.get('page')
    try:
        ratings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ratings = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ratings = paginator.page(paginator.num_pages)
    return render(request, 'cms/page_ratings/page-ratings.html', {"ratings": ratings})
