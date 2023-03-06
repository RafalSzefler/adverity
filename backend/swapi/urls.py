from django.urls import path, include
from swapi.views.fetch import fetch
from swapi.views.get_csv_file import get_csv_file
from swapi.views.get_csv_files_list import get_csv_files_list

urlpatterns = [
    path('fetch', fetch),
    path('csv_files', get_csv_files_list),
    path('csv_file/<file_id>', get_csv_file),
]
