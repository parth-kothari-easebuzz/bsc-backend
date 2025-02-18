import csv
from datetime import datetime
from decimal import Decimal
from io import StringIO, TextIOWrapper
from django.http import HttpResponse
import requests
from rest_framework import status 
from rest_framework.response import Response

from bscBhavCopy.models import BhavcopyRecord

from django.db import transaction
from bscBhavCopy.serializers import BhavcopyRecordSerializer


class BhavCopyOperationService():

    def parse_records(self, file):
        try:
            records = []
            
            # TextIOWrapper: is used for read the strings from file rather than byte stream.
            file_wrapper = TextIOWrapper(file, encoding='utf-8')

            # csv.DictReader which is used for csv file into the Python dict
            csv_reader = csv.DictReader(file_wrapper)
            
            required_headers = {"TradDt", "BizDt", "FinInstrmNm", "OpnPric", "HghPric", "LwPric", "ClsPric"}
            if not required_headers.issubset(csv_reader.fieldnames):
                raise ValueError("Missing required headers")
        
            for row in csv_reader:
                record = BhavcopyRecord(
                    trad_date = datetime.strptime(row.get('TradDt', ''), '%Y-%m-%d').date() if row.get('TradDt')  else None,
                    biz_date = datetime.strptime(row.get('BizDt'), '%Y-%m-%d').date() if row.get('BizDt')  else None,
                    name = row.get('FinInstrmNm'),
                    open_price = Decimal(row.get('OpnPric', 0)).quantize(Decimal('0.00')),
                    high_price=Decimal(row.get('HghPric', 0)).quantize(Decimal('0.00')),
                    low_price=Decimal(row.get('LwPric', 0)).quantize(Decimal('0.00')),
                    close_price=Decimal(row.get('ClsPric', 0)).quantize(Decimal('0.00'))
                )
                records.append(record)

            with transaction.atomic():
                BhavcopyRecord.objects.bulk_create(records)
                
            return Response({"message": f"{len(records)} records successfully saved."}, status=status.HTTP_201_CREATED)
    
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_file_records(self, request=None, id=None):
        try:
            if id:
                bhavcopy_record = BhavcopyRecord.objects.get(id = id, is_deleted = False)
                serializer = BhavcopyRecordSerializer(bhavcopy_record)
                return Response(serializer.data)
            
            else:
                # search = request.GET.get('search', '').strip()
                #  validate with dataclass 
                search = request.GET.get('search', '').strip() 
                page_size = int(request.GET.get('size', 10))
                page_number = int(request.GET.get('page', 1))
                
                # key word args
                filter_kwargs = {"is_deleted": False }
                
                if search:
                    filter_kwargs["name__icontains"] = search
                
                queryset = BhavcopyRecord.objects.filter(**filter_kwargs).order_by('-id').values()
               
                try:
                    total_records = queryset.count()
                    offset = (page_number - 1) * page_size
                    limit = offset + page_size
                    paginated_queryset = queryset[offset:limit]
                    if(paginated_queryset):
                        serializer = BhavcopyRecordSerializer(paginated_queryset, many=True)
                        return Response({
                            "total" : total_records,
                            "page" : page_number,
                            "size" : page_size,
                            "total_pages" : (total_records + page_size - 1) // page_size,
                            "data" : serializer.data                    
                        })
                            
                    else:
                        return Response({"message": "No Records Found"}, status=status.HTTP_404_NOT_FOUND)

                except Exception as e:
                    return Response({"message": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def update_record(self,request,id):
        try:
            try:
                obj = BhavcopyRecord.objects.get(id = id, is_deleted = False)
            except BhavcopyRecord.DoesNotExist:
                return Response(f"message: No record found for requested id {id}", status=status.HTTP_404_NOT_FOUND)
            
            data = request.data
            serializer = BhavcopyRecordSerializer(obj, data = data, partial = True)
            if(serializer.is_valid()):
                serializer.save()
                return Response({"message": "Record updated successfully."})
            else:
                return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_record(self,id):
        try:
            obj = BhavcopyRecord.objects.get(id=id, is_deleted=False)
            obj.is_deleted = True  
            obj.save()
            return Response({"message": "Record deleted successfully."}, status=status.HTTP_200_OK)

        except BhavcopyRecord.DoesNotExist:
            return Response({"message": f"No record found for requested id {id}"}, status=status.HTTP_404_NOT_FOUND)
        
    def export_sheet_by_search_result(self, request):        
        try:
            search = request.GET.get('search', '').strip()
            
            filter_kwargs = {"is_deleted": False }
            
            if search:
                filter_kwargs["name__icontains"] = search

            queryset = BhavcopyRecord.objects.filter(**filter_kwargs).order_by('-id')

            # StringIO it create in-memory file like object means it avoid writing on disk 
            csv_file = StringIO()

            # csv.writer is use for to write rows in csv file
            writer = csv.writer(csv_file)
            
            # Header of the particular file
            writer.writerow(['ID', 'TradDate', 'BizDate', 'Name', 'Open Price', 'High Price', 'Low Price', 'Close Price'])

            # Records
            for record in queryset:
                writer.writerow([
                    record.id,
                    record.trad_date,
                    record.biz_date,
                    record.name,
                    record.open_price,
                    record.high_price,
                    record.low_price,
                    record.close_price,
                ])
            
            # Reset fill pointer to the start
            csv_file.seek(0)
            
            # Create HTTPResponse with text/csv content 
            response = HttpResponse(csv_file, content_type='text/csv')

            # Inspect -> Header triggered for download the file otherwise it can lead some issue while download file
            # Content-Disposition -> used for how to handle the response content
            # attachment is says that download file instead of showing result
            response['Content-Disposition'] = 'attachment; filename=search_results.csv'
            return response
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def download_sheet_by_date(self, request):
        try:
            date = request.GET.get('date')
            if not date:
                return Response({"message": "Please provide a valid date in YYYYMMDD format."}, status=status.HTTP_400_BAD_REQUEST)

            url = f"https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_{date}_F_0000.CSV"
            
            headers = {
                # Used for-> request looks like coming from browser to avoid bot detectioin
                # some web-sites requires Referer, Accept with the User-Agent
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            try:

                # requests.get- fetch a csv file from the url
                response = requests.get(url, headers=headers)

                # raise_for_status: if request is successful then 200 o.w throws 404
                response.raise_for_status()

                # HttpResponse(response.content, content_type='text/csv') return downloaded file as resposnse
                csv_response = HttpResponse(response.content, content_type='text/csv')

                # set Content-Disposition force a downloaded with the name BhavCopy_20250212
                csv_response['Content-Disposition'] = f'attachment; filename="BhavCopy_{date}.csv"'

                return csv_response

            except requests.RequestException as e:
                return Response({"message": f"Error fetching BhavCopy: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        