==== Local prep and testing ====

--== App containerization ==--

# create Dockerfile as below
``` Dockerfile
FROM python:3.6-slim-buster

    # get curl
RUN apt update \
    && apt-get install curl -y \
    # get required packaged
    && curl https://raw.githubusercontent.com/UIUC-CS498-Cloud/MP12_PublicFiles/main/requirements.txt --output requirements.txt \
    && yes | pip --no-cache-dir install -r requirements.txt \
    # get python script
    && curl https://raw.githubusercontent.com/UIUC-CS498-Cloud/MP12_PublicFiles/main/classify.py --output classify.py

CMD ["python","-u","classify.py"]
```


# build docker image
docker build -t ofirsov/uiuc-cs498-mp12:0.1 . 
# test docker image
docker run -e "DATASET=mnist" -e "TYPE=ff" ofirsov/uiuc-cs498-mp12:0.1

# push to DockerHub
# first create repo in browser...
# log in on CLI
docker login
# now push
docker push ofirsov/uiuc-cs498-mp12:0.1


--== K8s job configuration ==--

Free job w/ container as hosted above, with env vars set

``` mp12.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: classify-free-job
spec:
  template:
    spec:
      containers:
      - name: classify-free-job
        image: ofirsov/uiuc-cs498-mp12:0.1
        env:
        - name: DATASET
          value: "mnist"
        - name: TYPE
          value: "ff"
        resources:
          limits:
            cpu: "0.9"
      restartPolicy: Never
  backoffLimit: 4
```

# Host on github
# now, run locally
kubectl create -f https://raw.githubusercontent.com/OleksF/scratch/main/mp12.yaml
# this gives
> job.batch/classify-mnist-ff-free created

# check status
kubectl get job classify-mnist-ff-free
# should not immediately show completed
# can instead watch
kubectl get jobs --watch
# once done, check again
kubectl get job classify-mnist-ff-free

# check created pods
kubectl get pods

# show pod log
kubectl logs classify-mnist-ff-free-bhg95


--== K8s job configuration ==--



# create premium namespace
kubectl create namespace default
# create free namespace
kubectl create namespace free-service
kubectl apply -f https://k8s.io/examples/admin/resource/quota-mem-cpu.yaml --namespace=free-service

kubectl create -f https://raw.githubusercontent.com/OleksF/scratch/main/mp12_free.yaml


to start cluster...

# locally set up AWS CLI and eksctl

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# AWS credentials
# set up an administrator account (or one with appropriate privileges...)
aws configure

# kubectl
curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
kubectl version --short --client



# run the cluster
eksctl create cluster -f clstr.yaml --name cs498-mp12-cluster

# get nodes
kubectl get nodes

# shut down the cluster, deleting all AWS resources
eksctl delete cluster --name cs498-mp12-cluster






