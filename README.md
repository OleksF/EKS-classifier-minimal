# EKS-classifier-minimal

Runs a free and paid tier classification service on some mock data using EKS backend with eksctl.

Following files from UIUC CS498, Spring 2022:
- `classify.py`
- `requirements.txt`

## Setup

### App containerization

Build docker image with Dockerfile in this repo. Name format should match DockerHub format of `{user}/{repo}[:tag]`, where `user` is DockerHub username.

```
docker build -t ofirsov/uiuc-cs498-mp12:0.1 .
```

Test Docker image. Should show simple feed forward NN classifier training loss over epochs and eventually accuracy of ~97%.

```
docker run -e "DATASET=mnist" -e "TYPE=ff" ofirsov/uiuc-cs498-mp12:0.1
```

For convenience, push image to DockerHub. To do this, create repo in browser, login on CLI, then push.

```
docker login
docker push ofirsov/uiuc-cs498-mp12:0.1
```

### Provision & ready EKS cluster

Set up AWS CLI.

```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Configure AWS CLI credentials. More details on this externally.

```
aws configure
```

Set up kubectl.

```
curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
kubectl version --short --client
```

Set up eksctl.

```
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

Using eksctl, set up cluster.

```
eksctl create cluster -f clstr.yaml --name cs498-mp12-cluster
```

Verify cluster nodes.

```
kubectl get nodes
```

To delete all created AWS resources, run below.

```
eksctl delete cluster --name cs498-mp12-cluster
```


### K8s configuration

Everything here can be run from a minimal EC2 instance.

Create namespaces for premium (default) and free tiers.

```
kubectl create namespace default
kubectl create namespace free-service
```

Apply ResourceQuota to free tier namespace.

```
kubectl apply -f https://raw.githubusercontent.com/OleksF/scratch/main/classify_free_rq.yaml --namespace=free-service
```

Build the pods.

```
kubectl create -f https://raw.githubusercontent.com/OleksF/scratch/main/mp12.yaml
```

### Testing job YAML with microkube

...

```
kubectl create -f https://raw.githubusercontent.com/OleksF/scratch/main/classify_free_job.yaml
kubectl get jobs --watch
kubectl get job classify-free-job
kubectl get pods
```

Using pod ID from last output, print off bash output from running container in job.

```
kubectl logs classify-free-job-{pod ID}
```