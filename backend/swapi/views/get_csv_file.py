from datetime import datetime

from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods

import petl

from swapi.models import CsvFile

HEADERS = [
    "name", "height", "mass", "hair_color", "skin_color",
    "eye_color", "birth_year", "gender", "homeworld", "edited_at",
]

def _timestamp_to_date(row):
    dt = datetime.fromtimestamp(float(row.edited_at))
    return f"{dt.year}-{dt.month}-{dt.day}"

@require_http_methods(["GET"])
def get_csv_file(request, file_id=None):
    count = int(request.GET.get("count", 10) or 10)
    offset = int(request.GET.get("offset", 0) or 0)
    if count > 20:
        count = 20
    elif count < 1:
        count = 1

    if offset < 0:
        offset = 0

    fields = request.GET.get("fields")
    if fields:
        fields = fields.split(",")
    else:
        fields = []
    
    try:
        # Read from database first, we don't want to access
        # filesystem with arbitrary user input.
        csv_file = CsvFile.objects.get(filename=file_id)
    except CsvFile.DoesNotExist:
        raise Http404()

    folder = settings.SWAPI_SETTINGS.CSV_DIR
    full_file = folder / file_id

    table = (petl
        .fromcsv(full_file)
        .pushheader(HEADERS)
        .addfield("date", _timestamp_to_date)
        .cutout("edited_at"))

    if fields:
        table = (table
            .aggregate(fields, len)
            .rename("value", "count"))
        final_fields = list(fields)
        final_fields.append("count")
    else:
        final_fields = list(HEADERS)
        final_fields.pop()
        final_fields.append("date")
        table = table.rowslice(offset, offset + count)

    return JsonResponse({
        "headers": final_fields,
        "data": list(table[1:])})
