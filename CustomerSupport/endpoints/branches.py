from flask_restful import Resource
from CustomerSupport.database.database_connection import  *

class GetBranches(Resource ,DatabaseConnection):
    def get(self):
        try:
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_branches")

            result = cursor.fetchall()
            print(result)

            self.conn.commit()
            cursor.close()
            if(len(result)>0):
                return {'status':200, 'results': result}
            else:
                return {'status':100, 'message': 'No Treatments'}

        except Exception as e:
            return {'error':str(e)}