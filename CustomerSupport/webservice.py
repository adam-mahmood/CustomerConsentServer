'''
Created on 12 Jul 2016

@author: adam mahmood
'''
import psycopg2
from flask import Flask,jsonify, abort, request, make_response, url_for, render_template
from flask_restful import Resource, Api,reqparse
from bcrypt import  hashpw,gensalt, checkpw
from flask_httpauth import HTTPBasicAuth,HTTPTokenAuth,HTTPDigestAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import base64
import io
from click.types import Path
import re



# initialization
loggedOn = False
auth = HTTPBasicAuth()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['DATABASE_URI'] = "host='localhost' dbname='customersupport' user='customersupport' password='12341234'"
api = Api(app)

#logging.info("Conecting to database\n -> %s" % conn_string)
##print("Conecting to database\n -> %s" % conn_string)

@app.route('/')
def index():
    return "Hello World!"

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

class Staff():

    def __init( self, userEmail, password,forename,surname,dob,contactNumber,gender,isAdmin):
        """TODO"""
        
      
    def hash_password(self, _userPassword):
        self.hash_password = hashpw(_userPassword.encode('UTF_8'), gensalt(12))
        return self.hash_password

    def verify_password(self, _userPassword, hashed_password):
        return checkpw(_userPassword, hashed_password)
    
    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = "Hello"
        return user

class DatabaseConnection():
    """The Databse Connection class provides connection method."""
    conn_string = "host='localhost' dbname='customersupport' user='customersupport' password='12341234'"
    def connect_to_database(self):
        try:
            self.conn = psycopg2.connect(DatabaseConnection.conn_string)
        except:
            print("Unable to connect to the database!")
        return self.conn
class CreateStaff(Resource,DatabaseConnection):
    

    def hash_password(self, _userPassword):
        return hashpw(_userPassword.encode('UTF_8'), gensalt(12))
    
    ##@auth.login_required 
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('surname',type=str,help='Surname of new Staff')
            parser.add_argument('forename',type=str,help='Forename of new Staff')
            parser.add_argument('email_address',type=str,help='Email address of Staff')
            parser.add_argument('password',type=str,help='Password of Staff')
            parser.add_argument('gender',type=str,help='Gender of new Staff')
            parser.add_argument('dob',type=str,help='DOB of new Staff')
            parser.add_argument('is_admin',type=str,help='Is admin of new Staff')
            parser.add_argument('phone_number',type=int,help='Phone number of new Staff')
            parser.add_argument('username',type=str,help='Username of Staff')
            parser.add_argument('address',type=str)
            parser.add_argument('city',type=str)
            parser.add_argument('post_code',type=str)
            parser.add_argument('registration_date',type=str,help='Registration Date of Staff')
            parser.add_argument('branch_name',type=str,help='Branch of Staff')
            
            args = parser.parse_args()
            _userEmail = args['email_address']
            _userPassword = args['password']
            _forename = args['forename']
            _surname = args['surname']
            _dob = args['dob']
            _contactNumber = args['phone_number']
            _gender = args['gender']
            _isAdmin = True if args['is_admin'].lower() == "True".lower() else False
            _username = args['username']
            _address = args['address']
            _city = args['city']
            _post_code = args['post_code']
            _registrationDate = args['registration_date']    
            _branchName = args['branch_name']        
            
            self.connect_to_database()
            cursor = self.conn.cursor()
            _userPassword = self.hash_password(_userPassword)
            print(_userPassword.decode())
            print(args)

            cursor.callproc("public.create_staff4",[_forename,_surname,_userEmail,_userPassword.decode(),_isAdmin,_gender,_dob,_contactNumber,_username,_address,_city,_post_code,_registrationDate,_branchName])

            result = cursor.fetchall()
            self.conn.commit()
            cursor.close()
            print(result)
            if( result is not None and len(result)> 0):
                loggedOn =True
                return {'status': 200,'message':'Staff Created Succesfully','result':result}
            else:
                return {'status': 100,'message':'Staff Already Exists','result':result}
        except Exception as e:
            return {'error':str(e)}
class EditStaff(Resource,DatabaseConnection):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('staff_id',type=str)
            parser.add_argument('surname',type=str,help='Surname to create new Customer')
            parser.add_argument('forename',type=str,help='Forename to create new Customer')
            parser.add_argument('date_of_birth',type=str,help='DOB to create new Customer')
            parser.add_argument('email_address',type=str,help='Email Address to create new Customer')
            parser.add_argument('contact_number',type=str,help='Contact number to create new Customer')
            parser.add_argument('address',type=str,help='Address to create new Customer')
            parser.add_argument('city',type=str,help='City to create new Customer')
            parser.add_argument('country',type=str,help='Country to create new Customer')
            parser.add_argument('post_code',type=str,help='Post Code to create new Customer')
            parser.add_argument('sex',type=str,help='Gender to create new Customer')
            args = parser.parse_args()
            _customerEmail = args['email_address']
            _contactNumber = args['contact_number']
            _customerId = args['customer_id'];
            
            print(args)
            filteredArgs = {k: v for k, v in args.items() if v   }
            print(filteredArgs)
            if (filteredArgs.__contains__('email_address')):
                filteredArgs.pop('email_address')
            elif (filteredArgs.__contains__('contact_number')):
                
                filteredArgs.pop('contact_number')
                
            length = len(filteredArgs)     
            index = 0;
            updateQuery = [];
            updateQuery.append("""UPDATE "Customer" SET """)
            for key, value in filteredArgs.items():
                index = index +1
                if(index == length):
                    updateQuery.append("""{} = '{}' """.format(key, value))
                else:
                    updateQuery.append("""{} = '{}', """.format(key, value))
                   
            print(updateQuery)
            self.connect_to_database()

            cursor = self.conn.cursor()
             
            #sql = """SELECT "Customer".customer_id,forename,surname,to_char("date_of_birth", 'DD/MM/YYYY'),email_address,address,city,country,phone,sex FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format("".join(updateQuery))
            sql = """{} WHERE "Customer".customer_id = to_number('{}','99999');""".format("".join(updateQuery),_customerId)
            print(sql)
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            result = "success"
            if( result is not None and len(result)> 0):
                return {'status': 200,'message':'Customer Changed Successfully','result':[]}
            else:
                return {'status': 100,'message':'Customer Not Changed','result':[]}
            
        except Exception as e:
            return {'error':str(e)}         
class CreateCustomer(Resource,DatabaseConnection):
    ##@auth.login_required  
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('surname',type=str,help='Surname to create new Customer')
            parser.add_argument('forename',type=str,help='Forename to create new Customer')
            parser.add_argument('dob',type=str,help='DOB to create new Customer')
            parser.add_argument('email_address',type=str,help='Email Address to create new Customer')
            parser.add_argument('contact_number',type=str,help='Contact number to create new Customer')
            parser.add_argument('address',type=str,help='Address to create new Customer')
            parser.add_argument('city',type=str,help='City to create new Customer')
            parser.add_argument('country',type=str,help='Country to create new Customer')
            parser.add_argument('post_code',type=str,help='Post Code to create new Customer')
            parser.add_argument('gender',type=str,help='Gender to create new Customer')
            parser.add_argument('registration_date',type=str,help='Registration Date to create new Customer')
            args = parser.parse_args()
            _customerEmail = args['email_address']
            _forename = args['forename']
            _surname = args['surname']
            _dob = args['dob']
            _contactNumber = args['contact_number']
            _address = args['address']
            _city = args['city']
            _country = args['country']
            _post_code = args['post_code']
            _gender = args['gender']
            _registrationDate = args['registration_date']
            
#             naive_date = datetime.datetime.strptime(_registrationDate, "%Y-%m-%d %H:%M:%S")
#             localtz = pytz.timezone('utc')
#             date_aware_la = localtz.localize(naive_date)
#             print(date_aware_la)
            self.connect_to_database()
            print(args)
            cursor = self.conn.cursor()
            if not _dob:
                _dob="NULL"
            print(_dob);
            cursor.callproc("public.create_customer6",[_surname,_forename,_customerEmail,_contactNumber,_address,_city,_country,_post_code,_dob,_gender,_registrationDate])

            result = cursor.fetchone()
            self.conn.commit()
            print(result)
            print(type(result))
            if( result is not None and len(result)> 0):
                cursor.callproc("public.get_treatments5",[int(result[0])])
                result2 = cursor.fetchall()
                self.conn.commit()
                cursor.close()
                return {'status': 200,'message':'Customer Created Succesfully','result':result,'treatments': result2}
            else:
                cursor.close()
                return {'status': 100,'message':'Customer Already Exists!','result':result}
            
        except Exception as e:
            return {'error':str(e)}    
     
class SearchCustomer(Resource,DatabaseConnection):
    ##@auth.login_required   
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('surname',type=str)
            parser.add_argument('forename',type=str)
            parser.add_argument('date_of_birth',type=str)
            parser.add_argument('email_address',type=str)
            parser.add_argument('contact_number',type=str)
            parser.add_argument('customer_id',type=str)

            args = parser.parse_args()

            print(args)
            filteredArgs = {k: v for k, v in args.items() if v  }
            length = len(filteredArgs)
            index = 0;
            print(filteredArgs)
            whereQuery = [];
            whereQuery.append("WHERE ")
            for key, value in filteredArgs.items():
                index = index +1
                if(index == length):
                    whereQuery.append("""{} = '{}' """.format(key, value))
                else:
                    whereQuery.append("""{} = '{}' AND """.format(key, value))
                
                
            print(whereQuery)
            self.connect_to_database()

            cursor = self.conn.cursor()
             
            #sql = """SELECT "Customer".customer_id,forename,surname,to_char("date_of_birth", 'DD/MM/YYYY'),email_address,address,city,country,phone,sex FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format("".join(whereQuery))
            sql = """SELECT "Customer".customer_id,"Customer".forename,"Customer".surname,"Customer".sex,"Emails".email_address,"Customer".address,"Customer".city,"Customer".country,"Customer".post_code,to_char("date_of_birth", 'DD/MM/YYYY') AS "date_of_birth","Customer_Phones".phone,to_char("registration_date", 'DD/MM/YYYY') AS "reg_birth" FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format("".join(whereQuery))
            print(sql)
            cursor.execute(sql)

            result = cursor.fetchall()
            self.conn.commit()
            cursor.close()
            print(result)
  
            if( result is not None and len(result)> 0):
                return {'status': 200,'message':'Customer(s) Found','result':result}
            else:
                return {'status': 100,'message':'No Customer(s) Found','result':result}
            
        except Exception as e:
            return {'error':str(e)}         
class EditCustomer(Resource,DatabaseConnection):
    ##@app.route('/api/v1.0/superdrug/editcustomer', methods=['POST'])
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('customer_id',type=str)
            parser.add_argument('surname',type=str,help='Surname to create new Customer')
            parser.add_argument('forename',type=str,help='Forename to create new Customer')
            parser.add_argument('date_of_birth',type=str,help='DOB to create new Customer')
            parser.add_argument('email_address',type=str,help='Email Address to create new Customer')
            parser.add_argument('contact_number',type=str,help='Contact number to create new Customer')
            parser.add_argument('address',type=str,help='Address to create new Customer')
            parser.add_argument('city',type=str,help='City to create new Customer')
            parser.add_argument('country',type=str,help='Country to create new Customer')
            parser.add_argument('post_code',type=str,help='Post Code to create new Customer')
            parser.add_argument('sex',type=str,help='Gender to create new Customer')
            args = parser.parse_args()
            _customerEmail = args['email_address']
            _contactNumber = args['contact_number']
            _customerId = args['customer_id'];
            
            print(args)
            filteredArgs = {k: v for k, v in args.items() if v   }
            print(filteredArgs)
            if (filteredArgs.__contains__('email_address')):
                filteredArgs.pop('email_address')
            elif (filteredArgs.__contains__('contact_number')):
                
                filteredArgs.pop('contact_number')
                
            length = len(filteredArgs)     
            index = 0;
            updateQuery = [];
            updateQuery.append("""UPDATE "Customer" SET """)
            for key, value in filteredArgs.items():
                index = index +1
                if(index == length):
                    updateQuery.append("""{} = '{}' """.format(key, value))
                else:
                    updateQuery.append("""{} = '{}', """.format(key, value))
                   
            print(updateQuery)
            self.connect_to_database()

            cursor = self.conn.cursor()
             
            #sql = """SELECT "Customer".customer_id,forename,surname,to_char("date_of_birth", 'DD/MM/YYYY'),email_address,address,city,country,phone,sex FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format("".join(updateQuery))
            sql = """{} WHERE "Customer".customer_id = to_number('{}','99999');""".format("".join(updateQuery),_customerId)
            print(sql)
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            result = "success"
            if( result is not None and len(result)> 0):
                return {'status': 200,'message':'Customer Changed Successfully','result':[]}
            else:
                return {'status': 100,'message':'Customer Not Changed','result':[]}
            
        except Exception as e:
            return {'error':str(e)}    
class Upload(Resource,DatabaseConnection):
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
            parser.add_argument('customer_id',type=str)
            parser.add_argument('staff_id',type=str)
            parser.add_argument('treatment_ids',action='append')
            parser.add_argument('upload_date',type=str)
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
            cursor.callproc("public.upload",[int(_customerId),int(_staffId),_uploadDate,_treatmentIds,filename])
            result = cursor.fetchone()
            print(result)
            self.conn.commit()
            cursor.close()

            if( result is not None and len(result)> 0):
                return {'status': 200,'message':result[0],'result':[]}
            else:
                return {'status': 100,'message':'Upload Un-Successful','result':[]}
            
        except Exception as e:
            return {'error':str(e)}            
class AuthenticateStaff(Resource,DatabaseConnection):

    def verify_password(self, _userPassword, hashed_password):
        return checkpw(_userPassword, hashed_password)

    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email',type=str,help='Email address to create user')
            parser.add_argument('password',type=str,help='Password to create user')

            args = parser.parse_args()
            _userEmail = args['email']
            _userPassword = args['password']
            _userPassword=_userPassword.encode('utf_8') ## Password Encoded to UTF_8

            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.authenticate_employee5",[_userEmail])

            result = cursor.fetchone()
 
            self.conn.commit()
            cursor.close()
            if(result[2] is None):
                return {'status':100,'message':"Authentication Failure. Staff's (%s)  password is not set!. See Administrator. "%_userEmail}
            
            if(result is not None and self.verify_password(_userPassword, result[2].encode('utf_8')) ):
                return {'status':200,'message':'Authentication Success','isAdmin':result[1],'Staff_id':result[0]}
            else:
                return {'status':100,'message':'Authentication Failure'}
            
        except Exception as e:
            return {'error':str(e)}
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email',type=str,help='Email address to create user')
            parser.add_argument('password',type=str,help='Password to create user')

            args = parser.parse_args()
            _userEmail = args['email']
            _userPassword = args['password']
            _userPassword=_userPassword.encode('utf_8') ## Password Encoded to UTF_8
            self.connect_to_database()
            cursor = self.conn.cursor()
            print(args)
            cursor.callproc("public.authenticate_employee9",[_userEmail])
            
            result = cursor.fetchone()
            print(result)
            self.conn.commit()
            cursor.close()
            database_password = result[14]
            if(database_password is None):
                return {'status':100,'message':"Authentication Failure. Staff's (%s)  password is not set!. See Administrator. "%_userEmail}
            if(result is not None and self.verify_password(_userPassword, database_password.encode('utf_8')) ):
                return {'status':200,'message':'Authentication Success','isAdmin':result[7],'staff':result[:14]}
            else:
                return {'status':100,'message':'Authentication Failure'}
            
        except Exception as e:
            return {'error':str(e)}

class Treatments(Resource,DatabaseConnection):
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
            if(len(result)>0):
                return {'status':200,'results':result}
            else:
                return {'status':100,'message':'No Treatments'}
            
        except Exception as e:
            return {'error':str(e)}   
class GetStaff(Resource,DatabaseConnection):
    def get(self):
        try:            
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_staff")

            result = cursor.fetchall()
            print(result)

            self.conn.commit()
            cursor.close()
            if(len(result)>0):
                return {'status':200,'results':result}
            else:
                return {'status':100,'message':'No Treatments'}
            
        except Exception as e:
            return {'error':str(e)}  
class GetStaffByBranch(Resource,DatabaseConnection):
    def get(self):
        try:            
            parser = reqparse.RequestParser()
            parser.add_argument('branch_id',type=str)    
            args = parser.parse_args()
            _branchId = args['branch_id'] 
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_staff",[_branchId,])

            result = cursor.fetchall()
            print(result)

            self.conn.commit()
            cursor.close()
            if(len(result)>0):
                return {'status':200,'results':result}
            else:
                return {'status':100,'message':'No Treatments'}
            
        except Exception as e:
            return {'error':str(e)}  
class GetBranches(Resource,DatabaseConnection):
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
                return {'status':200,'results':result}
            else:
                return {'status':100,'message':'No Treatments'}
            
        except Exception as e:
            return {'error':str(e)}                 
class CustomerTreatments(Resource,DatabaseConnection):
    ##@auth.login_required         
    def get(self):
        try:  
            parser = reqparse.RequestParser()
            parser.add_argument('customer_id',type=int,help='Customer ID to Search For Customer Treatments')    
            args = parser.parse_args()
            _customerId = args['customer_id']  
            print(type(_customerId))  
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_treatments5",[_customerId,])

            result = cursor.fetchall()
            print(result)

            self.conn.commit()
            cursor.close()
            if(len(result)>0):
                return {'status':200,'results':result}
            else:
                return {'status':100,'message':'No Treatments'}
            
        except Exception as e:
            return {'error':str(e)}

api.add_resource(CreateStaff, '/api/v1.0/superdrug/createstaff')
api.add_resource(SearchCustomer, '/api/v1.0/superdrug/searchcustomer')
api.add_resource(AuthenticateStaff, '/api/v1.0/superdrug/login/authenticatestaff')
api.add_resource(CreateCustomer, '/api/v1.0/superdrug/createcustomer')
api.add_resource(EditCustomer, '/api/v1.0/superdrug/editcustomer')
api.add_resource(Treatments, '/api/v1.0/superdrug/treatments')
api.add_resource(CustomerTreatments, '/api/v1.0/superdrug/customertreatments')
api.add_resource(GetStaff, '/api/v1.0/superdrug/getstaff')
api.add_resource(GetStaffByBranch, '/api/v1.0/superdrug/getstaffbybranch')
api.add_resource(GetBranches, '/api/v1.0/superdrug/getbranches')
api.add_resource(Upload, '/api/v1.0/superdrug/upload')

if __name__ == '__main__':
    ##context = ('cert.crt', 'key.key')
    app.run(host='0.0.0.0',debug=True, threaded=True)