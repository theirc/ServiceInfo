from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

from django.core.urlresolvers import reverse_lazy, reverse

from .models import PageRating


def update_page_rating(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        title_id = request.POST.get("title_id", "")
        # create a form instance and populate it with data from the request:
        title = Title.objects.get()
        page_rating = PageRating.objects.get()
        return render(request, 'xxx.html', context)
