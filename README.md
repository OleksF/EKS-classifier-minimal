# EKS-classifier-minimal

In layman's terms, this sets up the cloud machinery to reliably run predictions on a model hosted in the cloud from standard REST calls (as in Ml prediction requests made from your web pages, mobile apps, etc). Once your data scientists build a model, this can be used to deploy it in the state of the art Kubernetes (aka k8s) infrastructure framework. Features:
- different levels of service based on user tier (free or paying)
- load balancing between several instances of the model so that responses won't get slow with increased traffic
- spinning up and shutting down resources as needed so that you're not overpaying for cloud use when you scale
- continuous availability instead of waiting on the data science team to send an excel sheet or push new predictive scores once in a blue moon

Everything that follows is technical...

---

The following files are from UIUC CS498, Spring 2022:
- `classify.py` - MNIST handwritten digits classifier; can be any classifier though
- `requirements.txt` - computing environment req's

Built on an AWS EKS backend with eksctl.

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

In EC2...

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

Pull scripts.

```
curl https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/clstr.yaml > clstr.yaml
```

Using eksctl, set up cluster.

```
eksctl create cluster -f clstr.yaml
```

Verify cluster nodes.

```
kubectl get nodes
```

To delete all created AWS resources, run below.

```
eksctl delete cluster --name {cluster name from clstr.yaml}
```


### K8s configuration

Everything here can be run from a minimal AWS EC2 instance.

Create namespaces for premium (default, already exists) and free tiers.

```
kubectl create namespace free-service
```

Apply ResourceQuota to free tier namespace.

```
kubectl create -f https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/classify_free_rq.yaml --namespace=free-service
```

Build the pods.

```
kubectl create -f https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/classify_free_job.yaml --namespace=free-service
kubectl create -f https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/classify_premium_job.yaml --namespace=default
```

Check for 3 default pods and 2 free-service ones.

```
kubectl get pods -A
```

To tear it all down...

```
eksctl delete cluster --name {cluster name from clstr.yaml}
```

### Server setup

```
curl https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/server.py > server.py
curl https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/classify_free_job.yaml > classify_free_job.yaml
curl https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/classify_premium_job.yaml > classify_premium_job.yaml
```

### Testing job YAML with microkube

Local debugging option with microkube running locally instead of in the cloud.

```
kubectl create -f https://raw.githubusercontent.com/OleksF/EKS-classifier-minimal/main/classify_free_job.yaml
kubectl get jobs --watch
kubectl get job classify-free-job
kubectl get pods
```

Using pod ID from last output, print off bash output from running container in job.

```
kubectl logs classify-free-job-{pod ID}
```
