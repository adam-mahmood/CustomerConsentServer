from flask_restful import Resource, Api,reqparse
from CustomerSupport.database.database_connection import  *
from bcrypt import  hashpw,gensalt, checkpw

class AuthenticateStaff(Resource ,DatabaseConnection):

    def verify_password(self, _userPassword, hashed_password):
        return checkpw(_userPassword, hashed_password)

    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email' ,type=str ,help='Email address to create user')
            parser.add_argument('password' ,type=str ,help='Password to create user')

            args = parser.parse_args()
            _userEmail = args['email']
            _userPassword = args['password']
            _userPassword= _userPassword.encode('utf_8')  ## Password Encoded to UTF_8

            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.authenticate_employee5", [_userEmail])
            result = cursor.fetchone()

            self.conn.commit()
            cursor.close()
            if(result[2] is None):
                return {'status':100,'message' : "Authentication Failure. Staff's (%s)  password is not set!. See Administrator. "%_userEmail}

            if(result is not None and self. verify_password(_userPassword, result[2].encode('utf_8')) ):
                return {'status':200,'message':'Authentication Success' , 'isAdmin': result[1],'Staff_id':result[ 0]}
            else :
                return {'status':100,'message':'Authentication Failure' }
        except Exception as e:
            return {'error':str(e)}
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email',type=str,help='Email address to create user' )
            parser.add_argument('password',type=str,help='Password to create user')

            args = parser.parse_args()
            _userEmail = args['email']
            _userPassword = args['password']
            _userPassword=_userPassword.encode('utf_8') ## Password Encoded to UTF_8
            self.  connect_to_database()
            cursor = self.conn.cursor()

            cursor.callproc("public.authenticate_employee9",[_userEmail])

            result = cursor. fetchone()

            self.conn.commit()
            cursor.close()
            database_password = result[14]
            if(database_password is None): return {'status':100,'message': "Authentication Failure. Staff's (%s)  password is not set!. See Administrator. "%_userEmail}
            if(result is not None and self.verify_password(_userPassword, database_password.encode( 'utf_8')) ):
                return {'status':200,'message':'Authentication Success','isAdmin':result[7],'staff':result[:14]}
            else:
                return {'status':100,'message': 'Authentication Failure'}

        except Exception as e:
            return {'error':str(e)}
