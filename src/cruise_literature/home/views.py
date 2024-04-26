from django.shortcuts import render


def home(request):
    """
    Home page
    """
    if request.method == "GET":
        return render(
            request,
            #"interfaces/home.html",
            "interfaces/home_search.html",
        )


def about(request):
    """
    About page
    """
    if request.method == "GET":
        return render(
            request,
            "interfaces/about.html",
        )

