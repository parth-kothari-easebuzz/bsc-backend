from django.contrib import admin
from django.urls import path

from bscBhavCopy.controller import BhavCopyOperationController


urlpatterns = [
    path('upload-csv/', BhavCopyOperationController.as_view({
        'post':'parse_records_from_bhav_copy'
    })),

    path('get-csv-record/<int:id>/', BhavCopyOperationController.as_view({
        'get':'get_bhav_copy_records'
    })),
   
    path('get-csv-record/', BhavCopyOperationController.as_view({
        'get': 'get_bhav_copy_records'
    })),
    path('update-csv-record/<int:id>/', BhavCopyOperationController.as_view({
        'put':'update_bhav_copy_record'
    })),
    path('remove-csv-record/<int:id>/', BhavCopyOperationController.as_view({
        'delete':'delete_bhav_copy_record'
    })),
    path('download/search-result/', BhavCopyOperationController.as_view({
        'get':'export_bhav_copy_by_search'
    })),
    path('download/bhav-copy/by-date/', BhavCopyOperationController.as_view({
        'get':'download_bhav_copy_by_date'
    }))

]