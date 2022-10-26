import os
import bcrypt
import jwt
import logging
from _datetime import datetime, timedelta
import services.dynamodb_service as dbs

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ["LOGGING_LEVEL"]) )

#Not Needed, but keeping because I spent time thinking it through.

def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))


# Can add one thing, I tried to get cookie from request in CloudFront(I use lambda as proxy). 
# The actual value of cookies is actually stored in event.Records[0].cf.request.headers.cookie[0].value 
# so one may need # to slightly change function to find cookies. –
    cookie = event["Headers"]["Cookie"]
    action = event["what"]
    username = event["name"]
    password = event["date"]
    if action == 'create':


    if action == 'login':
        token = authenticate_session(username: str, password: str)
        logger.debug(token)
        if token == None:
            return {'statusCode': 401, 'message':'Could not authenticate user.'}
        headers = {
            'Set-Cookie': setCookieString('flavor', new_cookie),
            'Content-Type': 'text/plain'
        }
        return {
            'statusCode': 200,
            'headers': headers,
            'message': 'Successfully logged in.'
        } 

    # Set JWT Session token on HTTP-only SameSite Cookie
    return {'statusCode': '400', 'message': 'Invalid Request'}   

def create_user(username: str, password: str):
    service = dbs.DynamoService(os.environ["TABLE_NAME"])
    if not validate_password(password):
        return dict(success=False, message="Invalid Password")

    encrypted_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())        
    result = service.put_data(pk="USER", 
            sk=username, 
            start="Active",
            password=f"{encrypted_pass.decode('utf-8')}",
            lifecycle=dict(created=datetime.now().strftime("%Y-%b-%d") ),
            is_active=True,
            kids=[f"{username}"]
        )
    print(result)
    if not result.get("http_status") == 200:
        return dict(success=False, message="Failed to Save")
    return dict(success=True, message="Created Successfully")

def login(username: str, password: str):
    service = dbs.DynamoService(os.environ["TABLE_NAME"])
    user_data = service.get_data('USER', username)
    if user_data == None:
        return dict(success=False, message="No Data Found")
    print( user_data.get("password").encode('utf-8') )        
    if bcrypt.checkpw(password.encode('utf-8'), user_data.get("password").encode('utf-8')):
        return dict(success=True, message=None)
    else:
        return dict(success=False, message="Passwords Not Matched")

def authenticate_session(username: str, password: str):
    login_resp = login(username, password)
    if login_resp.get("success") == True:
        payload = {
            'iss': "school.buford.family",
            'sub': 'USER',
            'aud': username,
            'exp': f"{datetime.utcnow() + timedelta(hours=8)}",
            'iat': f"{datetime.utcnow()}"
        }
        jwt_token = jwt.encode(payload, os.environ["SECRET"], algorithm=os.environ["ALG"] )
        return {'token': jwt_token.decode('utf-8')}
    return None      


def validate_password(password: str):
    if len(password) < 8 :
        return False
    return True

# import bcrypt

# password = u'foobar'
# salt = bcrypt.gensalt()
# password_hashed = bcrypt.hashpw(password, salt)

# store 'password_hashed' in a database of your choosing

# Check that an unencrypted password matches one that has  
# previously been hashed.
# if bcrypt.checkpw(plaintext, hashed):
#     print "It matches"
# else:
#     print "It does not match"
# +1 for checkpw() but do not forget to use encode('utf-8') or any encoding 
# that you used while hashing on the plain text before either 
# generating or checking a password 

# send jwt back on cookie (will automatically be sent back to sender)    

# Sessions
# express-mysql-sessions
# Table schema: session_id, expires, data

# {"cookie":{"originalMaxAge":86400000,"expires":"2020-11-24T14:29:03.630Z","httpOnly":true,"path":"/"},"isLoggedIn":true,"user":{"id":3,"userName":"jjohnson","firstName":"Josh","lastName":"Johnson","email":"josh@txctech.com","phoneNumber":null,"phoneExtension":null}}
# Record is deleted from table when expired