from flask_restful import Resource, Api,reqparse
from flask import  url_for
from CustomerSupport.database.database_connection import  *
import base64
import re
from flask import send_file

class Upload(Resource ,DatabaseConnection):
    ##@app.route('/api/v1.0/superdrug/editcustomer', methods=['POST'])
    path = 'resources/customerSignatures/'
    imageType = '.jpg'

    def toByteArray(self, _signatureByteArray):
        i = 0
        bytearr = []
        while i < len(_signatureByteArray):
            bytearr.append(_signatureByteArray[i])
            i += 1

        return bytearr


    def convertToImage(self, _customerId, _uploadDate, _signatureImageString):
        imgdata = base64.b64decode(_signatureImageString)
        _uploadDate = re.sub('[/:]', '', _uploadDate)
        filename = Upload.path + _customerId + '_' + _uploadDate.replace(' ', '_') + Upload.imageType
        print(filename)
        with open(filename, 'wb') as f:
            f.write(imgdata)
        return filename

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('customer_id' ,type=str)
            parser.add_argument('staff_id' ,type=str)
            parser.add_argument('treatment_ids' ,action='append')
            parser.add_argument('upload_date' ,type=str)
            parser.add_argument('signature_image_string')

            args = parser.parse_args()
            _treatmentIds = args['treatment_ids']
            _staffId = args['staff_id']
            _customerId = args['customer_id'];
            _uploadDate = args['upload_date']
            _signatureImageString = args['signature_image_string']
            filename = self.convertToImage(_customerId, _uploadDate, _signatureImageString)

            self.connect_to_database()
            cursor = self.conn.cursor()
            print(args)
            cursor.callproc("public.upload" ,[int(_customerId) ,int(_staffId) ,_uploadDate ,_treatmentIds ,filename])
            result = cursor.fetchone()
            print(result)
            self.conn.commit()
            cursor.close()
            if( result is not None and len(result)> 0):
                return {'status': 200,'message': result[0], 'result':[]}
            else:
                return {'status': 100,'message': 'Upload Un-Successful','result':[]}
        except Exception as e:
            return {'error':str(e)}


class GetUploadsByCustomerId(Resource, DatabaseConnection):
    offset = 0
    ##@auth.login_required
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('customer_id', type=int, help='Customer ID to Search For Customer Uploads')
            parser.add_argument('offset_increment', type=int, help='Offset in the Uploads table, used to get the next set of records')

            args = parser.parse_args()
            _customerId = args['customer_id']
            _offsetIncrement = args['offset_increment']

            GetUploadsByCustomerId.offset = GetUploadsByCustomerId.offset + _offsetIncrement
            if(GetUploadsByCustomerId.offset < 0):
                GetUploadsByCustomerId.offset = 0;

            self.connect_to_database()
            cursor = self.conn.cursor()
            try:
                cursor.callproc("public.get_upload_by_customer_id2", [_customerId,GetUploadsByCustomerId.offset ])
            except Exception  as err:
                print("Error Getting Uploads: {0}".format(err))


            result = cursor.fetchall()
            for i in range(len(result)):
                upload = list(result[i])
                print(upload)
                # get_customer_by_id
                cursor.callproc("public.get_customer_by_id", [_customerId, ])
                customer = cursor.fetchone()

                # get_staff
                cursor.callproc("public.get_staff_by_id", [upload[2] ])
                staff = cursor.fetchone()

                #get_upload_treatments_by_upload_id
                cursor.callproc("public.get_upload_treatments_by_upload_id", [upload[0] ])
                upload_treatments = cursor.fetchall()

                result[i] = {'customer':customer,'staff':staff,'upload_treatments':upload_treatments,'upload_date':upload[3],'signature_url': url_for('static', filename=upload[4][10:])}

            print(result)
            self.conn.commit()
            cursor.close()
            if (len(result) > 0):
                return {'status': 200, 'results': result}
            else:
                return {'status': 100, 'message': 'No Customer Uploads for {}'.format(_customerId)}

        except Exception as e:
            return {'error': str(e)}


