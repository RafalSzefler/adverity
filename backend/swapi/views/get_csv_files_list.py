from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from swapi.models import CsvFile


@require_http_methods(["GET"])
def get_csv_files_list(request):
    result = []
    for csv_file in CsvFile.objects.order_by('-created_at'):
        result.append(csv_file.as_dict())
    return JsonResponse({"data": result})
