from kubernetes import client, config
from flask import Flask,request
from os import path
import yaml, random, string, json
import sys
import json

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
v1 = client.CoreV1Api()
app = Flask(__name__)
# app.run(debug = True)

@app.route('/config', methods=['GET'])
def get_config():
    """
    Fetch cluster configuration info.
    
    BODY: { "pods": [pod1, pod2 ...]}
    pods : a list of pods
    a pod:  {"node" : "node on which the pod is executing", "ip" : "ip address of the pod",
        "namespace" : "namespace of the node", "name" : "name of the pod", "status":"status of the pod"}
    """
    pods = []
    
    
    pods = []
    all_pods = v1.list_pod_for_all_namespaces()
    for pod in all_pods.items:
        pods.append({"node":pod.spec.node_name, "ip": pod.status.pod_ip, "namespace":pod.metadata.namespace, "name":pod.metadata.name, "status":pod.status.phase})
    
    output = {"pods": pods}
    output = json.dumps(output)

    return output

@app.route('/img-classification/free',methods=['POST'])
def post_free():
    """
    Create a job based on a POST request to the free tier, letting k8s do the routing as specified in the yaml w/ cluster config.
    """
    with open("classify_free_job.yaml", 'r') as fl:
        job = yaml.safe_load(fl)
    api = client.BatchV1Api()
    status = api.create_namespaced_job(namespace="free-service", body=job)
    return "success", 200


@app.route('/img-classification/premium', methods=['POST'])
def post_premium():
    """
    Create a job based on a POST request to the premium tier, letting k8s do the routing as specified in the yaml w/ cluster config.
    """
    with open("classify_premium_job.yaml", 'r') as fl:
        job = yaml.safe_load(fl)
    api = client.BatchV1Api()
    status = api.create_namespaced_job(namespace="default", body=job)
    return "success", 200

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
