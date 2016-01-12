
# from django.http import HttpResponseRedirect
from django.shortcuts import render

from cms.models.titlemodels import Title

from .models import PageRating


def update_page_rating(request):
    if request.method == 'POST':
        rating = int(request.POST.get("rating", ""))
        title_id = int(request.POST.get("title_id", ""))
        title = Title.objects.get(title_id=title_id)
        page_rating = PageRating.objects.get(page_title=title)
        page_rating.update_rating_average(rating)
        return render(request, '<h2>Thanks!</h2>')
    else:
        return render(request, '<h2>No rating specified</h2>')
