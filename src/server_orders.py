from concurrent import futures
import grpc
import jwt
import redis
import auth_pb2
import auth_pb2_grpc
import json
import sys

VALID_TOKEN = "supersecret"
redis_client = None

def get_root_creds(path):
    with open(path, 'rb') as cred_file:
            return cred_file.read()

def validate_jwt(metadata):
    meatdata_dict = dict(metadata)
    token = meatdata_dict.get("authentication")

    if not token:
        return False
    try:
        payload = jwt.decode(token, VALID_TOKEN, algorithms=["HS256"])
        print("PAYLOAD: ", payload)
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

class JWTInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        if not validate_jwt(handler_call_details.invocation_metadata):
            context = grpc.ServicerContext()
            context.set_details("Invalid authentication token")
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing JWT Token")
            return None

        return continuation(handler_call_details)
    
class Orders(auth_pb2_grpc.OrdersServicer):
    def CreateOrders(self, request, context):
        customer_name = request.customer_name + "_orders"
        order_dict = dict(request.orders)

        redis_client.set(customer_name, json.dumps(order_dict))

        return auth_pb2.CreateOrderResponse(message="Your orders have been added successfully!!", orders=order_dict)
    
    def GetOrders(self, request, context):
        customer_name = request.customer_name + "_orders"

        if not redis_client.exists(customer_name):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("No orders found")
            return auth_pb2.CreateOrderResponse(message=f"No orders are present for {request.customer_name}", orders={})
        
        order_dict = json.loads(redis_client.get(customer_name))
        return auth_pb2.CreateOrderResponse(message="Here are your orders", orders=order_dict)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=[JWTInterceptor()])
    auth_pb2_grpc.add_OrdersServicer_to_server(Orders(), server)
    server_credentials = grpc.ssl_server_credentials(
        (
            (
                get_root_creds('server.key'),
                get_root_creds('server.crt'),
            ),
        )
    )

    server.add_secure_port("[::]:50052", server_credentials)
    server.start()
    print("Server running on port 50052 with JWT authentication...")
    server.wait_for_termination()


if __name__ == "__main__":
    redis_client = redis.Redis.from_url(url="redis://default:a-very-complex-password-here@localhost:6379/0")
    if redis_client:
        print("Redis is connected.")
    else:
        print("Redis is not connected.")
        sys.exit(1)
    serve()