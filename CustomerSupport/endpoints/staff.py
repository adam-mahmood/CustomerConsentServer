from flask_restful import Resource, Api,reqparse
from CustomerSupport.database.database_connection import  *
from bcrypt import  hashpw,gensalt, checkpw

class CreateStaff(Resource ,DatabaseConnection):


    def hash_password(self, _userPassword):
        return hashpw(_userPassword.encode('UTF_8'), gensalt(12))

    ##@auth.login_required
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('surname' ,type=str ,help='Surname of new Staff')
            parser.add_argument('forename' ,type=str ,help='Forename of new Staff')
            parser.add_argument('email_address' ,type=str ,help='Email address of Staff')
            parser.add_argument('password' ,type=str ,help='Password of Staff')
            parser.add_argument('gender' ,type=str ,help='Gender of new Staff')
            parser.add_argument('dob' ,type=str ,help='DOB of new Staff')
            parser.add_argument('is_admin' ,type=str ,help='Is admin of new Staff')
            parser.add_argument('phone_number' ,type=int ,help='Phone number of new Staff')
            parser.add_argument('username' ,type=str ,help='Username of Staff')
            parser.add_argument('address' ,type=str)
            parser.add_argument('city' ,type=str)
            parser.add_argument('post_code' ,type=str)
            parser.add_argument('registration_date' ,type=str ,help='Registration Date of Staff')
            parser.add_argument('branch_name' ,type=str ,help='Branch of Staff')

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
            try:
                cursor.callproc("public.create_staff4"
                                ,[_forename ,_surname ,_userEmail ,_userPassword.decode() ,_isAdmin ,_gender ,_dob
                                 ,_contactNumber ,_username ,_address ,_city ,_post_code ,_registrationDate
                                 ,_branchName])
            except Exception  as err:
                print("Error Creating Staff: {0}".format(err))
            result = cursor.fetchall()
            self.conn.commit()
            cursor.close()
            print(result)
            if( result is not None and len(result)> 0):
                loggedOn =True
                return {'status': 200,'message': 'Staff Created Succesfully','result': result}
            else:
                return {'status': 100,'message': 'Staff Already Exists','result': result}
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


class GetStaff(Resource, DatabaseConnection):
    def get(self):
        try:
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_staff")

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


class GetStaffByBranch(Resource, DatabaseConnection):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('branch_id', type=str)
            args = parser.parse_args()
            _branchId = args['branch_id']
            self.connect_to_database()
            cursor = self.conn.cursor()
            cursor.callproc("public.get_staff", [_branchId, ])

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