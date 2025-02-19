from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status 
from rest_framework import viewsets

from bscBhavCopy.services import BhavCopyOperationService



# BhavCopyOperations is used for parse data into the database, 
# More it has methods for get the records, update record and delete the record.

# ViewSet is map the url by urls and it's action method. where as APPView is directly fetch
#  the method by the method name defined in class (Compulsory defined method get,post,put,delete,patch)
class BhavCopyOperationController(viewsets.ViewSet):
    
    def __init__(self):
        self.bhav_copy_operation_service = BhavCopyOperationService()

        pass
    # Store the excel files record into the db
    def parse_records_from_bhav_copy(self, request):
        try:
            file = request.FILES.get('file')

            if not file:
                return Response({"error" : "No file uploded." }, status=status.HTTP_400_BAD_REQUEST)
            
            if not file.name.lower().endswith('.csv'):
                return Response({"error": "Invalid file type. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)
            
            # bhav_copy_operation_service = BhavCopyOperationService()
            response = self.bhav_copy_operation_service.parse_records(file)
            return Response({"message" : response["message"], "status" : response['status']})
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_bhav_copy_records(self, request, id=None):
        try:

            search = request.GET.get('search', '').strip() 
            page_size = int(request.GET.get('size', 10))
            page_number = int(request.GET.get('page', 1))
            response = self.bhav_copy_operation_service.get_file_records(search, page_size, page_number,id)
            return Response({"message" : response["message"], "status" : response['status']})
             
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def update_bhav_copy_record(self, request, id) :
        try:
           data = request.data
           response = self.bhav_copy_operation_service.update_record(data,id)
           return Response({"message" : response["message"], "status":response['status']})

        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete_bhav_copy_record(self, request, id):
        try:
            response = self.bhav_copy_operation_service.delete_record(id)
            return Response({"message" : response["message"], "status" : response['status']})

        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def export_bhav_copy_by_search(self, request):
        try:
            search = request.GET.get('search', '').strip()
            response = self.bhav_copy_operation_service.export_sheet_by_search_result(search)
            
            # Create HTTPResponse with text/csv content 
            response = HttpResponse(response, content_type='text/csv')

            # Inspect -> Header triggered for download the file otherwise it can lead some issue while download file
            # Content-Disposition -> used for how to handle the response content
            # attachment is says that download file instead of showing result
            response['Content-Disposition'] = 'attachment; filename=search_results.csv'
            return response 
        except Exception as e:
            return Response({"message":f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def download_bhav_copy_by_date(self,request):
        try:
            date = request.GET.get('date')
            result = self.bhav_copy_operation_service.download_sheet_by_date(date)
           
            if "error" in result:
                    return Response({"message": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

            response = HttpResponse(result["csv_data"], content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="BhavCopy_{date}.csv"'
            return response

        except Exception as e:
            return Response({"message" : f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)