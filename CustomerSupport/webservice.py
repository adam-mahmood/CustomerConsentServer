'''
Created on 12 Jul 2016

@author: adam mahmood
'''

from flask import Flask,jsonify, make_response, url_for
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from CustomerSupport.endpoints.customer import *
from CustomerSupport.endpoints.branches import *
from CustomerSupport.endpoints.authenticate import *
from CustomerSupport.endpoints.treatments import *
from CustomerSupport.endpoints.upload import *
from CustomerSupport.endpoints.staff import *

# initialization
loggedOn = False
auth = HTTPBasicAuth()
app = Flask(__name__,static_folder = "resources")
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['DATABASE_URI'] = "host='localhost' dbname='customersupport' user='customersupport' password='12341234'"
api = Api(app)

#logging.info("Conecting to database\n -> %s" % conn_string)
##print("Conecting to database\n -> %s" % conn_string)

@app.route('/')
def index():
    return "Hello World!"

@app.route('/get_image')
def get_image():
    #send_file("resources/customerSignatures/95_160317_082057.jpg", mimetype='image/jpeg')
    return url_for('static', filename='customerSignatures/95_160317_082057.jpg')
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
api.add_resource(GetUploadsByCustomerId, '/api/v1.0/superdrug/getuploadsbyid')

if __name__ == '__main__':
    ##context = ('cert.crt', 'key.key')
    app.run(host='0.0.0.0',debug=True, threaded=True)