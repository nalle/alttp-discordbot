from kubernetes import client, config, utils
from ruamel.yaml import YAML
import datetime

yaml = YAML()
config.load_kube_config()

class Kubernetes():
    def __init__(self):
        config.load_kube_config()

    def create_persistent_volume(self, body):
        try:
            dep = yaml.load(body)
            k8s = client.CoreV1Api()
            resp = k8s.create_persistent_volume(
                body=dep)
        except Exception as e:
            return e

    def create_service(self, body):
        try:
            dep = yaml.load(body)
            k8s = client.CoreV1Api()
            resp = k8s.create_namespaced_service(
                body=dep, namespace=os.environ.get("NAMESPACE", "default"))
            return resp
        except Exception as e:
            return e

    def create_deployment(self, body):
        try:
            dep = yaml.load(body)
            k8s = client.AppsV1beta2Api()
            resp = k8s.create_namespaced_deployment(
                body=dep, namespace=os.environ.get("NAMESPACE", "default"))
            return resp
        except Exception as e:
            return e

    def create_persistent_volumeclaim(self, body):
        try:
            dep = yaml.load(body)
            k8s = client.CoreV1Api()
            resp = k8s.create_namespaced_persistent_volume_claim(
                body=dep, namespace=os.environ.get("NAMESPACE", "default"))
            return resp
        except Exception as e:
            return e

    def create_job(self, body):
        try:
            dep = yaml.load(body)
            dep['spec']['ttlSecondsAfterFinished'] = int(dep['spec']['ttlSecondsAfterFinished']) 
            dep['spec']['backoffLimit'] = int(dep['spec']['backoffLimit']) 
            k8s = client.BatchV1Api()
            resp = k8s.create_namespaced_job(
                body=dep, namespace=os.environ.get("NAMESPACE", "default"))
            return resp
        except Exception as e:
            return e

    def delete_job(self, name):
        k8s = client.BatchV1Api()
        resp = k8s.delete_namespaced_job(
            name=name, namespace=os.environ.get("NAMESPACE", "default"))
        return resp

    def delete_service(self, name):
        k8s = client.CoreV1Api()
        resp = k8s.delete_namespaced_service(
            name=name, namespace=os.environ.get("NAMESPACE", "default"))
        return resp

    def delete_pod(self, name):
        k8s = client.CoreV1Api()
        resp = k8s.delete_namespaced_pod(
            name=name, namespace=os.environ.get("NAMESPACE", "default"))
        return resp

    def delete_deployment(self, name):
        k8s = client.AppsV1beta2Api()
        resp = k8s.delete_namespaced_deployment(
            name=name, namespace=os.environ.get("NAMESPACE", "default"))
        return resp

    def delete_replica_set(self, name):
        k8s = client.AppsV1beta2Api()
        resp = k8s.delete_namespaced_replica_set(
            name=name, namespace=os.environ.get("NAMESPACE", "default"))
        return resp


    def read_log(self, name):
        k8s = client.CoreV1Api()
        return k8s.read_namespaced_pod_log(name=name, namespace=os.environ.get("NAMESPACE", "default"))

    def list_jobs(self):
        k8s = client.BatchV1Api()
        return k8s.list_namespaced_job(namespace=os.environ.get("NAMESPACE", "default"), pretty=True)

    def list_pods(self):
        k8s = client.CoreV1Api()
        return k8s.list_namespaced_pod(namespace=os.environ.get("NAMESPACE", "default"), pretty=True)

    def list_services(self):
        k8s = client.CoreV1Api()
        return k8s.list_namespaced_service(namespace=os.environ.get("NAMESPACE", "default"), pretty=True)

    def list_deployments(self):
        k8s = client.AppsV1beta2Api()
        return k8s.list_namespaced_deployment(namespace=os.environ.get("NAMESPACE", "default"), pretty=True)

    def list_replica_sets(self):
        k8s = client.AppsV1beta2Api()
        return k8s.list_namespaced_replica_set(namespace=os.environ.get("NAMESPACE", "default"), pretty=True)


    def cleanup_services(self, ttl = 86400):
        retvar = False
        for service in self.list_services().to_dict()['items']:
            if service['metadata']['creation_timestamp'] < datetime.datetime.now(service['metadata']['creation_timestamp'].tzinfo)-datetime.timedelta(seconds=ttl):
                if "multiworld-server" in service['metadata']['name']:
                    print("Deleteing {}".service(pods['metadata']['name']))
                    self.delete_service(service['metadata']['name'])
                    retvar = True
    
        return retvar

    def cleanup_pods(self, ttl = 86400):
        retvar = False
        for pod in self.list_pods().to_dict()['items']:
            if pod['metadata']['creation_timestamp'] < datetime.datetime.now(pod['metadata']['creation_timestamp'].tzinfo)-datetime.timedelta(seconds=ttl):
                if "multiworld-server" in pod['metadata']['name']:
                    print("Deleteing {}".format(pods['metadata']['name']))
                    self.delete_pod(pod['metadata']['name'])
                    retvar = True
    
        return retvar
 
    def cleanup_replica_sets(self, ttl = 86400):
        retvar = False
        for replica_set in self.list_replica_sets().to_dict()['items']:
            if replica_set['metadata']['creation_timestamp'] < datetime.datetime.now(replica_set['metadata']['creation_timestamp'].tzinfo)-datetime.timedelta(seconds=ttl):
                if "multiworld-server" in replica_set['metadata']['name']:
                    print("Deleteing {}".format(replica_set['metadata']['name']))
                    self.delete_replica_set(replica_set['metadata']['name'])
                    retvar = True
    
        return retvar
 
    
    def cleanup_deployments(self, ttl = 86400):
        retvar = False
        for deployment in self.list_deployments().to_dict()['items']:
            if deployment['metadata']['creation_timestamp'] < datetime.datetime.now(deployment['metadata']['creation_timestamp'].tzinfo)-datetime.timedelta(seconds=ttl):
                if "multiworld-server" in deployment['metadata']['name']:
                    print("Deleteing {}".format(deployment['metadata']['name']))
                    self.delete_deployment(deployment['metadata']['name'])
                    retvar = True
    
        return retvar
    
    def cleanup_batchjobs(self, ttl = 7200):
        retvar = False
        for job in self.list_jobs().to_dict()['items']:
            if job['metadata']['creation_timestamp'] < datetime.datetime.now(job['metadata']['creation_timestamp'].tzinfo)-datetime.timedelta(seconds=ttl):
                if "multiworld-server" in job['metadata']['name']:
                    print("Deleteing {}".format(job['metadata']['name']))
                    self.delete_job(service['metadata']['name'])
                    retvar = True
    
        return retvar
    


