# grpc_redis

## Step 0: Install Docker Desktop & Minikube

### Download Docker Desktop and Start a Minikube Cluster

- **Docker:** [Download Docker Desktop](https://docs.docker.com/desktop/)
- **Minikube:** [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)

## Step 1: Generate Tokens & gRPC Code

### Generate Private Key
```sh
cd ./src
openssl genpkey -algorithm RSA -out server.key
```

### Generate Certificate Signing Request (CSR)
```sh
openssl req -new -key server.key -out server.csr
```
> **Note:** When asked for **FQDN** while creating the CSR, type `localhost`.

### Generate Certificate
```sh
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

### Generate gRPC Code
```sh
cd ../
python -m grpc_tools.protoc -I ./protos --python_out=./src --grpc_python_out=./src auth.proto
```

## Step 2: Install Redis

```sh
cd ./kubernetes
minikube start
kubectl create namespace redis
kubectl -n redis apply -f ./redis/redis-configmap.yaml
kubectl -n redis apply -f ./redis/redis-statefulset.yaml
kubectl -n redis apply -f ./redis-sentinel/sentinel-statefulset.yaml
kubectl -n redis port-forward pod/redis-0 6379:6379
```

## Step 3: Start Servers

```sh
cd ../src
python server_auth.py
python server_orders.py
```

## Step 4: Make Calls Using the Client

```sh
python client_auth.py
python client_orders.py
```

> **Note:** To successfully fetch orders, complete this step **within 30 seconds**. You can increase the timeout in the `generate_jwt()` function inside `server_auth.py`.

