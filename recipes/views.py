from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

headers = {
    "X-RapidAPI-Key": "a2902d5316msh18425308907ed14p12fb8cjsn00f739bb744d",
    "X-RapidAPI-Host": "yummly2.p.rapidapi.com"
}


@csrf_exempt
def yummly_autocomplete(request):
    # Check for a query parameter in the request
    query = request.GET.get('query', '')

    # Define the URL and the headers required by the Yummly2 API
    url = "https://yummly2.p.rapidapi.com/feeds/auto-complete"


    # Send a request to the Yummly2 API
    response = requests.get(url, headers=headers, params={"q": query})

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response to JSON
        data = response.json()
        # Return the JSON data as a JsonResponse
        return JsonResponse(data, safe=False)
    else:
        # If the request was not successful, return an error message
        return JsonResponse({"error": "Failed to fetch data from Yummly2 API"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def yummly_search(request):
    query = request.GET.get('q', '')
    start = request.GET.get('start', '0')
    maxResults = request.GET.get('maxResults', '18')
    url = "https://yummly2.p.rapidapi.com/feeds/search"
    params = {
        "q": query,
        "start": start,
        "maxResult": maxResults,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from Yummly2 API", "status_code": response.status_code}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def yummly_feeds_list(request):
    start = request.GET.get('start', '0')
    limit = request.GET.get('limit', '24')
    tag = request.GET.get('tag', '')

    url = "https://yummly2.p.rapidapi.com/feeds/list"

    params = {
        "start": start,
        "limit": limit,
        "tag": tag
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from Yummly2 API", "status_code": response.status_code}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])  # Only allow GET requests for this view
def get_list_similarities(request):
    url = "https://yummly2.p.rapidapi.com/feeds/list-similarities"
    params = request.GET.dict()

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from the API", "status_code": response.status_code},
                                status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_categories_list(request):

    url = "https://yummly2.p.rapidapi.com/categories/list"
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, safe=False)
        else:

            return JsonResponse({"error": "Failed to fetch data from Yummly2 API", "status_code": response.status_code}, status=response.status_code)
    except requests.exceptions.RequestException as e:

        return JsonResponse({"error": str(e)}, status=500)