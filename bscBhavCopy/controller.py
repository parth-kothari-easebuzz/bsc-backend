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
            resopnse = self.bhav_copy_operation_service.parse_records(file)
            return resopnse
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_bhav_copy_records(self, request, id=None):
        try:
            response = self.bhav_copy_operation_service.get_file_records(request,id)
            return response               
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def update_bhav_copy_record(self, request, id) :
        try:
           response = self.bhav_copy_operation_service.update_record(request,id)
           return response
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete_bhav_copy_record(self, request, id):
        try:
            response = self.bhav_copy_operation_service.delete_record(id)
            return response
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def export_bhav_copy_by_search(self, request):
        try:
            response = self.bhav_copy_operation_service.export_sheet_by_search_result(request)
            return response
        except Exception as e:
            return Response({"message":f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def download_bhav_copy_by_date(self,request):
        try:
            response = self.bhav_copy_operation_service.download_sheet_by_date(request)
            return response
        except Exception as e:
            return Response({"message" : f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)