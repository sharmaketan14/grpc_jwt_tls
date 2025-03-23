import grpc
import jwt
import auth_pb2
import auth_pb2_grpc
from server_orders import VALID_TOKEN

SERVER_ADDRESS = "localhost:50052"

def get_root_creds(path):
    with open(path, 'rb') as cred_file:
            return cred_file.read()

class AuthMetadataPlugin(grpc.AuthMetadataPlugin):
    def __init__(self, token):
        self._token = token
    def __call__(self, context, callback):
        metadata = (("authentication", self._token),)
        callback(metadata, None)

def create_orders(customer_name, order_list, token):
    auth_plugin = AuthMetadataPlugin(token)
    call_credentials = grpc.metadata_call_credentials(auth_plugin)
    channel_credential = grpc.ssl_channel_credentials(
        get_root_creds("server.crt")
    )

    composite_credentials = grpc.composite_channel_credentials(channel_credential, call_credentials)
    secure_channel = grpc.secure_channel(SERVER_ADDRESS, composite_credentials)

    stub = auth_pb2_grpc.OrdersStub(secure_channel)

    try:
        response = stub.CreateOrders(auth_pb2.CreateOrderRequest(customer_name=customer_name, orders=order_list))
        print(f"Server Response: {response.message}\n{response.orders}")
    except grpc.RpcError as e:
        print(f"Authentication failed: {e.details()}")

def get_orders(customer_name, token):
    auth_plugin = AuthMetadataPlugin(token)
    call_credentials = grpc.metadata_call_credentials(auth_plugin)
    channel_credential = grpc.ssl_channel_credentials(
        get_root_creds("server.crt")
    )

    composite_credentials = grpc.composite_channel_credentials(channel_credential, call_credentials)
    secure_channel = grpc.secure_channel(SERVER_ADDRESS, composite_credentials)

    stub = auth_pb2_grpc.OrdersStub(secure_channel)

    try:
        response = stub.GetOrders(auth_pb2.CreateOrderRequest(customer_name=customer_name))
        print(f"Server Response: {response.message}\n{response.orders}")
    except grpc.RpcError as e:
        print(f"Authentication failed: {e.details()}")

if __name__ == "__main__":
    with open("token.txt", 'r') as token_file:
        token = token_file.read()
        token_file.close()
    #create_orders("Alice", {"apple": 120, "banana": 70}, token)
    get_orders("Alice", token)