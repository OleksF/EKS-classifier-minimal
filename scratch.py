from kubernetes import client, config
config.load_kube_config()
v1 = client.CoreV1Api()
pods = v1.list_pod_for_all_namespaces()
print(pods.items[0])