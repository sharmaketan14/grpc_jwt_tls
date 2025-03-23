# grpc_redis

## Step - 0: Install Docker Desktop & Minikube

### Dowload Docker Desktop and Start a Minikube Cluster

Docker: https://docs.docker.com/desktop/?_gl=1*k8mbhh*_gcl_au*MzQ0ODcyODkwLjE3NDI3NjU4NzU.*_ga*MTc2ODAyNDc1NS4xNzMzNjM4MTQ4*_ga_XJWPQMJYHQ*MTc0Mjc2NTg2My4xNC4xLjE3NDI3NjU4NzUuNDguMC4w

Minikube: https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download

## Step - 1: Generate Tokens & GRPC Code

### Generate Private Key

cd ./src
openssl genpkey -algorithm RSA -out server.key

### Generate Certificate Signing Request

openssl req -new -key server.key -out server.csr

### Generate Certificate

openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

When asked for FQDN while creating CSR, type localhost.

cd ../
python -m grpc_tools.protoc -I ./protos --python_out=./src --grpc_python_out=./src auth.proto

## Step - 2: Install Redis

cd ./kubernetes
minikube start
kubectl create ns redis
kubectl -n redis apply -f ./redis/redis-configmap.yaml
kubectl -n redis apply -f ./redis/redis-statefulset.yaml
kubectl apply -n redis -f ./redis-sentinel/sentinel-statefulset.yaml
kubectl -n redis port-forward pod/redis-0 6379:6379

## Step - 3: Start Servers

cd ../src
python server_auth.py
python server_orders.py

## Step - 4: Make calls using client

python client_auth.py
python client_orders.py

To succesfully fetch orders do this step under 30 seconds.
You can increase time in generate_jwt() in server_auth.py file.
