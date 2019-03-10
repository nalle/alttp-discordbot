DATE=$(shell date +%s)

all:
	docker build -t alttpbot .

deploy:
	docker build -t registry.gigabit.nu:5000/alttpbot:${DATE} .
	docker push registry.gigabit.nu:5000/alttpbot:${DATE}
	kubectl --record deployment.apps/alttpbot set image deployment.v1.apps/alttpbot alttpbot=registry.gigabit.nu:5000/alttpbot:${DATE}

reset:
	kubectl delete -f deployment.yml
	kubectl apply -f deployment.yml
