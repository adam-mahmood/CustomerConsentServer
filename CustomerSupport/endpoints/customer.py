
from flask_restful import Resource, Api,reqparse
from CustomerSupport.database.database_connection import  *


class CreateCustomer(Resource, DatabaseConnection):
    ##@auth.login_required
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('surname', type=str, help='Surname to create new Customer')
            parser.add_argument('forename', type=str, help='Forename to create new Customer')
            parser.add_argument('dob', type=str, help='DOB to create new Customer')
            parser.add_argument('email_address', type=str, help='Email Address to create new Customer')
            parser.add_argument('contact_number', type=str, help='Contact number to create new Customer')
            parser.add_argument('address', type=str, help='Address to create new Customer')
            parser.add_argument('city', type=str, help='City to create new Customer')
            parser.add_argument('country', type=str, help='Country to create new Customer')
            parser.add_argument('post_code', type=str, help='Post Code to create new Customer')
            parser.add_argument('gender', type=str, help='Gender to create new Customer')
            parser.add_argument('registration_date', type=str, help='Registration Date to create new Customer')
            args = parser.parse_args()
            _customerEmail = args['email_address']
            _forename = args['forename']
            _surname = args['surname']
            _dob = args['dob']
            _contactNumber = args['contact_number']
            _address = args['address']
            _city = args['city']
            _country = args['country']
            _post_code = args['post_code'].upper()
            _gender = args['gender']
            _registrationDate = args['registration_date']

            self.connect_to_database()
            print(args)
            cursor = self.conn.cursor()

            print(_dob);
            try:
                cursor.callproc("public.create_customer6",
                                [_surname, _forename, _customerEmail, _contactNumber, _address, _city, _country,
                                 _post_code, _dob, _gender, _registrationDate])
            except Exception  as err:
                print("Error Creating Customer: {0}".format(err))

            result = cursor.fetchone()
            self.conn.commit()

            if (result is not None and len(result) > 0):
                cursor.callproc("public.get_treatments5", [int(result[0])])
                result2 = cursor.fetchall()
                self.conn.commit()
                cursor.close()
                return {'status': 200, 'message': 'Customer Created Succesfully', 'result': result,
                        'treatments': result2}
            else:
                cursor.close()
                return {'status': 100, 'message': 'Customer Already Exists!', 'result': result}

        except Exception as e:
            return {'error': str(e)}


class SearchCustomer(Resource, DatabaseConnection):
    ##@auth.login_required
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('surname', type=str)
            parser.add_argument('forename', type=str)
            parser.add_argument('date_of_birth', type=str)
            parser.add_argument('email_address', type=str)
            parser.add_argument('contact_number', type=str)
            parser.add_argument('customer_id', type=str)

            args = parser.parse_args()

            print(args)
            filteredArgs = {k: v for k, v in args.items() if v}
            length = len(filteredArgs)
            index = 0;
            print(filteredArgs)
            whereQuery = [];
            whereQuery.append("WHERE ")
            for key, value in filteredArgs.items():
                index = index + 1
                if (index == length):
                    whereQuery.append("""{} ILIKE '{}%' """.format(key, value))
                else:
                    whereQuery.append("""{} ILIKE '{}%' AND """.format(key, value))

            print(whereQuery)
            self.connect_to_database()

            cursor = self.conn.cursor()

            # sql = """SELECT "Customer".customer_id,forename,surname,to_char("date_of_birth", 'DD/MM/YYYY'),email_address,address,city,country,phone,sex FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format("".join(whereQuery))
            sql = """SELECT "Customer".customer_id,"Customer".forename,"Customer".surname,"Customer".sex,"Emails".email_address,"Customer".address,"Customer".city,"Customer".country,"Customer".post_code,to_char("date_of_birth", 'DD/MM/YYYY') AS "date_of_birth","Customer_Phones".phone,to_char("registration_date", 'DD/MM/YYYY') AS "reg_birth" FROM public."Customer" INNER JOIN public."Emails" ON "Customer".customer_id = "Emails".customer_id INNER JOIN public."Customer_Phones" ON "Customer".customer_id = "Customer_Phones".customer_id {};""".format(
                "".join(whereQuery))
            print(sql)
            cursor.execute(sql)

            result = cursor.fetchall()
            self.conn.commit()
            cursor.close()
            print(result)

            if (result is not None and len(result) > 0):
                return {'status': 200, 'message': 'Customer(s) Found', 'result': result}
            else:
                return {'status': 100, 'message': 'No Customer(s) Found', 'result': result}

        except Exception as e:
            return {'error': str(e)}


class EditCustomer(Resource, DatabaseConnection):
    ##@app.route('/api/v1.0/superdrug/editcustomer', methods=['POST'])
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('customer_id', type=str)
            parser.add_argument('surname', type=str, help='Surname to create new Customer')
            parser.add_argument('forename', type=str, help='Forename to create new Customer')
            parser.add_argument('date_of_birth', type=str, help='DOB to create new Customer')
            parser.add_argument('email_address', type=str, help='Email Address to create new Customer')
            parser.add_argument('contact_number', type=str, help='Contact number to create new Customer')
            parser.add_argument('address', type=str, help='Address to create new Customer')
            parser.add_argument('city', type=str, help='City to create new Customer')
            parser.add_argument('country', type=str, help='Country to create new Customer')
            parser.add_argument('post_code', type=str, help='Post Code to create new Customer')
            parser.add_argument('sex', type=str, help='Gender to create new Customer')
            args = parser.parse_args()
            _customerEmail = args['email_address']
            _contactNumber = args['contact_number']
            _customerId = args['customer_id'];

            print(args)
            filteredArgs = {k: v for k, v in args.items() if v}
            filteredArgsEmail = {}
            filteredArgsPhoneNumber = {}

            filteredArgs.pop('customer_id')
            print(filteredArgs)
            ##Because Email Adress and Phone number are in seperate tables they need to be seperated into their own dics
            if (filteredArgs.__contains__('email_address')):
                filteredArgsEmail['email_address'] = filteredArgs.pop('email_address')

            if (filteredArgs.__contains__('contact_number')):
                filteredArgsPhoneNumber['phone'] = filteredArgs.pop('contact_number')

            if filteredArgs:
                cursor = self.update(filteredArgs, _customerId, """ "Customer"  """, """ "Customer".customer_id""")

            if filteredArgsEmail:
                cursor = self.update(filteredArgsEmail, _customerId, """ "Emails" """, """ "Emails".customer_id""")

            if filteredArgsPhoneNumber:
                cursor = self.update(filteredArgsPhoneNumber, _customerId, """ "Customer_Phones" """,
                                     """ "Customer_Phones".customer_id""")

            cursor.close()
            result = "success"
            if (result is not None and len(result) > 0):
                return {'status': 200, 'message': 'Customer Changed Successfully', 'result': []}
            else:
                return {'status': 100, 'message': 'Customer Not Changed', 'result': []}

        except Exception as e:
            return {'error': str(e)}

    def update(self, filteredArgs, _customerId, tableName, custmerIdColumnName):
        length = len(filteredArgs)
        index = 0;
        updateQuery = [];
        updateQuery.append("""UPDATE {} SET """.format(tableName))
        for key, value in filteredArgs.items():
            index = index + 1
            if (index == length):
                updateQuery.append("""{} = '{}' """.format(key, value))
            else:
                updateQuery.append("""{} = '{}', """.format(key, value))
        print(updateQuery)
        self.connect_to_database()
        cursor = self.conn.cursor()
        sql = """{} WHERE {} = to_number('{}','99999');""".format("".join(updateQuery), custmerIdColumnName,
                                                                  _customerId)
        print(sql)
        try:
            cursor.execute(sql)
            self.conn.commit()
        except Exception  as err:
            print("Error Editing Customer: {0}".format(err))
        return cursor