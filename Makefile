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
		-t recommender-devops-$(COMPONENT):latest

docker-run:
	make docker-build $(COMPONENT)
	docker run -p $(PORT):$(PORT) recommender-devops-$(COMPONENT):latest

docker-push:
	docker login
	docker image tag recommender-devops-$(COMPONENT):latest $(GCR_REPO)/recommender-devops-$(COMPONENT):latest
	docker push $(GCR_REPO)/recommender-devops-$(COMPONENT):latest

docker-build-push-pipeline:
	docker build --tag $(GCR_REPO)/recommender-devops-pipeline-$(COMPONENT):v1 -f pipeline/Dockerfile . \
		&& docker push $(GCR_REPO)/recommender-devops-pipeline-$(COMPONENT):v1


# Kubernetes
minikube-start:
	minikube start
	minikube dashboard

create-namespaces:
	kubectl create namespace recommender-devops-dev
	kubectl create namespace recommender-devops-staging
	kubectl create namespace recommender-devops-prod


# Helm
helm-install:
	cd helm && \
	helm install recommender-devops-$(COMPONENT)-$(ENV) recommender-devops-$(COMPONENT) -n recommender-devops-$(ENV) -f recommender-devops-$(COMPONENT)/values-$(ENV).yaml

helm-upgrade:
	cd helm && \
	helm upgrade recommender-devops-$(COMPONENT)-$(ENV) recommender-devops-$(COMPONENT) -n recommender-devops-$(ENV) -f recommender-devops-$(COMPONENT)/values-$(ENV).yaml

helm-uninstall:
	cd helm && \
	helm uninstall recommender-devops-$(COMPONENT)-$(ENV) -n recommender-devops-$(ENV)


# Skaffold
skaffold-run:
	skaffold run -m recommender-devops-$(COMPONENT) -p $(ENV) --tail --port-forward

skaffold-dev:
	skaffold dev -m recommender-devops-$(COMPONENT) -p $(ENV) --tail --port-forward


# Kubernetes GCR Authentication
minikube-addons:
	minikube addons disable gcp-auth
	minikube addons enable gcp-auth


# MLFlow Docker
mlflow-postgres-docker-run:
	docker run --name mlflow-database \
		-v C:\Users\Grainer\Projects\recommender-devops\mlflow-db:/bitnami/postgresql \
		-e POSTGRESQL_USERNAME=admin \
		-e POSTGRESQL_PASSWORD=password \
		-e POSTGRESQL_DATABASE=mlflow-tracking-server-db \
		--expose 5432 \
		-p 5432:5432 \
		bitnami/postgresql

mlflow-docker-build:
	docker build . -f mlflow/Dockerfile -t mlflow:latest

mlflow-docker-run:
	- docker stop mlflow & docker rm mlflow
	docker run --name mlflow \
	-v C:\Users\Grainer\Projects\recommender-devops\secrets:/workdir/gcloud-credentials/ \
	-e ARTIFACT_STORE=gs://personal-mlflow-tracking/artifacts \
	-p 5000:5000 \
	--link mlflow-database \
	mlflow:latest

# MLFlow Kubernetes
mlflow-install:
	make mlflow-object-credentials-add
	make mlflow-postgres-install
	make mlflow-build
	kubectl apply -f kubernetes/mlflow-config.yaml
	kubectl apply -f kubernetes/mlflow.yaml

mlflow-object-credentials-add:
	- kubectl -n recommender-devops-$(ENV) delete secret gcsfs-creds
	kubectl -n recommender-devops-$(ENV) create secret generic gcsfs-creds --from-file=secrets/gcloud-credentials.json

mlflow-postgres-install:
	helm repo add bitnami https://charts.bitnami.com/bitnami

	- helm delete mlflow-db
	- kubectl delete pvc data-mlflow-db-postgresql-0

	helm install mlflow-db bitnami/postgresql \
		-f mlflow/postgresql-values.yaml

mlflow-build:
	docker build . -f mlflow/Dockerfile -t ${GCR_REPO}/mlflow:latest
	docker push ${GCR_REPO}/mlflow:latest


# Recommender
recommender-build:
	docker build . -f recommender/Dockerfile -t ${GCR_REPO}/recommender-engine:latest
	docker push ${GCR_REPO}/recommender-engine:latest


# Helm Prometheus
helm-prometheus-repo-add:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

helm-prometheus-install:
	helm install prometheus prometheus-community/kube-prometheus-stack -n recommender-devops-$(ENV)

grafana-port-forward:
	kubectl port-forward deployment/prometheus-grafana 3000 -n recommender-devops-$(ENV)	# admin/prom-operator

prometheus-port-forward:
	kubectl port-forward prometheus-prometheus-kube-prometheus-prometheus-0 9090 -n recommender-devops-$(ENV)


# Argo
argo-cli-install:
	curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.2.9/argo-darwin-amd64.gz
	gunzip argo-darwin-amd64.gz
	chmod +x argo-darwin-amd64
	mv ./argo-darwin-amd64 /usr/local/bin/argo
	argo version

argo-deploy-components:
	kubectl -n recommender-devops-$(ENV) apply -f pipeline/argo-component-manifest/argo-workflow.yaml

	# kubectl -n recommender-devops-$(ENV) apply -f pipeline/argo-component-manifest/argo-events.yaml
	# kubectl -n recommender-devops-$(ENV) apply -f pipeline/argo-component-manifest/event-bus.yaml
	# kubectl -n recommender-devops-$(ENV) apply -f pipeline/argo-component-manifest/event-source.yaml

	# kubectl -n recommender-devops-$(ENV) apply -f pipeline/argo-component-manifest/workflow-service-account.yaml

argo-workflow-port-forward:
	kubectl -n recommender-devops-$(ENV) port-forward deployment/argo-server 2746:2746

argo-workflow-template-deploy:
	argo template -n recommender-devops-$(ENV) lint pipeline/argo-manifest/workflow-template.yaml
	- argo template -n recommender-devops-$(ENV) delete my-workflow-template
	argo template -n recommender-devops-$(ENV) create pipeline/argo-manifest/workflow-template.yaml

argo-workflow-submit:
	argo submit -n recommender-devops-$(ENV) --from workflowtemplate/my-workflow-template

argo-events-deploy:
	kubectl -n recommender-devops-$(ENV) delete -f pipeline/argo-manifest/webhook-sensor.yaml
	kubectl -n recommender-devops-$(ENV) apply -f pipeline/argo-manifest/webhook-sensor.yaml
	make argo-events-port-forward

argo-events-port-forward:
	$(eval ARGO_WEBHOOK_POD_NAME := $(shell kubectl -n recommender-devops-$(ENV) get pod -l eventsource-name=webhook -o name))
	kubectl -n recommender-devops-$(ENV) port-forward $(ARGO_WEBHOOK_POD_NAME) 12000:12000

curl-argo-events:
	curl -d '{"message":"Hello there"}' -H "Content-Type: application/json" -X POST http://localhost:12000/deploy


# MongoDB
helm-install-mongodb:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install recommender-devops-mongo bitnami/mongodb -n recommender-devops-$(ENV)

mongodb-password:
	kubectl get secret --namespace recommender-devops-$(ENV) recommender-devops-mongo-mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 --decode

mongodb-port-forward:
	kubectl port-forward --namespace recommender-devops-$(ENV) svc/recommender-devops-mongo-mongodb 27011:27017


# Redis
helm-install-redis:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install recommender-devops-redis bitnami/redis -n recommender-devops-$(ENV)


# ElasticSearch
helm-install-elasticsearch:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install recommender-devops-elasticsearch bitnami/elasticsearch -n recommender-devops-$(ENV)

elasticsearch-port-forward:
	kubectl port-forward --namespace recommender-devops-dev svc/recommender-devops-elasticsearch-coordinating-only 9200:9200 & \
    	curl http://127.0.0.1:9200/


# Fluentd
helm-install-fluentd:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install recommender-devops-fluentd bitnami/fluentd -n recommender-devops-$(ENV)
