from concurrent import futures
import grpc
import jwt
import redis
import bcrypt
import auth_pb2
import auth_pb2_grpc
import datetime
import json
import sys
VALID_TOKEN = "supersecret"

def get_root_creds(path):
    with open(path, 'rb') as cred_file:
            return cred_file.read()
    
redis_client = None

def generate_jwt(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=30),
    }
    return jwt.encode(payload, VALID_TOKEN, algorithm="HS256")

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def CreateUser(self, request, context):
        username = request.username
        password = request.password

        if redis_client.exists(username):
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("User already exists")
            return auth_pb2.AuthResponse(
                message=f"User already exists, Creation Failed"
            )
        else:
            mydict = {
                "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            }
            redis_client.set(username, json.dumps(mydict))
            return auth_pb2.AuthResponse(
                message=f"Hello {request.username}, Account Created"
            )
        
    def GetAuthenticated(self, request, context):
        username = request.username
        password = request.password
        
        if not redis_client.exists(username):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return auth_pb2.AuthResponse(
                message=f"User not found, Authentication Failed"
            )
        else:
            mydict = json.loads(redis_client.get(username))
            if bcrypt.checkpw(password.encode('utf-8'), mydict["password"].encode('utf-8')):
                token = generate_jwt(username)
                return auth_pb2.AuthResponse(
                    message=f"Hello {request.username}, Authentication Success.",
                    token=token
                )
            else:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid authentication token")
                return auth_pb2.AuthResponse(
                    message=f"Invalid credentials, Authentication Failed"
                )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server_credentials = grpc.ssl_server_credentials(
        (
            (
                get_root_creds('server.key'),
                get_root_creds('server.crt'),
            ),
        )
    )

    server.add_secure_port("[::]:50051", server_credentials)
    server.start()
    print("Server running on port 50051 with JWT authentication...")
    server.wait_for_termination()


if __name__ == "__main__":
    redis_client = redis.Redis.from_url(url="redis://default:a-very-complex-password-here@localhost:6379/0")
    if redis_client:
        print("Redis is connected.")
    else:
        print("Redis is not connected.")
        sys.exit(1)
    serve()
