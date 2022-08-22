ENV ?= dev
COMPONENT ?= frontend

# frontend PORT=8501, backend PORT=8502
PORT ?= 8501

GCR_REPO ?= gcr.io/personal-351003
MLFLOW_GS_ARTIFACT_PATH ?= gs://personal-mlflow-tracking/artifacts


# Initialize project
.PHONY: install
install:
	python -m pip install -e ".[dev]" --no-cache-dir


# Pre commit hooks
.PHONY: install-pre-commit
install-pre-commit:
	pre-commit install
	pre-commit autoupdate

.PHONY: run-pre-commit
run-pre-commit:
	pre-commit run --all-files


# Styling
.PHONY: style
style:
	black .
	isort .
	flake8


# Cleaning
.PHONY: clean
clean: style
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E "pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -f .coverage


# DVC
.PHONY: dvc
dvc:
	dvc add data/restaurant/orders.csv
	dvc add data/restaurant/SampleSubmission.csv
	dvc add data/restaurant/test_customers.csv
	dvc add data/restaurant/test_full.csv
	dvc add data/restaurant/test_locations.csv
	dvc add data/restaurant/train_customers.csv
	dvc add data/restaurant/train_full.csv
	dvc add data/restaurant/train_locations.csv
	dvc add data/restaurant/VariableDefinitions.txt
	dvc add data/restaurant/vendors.csv
	dvc push


# Test
.PHONY: test
test:
	pytest


# Local Docker
docker-build:
	docker image build -f $(COMPONENT)/Dockerfile . \
		-t kubernetes-devops-$(COMPONENT):latest

docker-run:
	make docker-build $(COMPONENT)
	docker run -p $(PORT):$(PORT) kubernetes-devops-$(COMPONENT):latest

docker-push:
	docker login
	docker image tag kubernetes-devops-$(COMPONENT):latest $(GCR_REPO)/kubernetes-devops-$(COMPONENT):latest
	docker push $(GCR_REPO)/kubernetes-devops-$(COMPONENT):latest

docker-build-push-pipeline:
	docker build --tag $(GCR_REPO)/kubernetes-devops-pipeline-$(COMPONENT):v1 -f pipeline/Dockerfile . \
		&& docker push $(GCR_REPO)/kubernetes-devops-pipeline-$(COMPONENT):v1


# Kubernetes
minikube-start:
	minikube start --memory 8192 --cpus 8
	minikube addons enable gcp-auth
	minikube dashboard

create-namespaces:
	kubectl apply -f kubernetes/namespace.yaml


# Skaffold
skaffold-run:
	skaffold run -f skaffold/$(COMPONENT).yaml --tail --port-forward

skaffold-dev:
	skaffold dev -m skaffold/$(COMPONENT).yaml --tail --port-forward


# Kubernetes GCR Authentication
minikube-addons:
	minikube addons disable gcp-auth
	minikube addons enable gcp-auth


# MLFlow Docker
mlflow-postgres-docker-run:
	docker run --name mlflow-database \
		-v C:\Users\Grainer\Projects\kubernetes-devops\mlflow-db:/bitnami/postgresql \
		-e POSTGRESQL_USERNAME=admin \
		-e POSTGRESQL_PASSWORD=password \
		-e POSTGRESQL_DATABASE=mlflow-tracking-server-db \
		--expose 5432 \
		-p 5432:5432 \
		bitnami/postgresql

mlflow-docker-build:
	docker build . -f mlflow/Dockerfile -t mlflow:1.0

mlflow-docker-run:
	- docker stop mlflow & docker rm mlflow
	docker run --name mlflow \
	-v C:\Users\Grainer\Projects\kubernetes-devops\secrets:/workdir/gcloud-credentials/ \
	-e ARTIFACT_STORE=gs://personal-mlflow-tracking/artifacts \
	-p 5000:5000 \
	--link mlflow-database \
	mlflow:1.0


# MLFlow Kubernetes
mlflow-install:
	make mlflow-object-credentials-add
	make mlflow-postgres-install
	make mlflow-build
	kubectl apply -f kubernetes/configmap.yaml
	kubectl apply -f kubernetes/mlflow.yaml

mlflow-object-credentials-add:
	- kubectl delete secret gcsfs-creds
	kubectl create secret generic gcsfs-creds --from-file=secrets/gcloud-credentials.json

mlflow-postgres-install:
	helm repo add bitnami https://charts.bitnami.com/bitnami

	- helm delete mlflow-db
	- kubectl delete pvc data-mlflow-db-postgresql-0

	helm install mlflow-db bitnami/postgresql \
		-f mlflow/postgresql-values.yaml

mlflow-build:
	docker build . -f mlflow/Dockerfile -t ${GCR_REPO}/mlflow:1.0
	docker push ${GCR_REPO}/mlflow:1.0


# MongoDB
mongodb-install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install mongodb bitnami/mongodb


# Kafka
kafka-install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install kafka bitnami/kafka


# Script
kubernetes-script-run:
	docker build . -f scripts/Dockerfile -t ${GCR_REPO}/kubernetes-devops-script:1.0
	docker push ${GCR_REPO}/kubernetes-devops-script:1.0

	- kubectl delete -f kubernetes/script.yaml
	kubectl apply -f kubernetes/script.yaml

	timeout 5

	kubectl logs job/script -f


# Recommender Trainer
recommender-train:
	make recommender-engine-build

	- kubectl delete -f kubernetes/recommender-trainer.yaml
	kubectl apply -f kubernetes/recommender-trainer.yaml

	timeout 5

	kubectl logs job/recommender-trainer -f


# Recommender Engine
recommender-engine-build:
	docker build . -f recommender/Dockerfile -t ${GCR_REPO}/recommender-engine:1.0
	docker push ${GCR_REPO}/recommender-engine:1.0


# Consumer
consumer-build:
	docker build . -f recommender/Dockerfile -t ${GCR_REPO}/kubernetes-devops-consumer:1.0
	docker push ${GCR_REPO}/kubernetes-devops-consumer:1.0


# Backend
backend-build:
	docker build . -f recommender/Dockerfile -t ${GCR_REPO}/kubernetes-devops-backend:1.0
	docker push ${GCR_REPO}/kubernetes-devops-backend:1.0


# Frontend
frontend-build:
	docker build . -f recommender/Dockerfile -t ${GCR_REPO}/kubernetes-devops-frontend:1.0
	docker push ${GCR_REPO}/kubernetes-devops-frontend:1.0


# Fluentd
fluentd-build:
	docker build . -f fluentd/Dockerfile -t ${GCR_REPO}/fluentd:1.0
	docker push ${GCR_REPO}/fluentd:1.0


# Helm Prometheus
helm-prometheus-repo-add:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

helm-prometheus-install:
	helm install prometheus prometheus-community/kube-prometheus-stack

grafana-port-forward:
	kubectl port-forward deployment/prometheus-grafana 3000	# admin/prom-operator

prometheus-port-forward:
	kubectl port-forward prometheus-prometheus-kube-prometheus-prometheus-0 9090


# Argo CD
argo-cd:
	kubectl create namespace argocd
	kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

argo-cd-port-forward:
	kubectl port-forward svc/argocd-server -n argocd 8080:443

argo-cd-cli-setup:
	argocd login 127.0.01:8080
	argocd cluster add minikube


# Argo
argo-cli-install:
	curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.2.9/argo-darwin-amd64.gz
	gunzip argo-darwin-amd64.gz
	chmod +x argo-darwin-amd64
	mv ./argo-darwin-amd64 /usr/local/bin/argo
	argo version

argo-deploy-components:
	kubectl apply -f pipeline/argo-component-manifest/argo-workflow.yaml

	# kubectl apply -f pipeline/argo-component-manifest/argo-events.yaml
	# kubectl apply -f pipeline/argo-component-manifest/event-bus.yaml
	# kubectl apply -f pipeline/argo-component-manifest/event-source.yaml

	# kubectl apply -f pipeline/argo-component-manifest/workflow-service-account.yaml

argo-workflow-port-forward:
	kubectl port-forward deployment/argo-server 2746:2746

argo-workflow-template-deploy:
	argo template lint pipeline/argo-manifest/workflow-template.yaml
	- argo template delete my-workflow-template
	argo template create pipeline/argo-manifest/workflow-template.yaml

argo-workflow-submit:
	argo submit --from workflowtemplate/my-workflow-template

argo-events-deploy:
	kubectl delete -f pipeline/argo-manifest/webhook-sensor.yaml
	kubectl apply -f pipeline/argo-manifest/webhook-sensor.yaml
	make argo-events-port-forward

argo-events-port-forward:
	$(eval ARGO_WEBHOOK_POD_NAME := $(shell kubectl get pod -l eventsource-name=webhook -o name))
	kubectl port-forward $(ARGO_WEBHOOK_POD_NAME) 12000:12000

curl-argo-events:
	curl -d '{"message":"Hello there"}' -H "Content-Type: application/json" -X POST http://localhost:12000/deploy


# MongoDB
helm-install-mongodb:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install kubernetes-devops-mongo bitnami/mongodb

mongodb-password:
	kubectl get secret --namespace kubernetes-devops-$(ENV) kubernetes-devops-mongo-mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 --decode

mongodb-port-forward:
	kubectl port-forward --namespace kubernetes-devops-$(ENV) svc/kubernetes-devops-mongo-mongodb 27011:27017


# Redis
helm-install-redis:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install kubernetes-devops-redis bitnami/redis


# ElasticSearch
helm-install-elasticsearch:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install kubernetes-devops-elasticsearch bitnami/elasticsearch

elasticsearch-port-forward:
	kubectl port-forward --namespace kubernetes-devops-dev svc/kubernetes-devops-elasticsearch-coordinating-only 9200:9200 & \
    	curl http://127.0.0.1:9200/


# Fluentd
helm-install-fluentd:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install kubernetes-devops-fluentd bitnami/fluentd
