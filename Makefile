DATE=$(shell date +%s | shasum | cut -d' ' -f1)

all:
	docker build -t registry.gigabit.nu/alttpbot:latest .

deploy:
	docker build -t registry.gigabit.nu/alttpbot:latest .
	docker push registry.gigabit.nu/alttpbot:latest
	-kubectl delete -f deployment.yml
	kubectl apply -f deployment.yml

reset:
	-kubectl delete -f deployment.yml
	kubectl apply -f deployment.yml

worker:
	docker build -t registry.gigabit.nu/multiworld-worker:latest -f multiworld-worker/Dockerfile .
	docker push registry.gigabit.nu/multiworld-worker:latest
	-kubectl delete -f multiworld-worker/deployment.yml
	kubectl apply -f multiworld-worker/deployment.yml
