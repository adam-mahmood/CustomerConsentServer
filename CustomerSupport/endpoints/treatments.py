from flask_restful import Resource,reqparse
from CustomerSupport.database.database_connection import  *


class Treatments(Resource, DatabaseConnection):
    ## @auth.login_required
    def get(self):
        try:
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_treatments")

            result = cursor.fetchall()
            print(result)

            self.conn.commit()
            cursor.close()
            if (len(result) > 0):
                return {'status': 200, 'results': result}
            else:
                return {'status': 100, 'message': 'No Treatments'}

        except Exception as e:
            return {'error': str(e)}


class CustomerTreatments(Resource, DatabaseConnection):
    ##@auth.login_required
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('customer_id', type=int, help='Customer ID to Search For Customer Treatments')
            args = parser.parse_args()
            _customerId = args['customer_id']
            print(type(_customerId))
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_treatments5", [_customerId, ])

            result = cursor.fetchall()
            print(result)

            self.conn.commit()
            cursor.close()
            if (len(result) > 0):
                return {'status': 200, 'results': result}
            else:
                return {'status': 100, 'message': 'No Treatments'}

        except Exception as e:
            return {'error': str(e)}