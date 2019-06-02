DATE=$(shell date +%s | shasum | cut -d' ' -f1)
NAMESPACE := $(or ${NAMESPACE},${NAMESPACE},default)

define deploy_alttpbot
	-kubectl delete --namespace=${NAMESPACE} -f templates/${NAMESPACE}/deployment.yml
	kubectl apply --namespace=${NAMESPACE} -f templates/${NAMESPACE}/deployment.yml
endef

define deploy_worker
	-kubectl delete --namespace=${NAMESPACE} -f multiworld-worker/templates/${NAMESPACE}/deployment.yml
	kubectl apply --namespace=${NAMESPACE} -f multiworld-worker/templates/${NAMESPACE}/deployment.yml
endef

all:
	docker build -t registry.gigabit.nu/alttpbot/${NAMESPACE}:latest .
	docker build -t registry.gigabit.nu/multiworld-worker/${NAMESPACE}:latest -f multiworld-worker/Dockerfile --build-arg NAMESPACE=${NAMESPACE} .

push:
	docker push registry.gigabit.nu/alttpbot/${NAMESPACE}:latest
	docker push registry.gigabit.nu/multiworld-worker/${NAMESPACE}:latest

deploy: all push
	$(call deploy_alttpbot)
	$(call deploy_worker)

discord:
	docker build -t registry.gigabit.nu/alttpbot/${NAMESPACE}:latest .
	docker push registry.gigabit.nu/alttpbot/${NAMESPACE}:latest

worker:
	docker build -t registry.gigabit.nu/multiworld-worker/${NAMESPACE}:latest -f multiworld-worker/Dockerfile --build-arg NAMESPACE=${NAMESPACE} .
	docker push registry.gigabit.nu/multiworld-worker/${NAMESPACE}:latest

