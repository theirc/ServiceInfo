from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

from cms.models.titlemodels import Title

from .models import PageRating


def update_page_rating(request):
    if request.method == 'POST':
        rating = int(request.POST.get("rating", ""))
        title_id = int(request.POST.get("title_id", ""))
        title = cms.Title.objects.get(title_id=title_id)
        page_rating = PageRating.objects.get(page_title=title)
        page_rating.num_ratings += 1
        page_rating.rating_total += rating
        page_rating.save(update_fields=["num_ratings", "rating_total"])
        return render(request, '<h2>Thanks!</h2>', context)
    else:
        return render(request, '<h2>No rating specified</h2>', context)
