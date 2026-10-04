from django.shortcuts import render, redirect
from django.http import JsonResponse
from location.models import City, Province


# Create your views here.
def set_city(request):
    provinces = Province.objects.order_by("name")
    cities = City.objects.order_by("name")
    
    if request.method == "POST":
        city = City.objects.filter(id=request.POST.get("city_id")).first()

        if not city:
            return redirect("location:set_city")

        request.session["city_id"] = city.id
        request.session["city_name"] = city.name
        return redirect("listing:list_page")

    selected_city = (
        City.objects.select_related("province")
        .filter(id=request.session.get("city_id"))
        .first()
    )
    
    context = {
        "provinces": provinces,
        "cities": cities,
        "selected_city": selected_city,
        }

    return render(request, "select_city.html", context)