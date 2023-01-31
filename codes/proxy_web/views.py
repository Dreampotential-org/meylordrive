from rest_framework.response import Response
from django.http import HttpResponse

from rest_framework.views import APIView
import mimetypes
# Create your views here.

def get_domain(request, resource):
    # print(request)
    # print(dir(request))
    # print(resource)
    # print (request.headers)
    # print (request.META)

    path = request.path

    domain_name = request.META['HTTP_HOST'].split(":")[0]
    print(domain_name)
    # xxx todo based on host path implement logic here
    directory = "/home/jj/useiam/www/"

    # implement logic to load file from system and return response to request

    f = open(directory + path, "rb")

    content_type = mimetypes.guess_type(directory + path)[0]

    return HttpResponse(f.read(), content_type=content_type)


