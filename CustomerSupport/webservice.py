'''
Created on 12 Jul 2016

@author: adam mahmood
'''
import psycopg2
import datetime
import pytz
import logging
from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from setuptools.command.build_ext import if_dl
from bcrypt import  hashpw,gensalt, checkpw
from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)
api = Api(app)
conn_string = "host='localhost' dbname='customersupport' user='customersupport' password='12341234'"
#logging.info("Conecting to database\n -> %s" % conn_string)
print("Conecting to database\n -> %s" % conn_string)

@app.route('/')
def index():
    return "Hello World!"
 
class CreateStaff(Resource):
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
            args = parser.parse_args()
            _userEmail = args['email_address']
            _userPassword = args['password']
            _forename = args['forename']
            _surname = args['surname']
            _dob = args['dob']
            _contactNumber = args['phone_number']
            _gender = args['gender']
            _isAdmin = True if args['is_admin'].lower() == "True".lower() else False
            
            try:
                conn = psycopg2.connect(conn_string)
            except:
                print("Unable to connect to the database!")
            cursor = conn.cursor()
            _userPassword = hashpw(_userPassword.encode('UTF_8'), gensalt(12))
            print(_userPassword.decode())
            cursor.callproc("public.create_staff3",[_forename,_surname,_userEmail,_userPassword.decode(),_isAdmin,_gender,_dob,_contactNumber])

            result = cursor.fetchall()
            conn.commit()
            cursor.close()
            print(result)
            if( result is not None and len(result)> 0):
                return {'status': 200,'message':'Staff Created Succesfully','result':result}
            else:
                return {'status': 100,'message':'Staff Already Exists','result':result}
        except Exception as e:
            return {'error':str(e)}
        
class CreateCustomer(Resource):
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
            try:
                conn = psycopg2.connect(conn_string)
            except:
                print("Unable to connect to the database!")
            print(args)
            cursor = conn.cursor()
            cursor.callproc("public.create_customer5",[_surname,_forename,_customerEmail,_contactNumber,_address,_city,_country,_post_code,_dob,_gender,_registrationDate])

            result = cursor.fetchone()
            conn.commit()
            print(result)
            print(type(result))
            if( result is not None and len(result)> 0):
                cursor.callproc("public.get_treatments5",[int(result[0])])
                result2 = cursor.fetchall()
                conn.commit()
                cursor.close()
                return {'status': 200,'message':'Customer Created Succesfully','result':result,'treatments': result2}
            else:
                cursor.close()
                return {'status': 100,'message':'Customer Already Exists!','result':result}
            
        except Exception as e:
            return {'error':str(e)}    
        
class SearchCustomer(Resource):
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
            try:
                conn = psycopg2.connect(conn_string)
            except:
                print("Unable to connect to the database!")

            cursor = conn.cursor()
             
            #sql = """SELECT "Customer".customer_id,forename,surname,to_char("date_of_birth", 'DD/MM/YYYY'),email_address,address,city,country,phone,sex FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format("".join(whereQuery))
            sql = """SELECT "Customer".customer_id,"Customer".forename,"Customer".surname,"Customer".sex,"Emails".email_address,"Customer".address,"Customer".city,"Customer".country,"Customer".post_code,to_char("date_of_birth", 'DD/MM/YYYY') AS "date_of_birth","Customer_Phones".phone,to_char("registration_date", 'DD/MM/YYYY') AS "reg_birth" FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format("".join(whereQuery))
            print(sql)
            cursor.execute(sql)

            result = cursor.fetchall()
            conn.commit()
            cursor.close()
            print(result)
  
            if( result is not None and len(result)> 0):
                return {'status': 200,'message':'Customer(s) Found','result':result}
            else:
                return {'status': 100,'message':'No Customer(s) Found','result':result}
            
        except Exception as e:
            return {'error':str(e)}          
class AuthenticateStaff(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email',type=str,help='Email address to create user')
            parser.add_argument('password',type=str,help='Password to create user')

            args = parser.parse_args()
            _userEmail = args['email']
            _userPassword = args['password']
            _userPassword=_userPassword.encode('utf_8') ## Password Encoded to UTF_8

            try:
                conn = psycopg2.connect(conn_string)
            except:
                print("Unable to connect to the database!")
            cursor = conn.cursor()
            cursor.callproc("public.authenticate_employee5",[_userEmail])

            result = cursor.fetchone()
 
            conn.commit()
            cursor.close()
            if(result[2] is None):
                return {'status':100,'message':"Authentication Failure. User's (%s)  password is not set!. See Administrator. "%_userEmail}
            
            if(result is not None and checkpw(_userPassword, result[2].encode('utf_8')) ):
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
            try:
                conn = psycopg2.connect(conn_string)
            except:
                print("Unable to connect to the database!")
            cursor = conn.cursor()
            cursor.callproc("public.authenticate_employee8",[_userEmail])

            result = cursor.fetchone()
 
            conn.commit()
            cursor.close()
            if(result[7] is None):
                return {'status':100,'message':"Authentication Failure. User's (%s)  password is not set!. See Administrator. "%_userEmail}
            if(result is not None and checkpw(_userPassword, result[7].encode('utf_8')) ):
                return {'status':200,'message':'Authentication Success','isAdmin':result[3],'staff':result[:7]}
            else:
                return {'status':100,'message':'Authentication Failure'}
            
        except Exception as e:
            return {'error':str(e)}
class Treatments(Resource):

    def get(self):
        try:            
            try:
                conn = psycopg2.connect(conn_string)
            except:
                print("Unable to connect to the database!")
            cursor = conn.cursor()
            cursor.callproc("public.get_treatments")

            result = cursor.fetchall()
            print(result)

            conn.commit()
            cursor.close()
            if(len(result)>0):
                return {'status':200,'results':result}
            else:
                return {'status':100,'message':'No Treatments'}
            
        except Exception as e:
            return {'error':str(e)}   
        
class CustomerTreatments(Resource):        
    def get(self):
        try:  
            parser = reqparse.RequestParser()
            parser.add_argument('customer_id',type=int,help='Customer ID to Search For Customer Treatments')    
            args = parser.parse_args()
            _customerId = args['customer_id']  
            print(type(_customerId))  
            try:
                conn = psycopg2.connect(conn_string)
            except:
                print("Unable to connect to the database!")
            cursor = conn.cursor()
            cursor.callproc("public.get_treatments5",[_customerId,])

            result = cursor.fetchall()
            print(result)

            conn.commit()
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
api.add_resource(Treatments, '/api/v1.0/superdrug/treatments')
api.add_resource(CustomerTreatments, '/api/v1.0/superdrug/customertreatments')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)