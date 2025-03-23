import grpc
import jwt
import auth_pb2
import datetime
import auth_pb2_grpc
from server_auth import VALID_TOKEN

SERVER_ADDRESS = "localhost:50051"

def get_root_creds(path):
    with open(path, 'rb') as cred_file:
            return cred_file.read()
    
def write_token(token):
    with open("token.txt", 'w') as token_file:
        token_file.write(token)
        token_file.close()

def create_user(username, password):
    channel_credential = grpc.ssl_channel_credentials(
        get_root_creds("server.crt")
    )

    secure_channel = grpc.secure_channel(SERVER_ADDRESS, channel_credential)

    stub = auth_pb2_grpc.AuthServiceStub(secure_channel)

    try:
        response = stub.CreateUser(
            auth_pb2.AuthRequest(username=username, password=password)
        )
        print(f"Server Response: {response.message}")
    except grpc.RpcError as e:
        print(f"Authentication failed: {e.details()}")

def get_authenticated(username, password):
    channel_credential = grpc.ssl_channel_credentials(
        get_root_creds("server.crt")
    )

    secure_channel = grpc.secure_channel(SERVER_ADDRESS, channel_credential)

    stub = auth_pb2_grpc.AuthServiceStub(secure_channel)

    try:
        response = stub.GetAuthenticated(
            auth_pb2.AuthRequest(username=username, password=password)
        )
        print(f"Server Response: {response.message}")
        write_token(response.token)
    except grpc.RpcError as e:
        print(f"Authentication failed: {e.details()}")

if __name__ == "__main__":
    create_user("Alice", "supersecret")
    get_authenticated("Alice", "supersecret")