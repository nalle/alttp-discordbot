from bot.k8s import Kubernetes
from jinja2 import Template
import xkcdpass.xkcd_password as xp
import datetime
import time
import re
import os
import random
import string
import json
import redis

k8s = Kubernetes()


class Multiworld():

    def randomString(self, stringLength=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def generate_template(self, template=None, **kwargs):
        with open(template) as f:
            t = Template(f.read())

        return t.render(kwargs)

    def get_port(self):
        services = k8s.list_services()
        port = random.randint(10000,65535)
        ports = []
        for service in services.to_dict()['items']:
            ports.append(service['spec']['ports'][0]['target_port'])

        if port in ports:
            return self.get_port()
        else:
            return port

    def generate_password(self):
        def capitalize_first_letter(s):
            new_str = []
            s = s.split(" ")
            for i, c in enumerate(s):
                new_str.append(c.capitalize())
            return "".join(new_str)


        words = xp.locate_wordfile()
        mywords = xp.generate_wordlist(wordfile=words, min_length=5, max_length=8)
        raw_password = xp.generate_xkcdpassword(mywords)

        return capitalize_first_letter(raw_password)

    def _poll_job(self, job):
        roms = []
        multidata = ""
        wait_for_seed = True

        while wait_for_seed:
            for item in k8s.list_jobs().to_dict()['items']:
                if item['status']['succeeded'] and item['metadata']['name'] == job.to_dict()['metadata']['labels']['job-name']:
                    k8s.delete_job(item['metadata']['name'])
                    for pod in k8s.list_pods().to_dict()['items']:
                        if pod['status']['conditions'][0]['reason'] == "PodCompleted":
                            seed = re.findall("Seed: ([0-9]+)", k8s.read_log(pod['metadata']['name']))[0]
                            k8s.delete_pod(pod['metadata']['name'])
                            for directories, crap, files in os.walk("/multiworld"):
                                for file in files:
                                    if seed in file:
                                        if "multidata" in file:
                                            multidata = file
                                        else:
                                            roms.append(file)
                    wait_for_seed = False
                time.sleep(1)
        return multidata, roms

    def create_multiworld(self, uuid, **kwargs):
        redis_host = os.environ.get('REDIS_HOST') or "127.0.0.1"
        redis_port = os.environ.get('REDIS_PORT') or 6379
        redis_password = os.environ.get('REDIS_PASSWORD') or None

        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
        )

        self.arguments = []
        for k, v in kwargs.items():
            self.arguments.append("--{}".format(k))
            self.arguments.append("{}".format(v))

        password = self.generate_password()
        port = self.get_port()
        hashid = self.randomString()

        pv = k8s.create_persistent_volume(
            self.generate_template(
                template="templates/k8s-persistent-volume",
            )
        )

        pvc = k8s.create_persistent_volumeclaim(
            self.generate_template(
                template="templates/k8s-persistent-volume-claim",
            )
        )

        job = k8s.create_job(
            self.generate_template(
                template="templates/k8s-batchjob",
                name="multiworld-generator-{}".format(hashid),
                arguments=self.arguments,
            )
        )

        multidata, roms = self._poll_job(job)

        deployment = k8s.create_deployment(
            self.generate_template(
                template="templates/k8s-deployment",
                name="multiworld-server-{}".format(hashid),
                port=port,
                password=password,
                multidata=multidata,
            )
        )
        service  = k8s.create_service(
            self.generate_template(
                template="templates/k8s-service",
                name="multiworld-server-{}".format(hashid),
                port=port,
            )
        )

        output_data = json.dumps({
            "server": {
                "host": "alttp.gigabit.nu",
                "port": port,
                "password": password
            },
            "roms": roms
        })

        r.set(uuid, output_data)

        return output_data


def start_multiworld_job(*args, **kwargs):
    m = Multiworld()
    m.create_multiworld(*args, **kwargs)
