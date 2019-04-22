DATE=$(shell date +%s | shasum | cut -d' ' -f1)

all:
	docker build -t registry.gigabit.nu/alttpbot:${DATE} .

deploy:
	docker build -t registry.gigabit.nu/alttpbot:${DATE} .
	docker push registry.gigabit.nu/alttpbot:${DATE}
	kubectl --record deployment.apps/alttpbot set image deployment.v1.apps/alttpbot alttpbot=registry.gigabit.nu/alttpbot:${DATE}

reset:
	kubectl delete -f deployment.yml
	kubectl apply -f deployment.yml
