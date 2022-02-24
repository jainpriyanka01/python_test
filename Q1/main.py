from flask import Flask, render_template, request, jsonify,make_response
from datetime import timedelta,datetime
from flask_sqlalchemy import SQLAlchemy
import os
from flask import request, jsonify, copy_current_request_context
import logging
import jwt
import struct
import socket
from functools import wraps
my_path = os.path.abspath(os.path.dirname(__file__))
main_path = os.path.join(my_path, "")


app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = '$_0031$%^1<.,{{09@)cvsj__&'



logging.basicConfig(filename='router.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(threadName)s : %(message)s')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///router.db'


db = SQLAlchemy(app)

# Creating router_details table
class Router(db.Model):
    __tablename__ = 'router_details'
    Sapid = db.Column('Sapid', db.String(18), nullable=False)
    Hostname = db.Column('Hostname',db.String(14), nullable=False)
    Loopback = db.Column('Loopback',db.Integer,nullable=False,primary_key = True)
    Macaddress = db.Column('Macaddress',db.String(17), nullable=False)
    status=db.Column('status',db.Boolean,default=True,nullable=False)

db.create_all()

#Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'X-Access-Token' in request.headers:
            token = request.headers['x-access-token']
            logging.info("Token received: "+str(token))

        if not token:
            logging.info("Token is missing")
            return jsonify({'message' : 'Token is missing !!'}), 401


        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            logging.info("Token received"+str(data))
            current_user = "$_0031$%^1<.,{{09@)cvsj__&"
        except:
            logging.info("Exception Encountered: Invalid Token")
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401

        return  f(current_user, *args, **kwargs)

    return decorated


@app.route('/token', methods = ['GET', 'POST'])
def token():
    """Function to generate token

    Returns:
        string: encrypted token value
    """
    logging.info("Executing token function")
    token = jwt.encode({
                        'public_id':'test',
                        'exp' : datetime.utcnow() + timedelta(minutes = 30)
                }, app.config['SECRET_KEY'])
    logging.info("Generated token: "+str(token))
    return token

@app.route('/')
def index():
    """Function to return index page

    Returns:
        html page: return index.html page with all the records
    """
    all_records=Router.query.filter_by(status=True)
    return render_template('index.html', all_records=all_records)


@app.route('/create_record', methods=['GET','POST'])
def create_record():
    """Function to return create record page

    Returns:
        html page: return create.html page with all the records
    """
    return render_template('create.html')

@app.route('/update_record', methods=['GET','POST'])
def update_record():
    """Function to return update record page

    Returns:
        html page: return update.html page with all the records
    """
    all_records=Router.query.filter_by(status=True)
    return render_template('update.html',record=all_records)

@app.route('/delete_record', methods=['GET','POST'])
def delete_record():
    """Function to return delete record page

    Returns:
        html page: return delete.html page with all the records
    """
    all_records=Router.query.filter_by(status=True)
    return render_template('delete.html',record=all_records)

@app.route('/api/create', methods=['POST'])
@token_required
def create(token_value):
    """Function to Create new record of router in DB

    Args:
        token_value (string): token to authenticate the API

    Returns:
        json: Result JSON
    """
    if token_value == app.config['SECRET_KEY']:
        header=request.headers
        logging.info("Checking if x-access-token is passed in the header of request")
        if 'X-Access-Token' in header:
            token=header['X-Access-Token']
        else:
            logging.info("x-access-token is not passed in the header of request")
            result_json={"Status":"401","Message":"Authentication Error, Please pass X-Access-Token in headers"}
            return result_json
        try:
            sap_id = request.args['sap_id']
            hostname = request.args['hostname']
            loopback = request.args['loopback']
            macaddress = request.args['macaddress']

            new_record = Router(Sapid=sap_id,Hostname=hostname,Loopback=loopback,Macaddress=macaddress)
            db.session.add(new_record)
            db.session.commit()
            result=({'status':200})
        except Exception as e:
            logging.info("Exception in create function: "+str(e))
            result={'status':400,'reason':str(e)}
        return jsonify(result)
    else:
        return jsonify({"status":400,"message":"Invalid Token"})
    

@app.route('/api/update_record/<loopback>', methods=["PUT"])
@token_required
def update_record_by_loopback(token_value,loopback):
    """Function to update existing router record in DB

    Args:
        token_value (str): token to authenticate the API
        loopback (str): loopback value to update the record

    Returns:
        json: result json
    """
    if token_value == app.config['SECRET_KEY']:
        header=request.headers
        logging.info("Checking if x-access-token is passed in the header of request")
        if 'X-Access-Token' in header:
            token=header['X-Access-Token']
        else:
            logging.info("x-access-token is not passed in the header of request")
            result_json={"Status":"401","Message":"Authentication Error, Please pass X-Access-Token in headers"}
            return result_json
        results=[]
        get_router_details = Router.query.get(loopback)
        ##Checking if sap_id,hostname or macaddress are in the request. 
        if 'sap_id' in request.args:
            if request.args['sap_id']:
                get_router_details.Sapid = request.args['sap_id']
        if 'hostname' in request.args:
            if request.args['hostname']:
                get_router_details.Hostname = request.args['hostname']
        if 'macaddress' in request.args:
            if request.args['macaddress']:
                get_router_details.Macaddress = request.args['macaddress']
            
        db.session.commit()

        #Checking if the record has been updated in the DB
        details_router = Router.query.get(loopback)
        sap_id = details_router.Sapid
        hostname = details_router.Hostname
        loopback = details_router.Loopback
        macaddress = details_router.Macaddress
        result = {"sap_id":sap_id,"hostname":hostname,"loopback":loopback,"macaddress":macaddress}
        results.append(result)
        return (jsonify({"result": results}))
    else:
        return jsonify({"status":400,"message":"Invalid Token"})


@app.route('/api/all_routers', methods=['GET'])
@token_required
def all_routers(token_value):
    """Function to get details of all the routers

    Args:
        token_value (str): token to authenticate the API

    Returns:
        json: result json
    """
    if token_value == app.config['SECRET_KEY']:
        header=request.headers
        logging.info("Checking if x-access-token is passed in the header of request")
        if 'X-Access-Token' in header:
            token=header['X-Access-Token']
        else:
            logging.info("x-access-token is not passed in the header of request")
            result_json={"Status":"401","Message":"Authentication Error, Please pass X-Access-Token in headers"}
            return result_json
        data = Router.query.filter_by(status=True)
        results=[]
        for d in data:
            sap_id=d.Sapid
            hostname=d.Hostname
            loopback=d.Loopback
            macaddress=d.Macaddress
            result={"sap_id":sap_id,"hostname":hostname,"loopback":loopback,"macaddress":macaddress}
            results.append(result)

        return jsonify(status=200,result=results)
    else:
        return jsonify({"status":400,"message":"Invalid Token"})


@app.route('/api/delete_record/<loopback>', methods=['DELETE'])
@token_required
def delete_record_by_loopback(token_value,loopback):
    """Function to delete record on the basis of loopback

    Args:
        token_value (str): token to authenticate the API
        loopback (str): loopback value to delete record

    Returns:
        json: result json
    """
    if token_value == app.config['SECRET_KEY']:
        header=request.headers

        if 'X-Access-Token' in header:
            token=header['X-Access-Token']
        else:
            logging.info("x-access-token is not passed in the header of request")
            result_json={"Status":"401","Message":"Authentication Error, Please pass X-Access-Token in headers"}
            return result_json
        get_router_details = Router.query.get(loopback)
        get_router_details.status=False
        db.session.add(get_router_details)
        db.session.commit()
        return make_response("Record Deleted", 204)
    else:
        return jsonify({"status":400,"message":"Invalid Token"})



@app.route('/api/get/<start>/<end>', methods=['GET'])
@token_required
def findIPs(token_value,start, end):
    """Function to find routers within loopback range

    Args:
        token_value (str): token to authenticate API
        start (str): Start range of IP
        end (str): End range of IP

    Returns:
        json: result json
    """
    if token_value == app.config['SECRET_KEY']:
        header=request.headers
        if 'X-Access-Token' in header:
            token=header['X-Access-Token']
        else:
            logging.info("x-access-token is not passed in the header of request")
            result_json={"Status":"401","Message":"Authentication Error, Please pass X-Access-Token in headers"}
            return result_json
        results=[]
        ipstruct = struct.Struct('>I')
        start, = ipstruct.unpack(socket.inet_aton(start))
        end, = ipstruct.unpack(socket.inet_aton(end))
        ips=([socket.inet_ntoa(ipstruct.pack(i)) for i in range(start, end+1)])
        for ip in ips:
            get_router_details = Router.query.get(ip)
            if get_router_details:
                sap_id=get_router_details.Sapid
                hostname=get_router_details.Hostname
                loopback=get_router_details.Loopback
                macaddress=get_router_details.Macaddress
                result={"sap_id":sap_id,"hostname":hostname,"loopback":loopback,"macaddress":macaddress}
                results.append(result)
        return jsonify(status=200,result=results)
    else:
        return jsonify({"status":400,"message":"Invalid Token"})


if __name__ == '__main__':
	app.run()