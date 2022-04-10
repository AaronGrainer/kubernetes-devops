ENV ?= dev
COMPONENT ?= frontend

# frontend PORT=8501, backend PORT=8502
PORT ?= 8501

GCR_REPO ?= aarongrainer
MLFLOW_GS_ARTIFACT_PATH ?= gs://mlflow-tracking-storage/artifacts


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
	# flake8
	isort .


# Cleaning
.PHONY: clean
clean: style
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E "pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -f .coverage


# Test
.PHONY: test
test:
	great_expectations checkpoint run projects
	great_expectations checkpoint run tags
	pytest -m "not training"


# Local Docker
docker-build:
	docker image build -f $(COMPONENT)/Dockerfile . \
		-t evelyn-$(COMPONENT):latest

docker-run:
	make docker-build $(COMPONENT)
	docker run -p $(PORT):$(PORT) evelyn-$(COMPONENT):latest

docker-push:
	docker login
	docker image tag evelyn-$(COMPONENT):latest $(GCR_REPO)/evelyn-$(COMPONENT):latest
	docker push $(GCR_REPO)/evelyn-$(COMPONENT):latest

docker-build-push-pipeline:
	docker build --tag $(GCR_REPO)/evelyn-pipeline-$(COMPONENT):v1 -f pipeline/Dockerfile . \
		&& docker push $(GCR_REPO)/evelyn-pipeline-$(COMPONENT):v1


# Kubernetes
minikube-start:
	minikube start
	minikube dashboard

create-namespaces:
	kubectl create namespace evelyn-dev
	kubectl create namespace evelyn-staging
	kubectl create namespace evelyn-prod


# Helm
helm-install:
	cd helm && \
	helm install evelyn-$(COMPONENT)-$(ENV) evelyn-$(COMPONENT) -n evelyn-$(ENV) -f evelyn-$(COMPONENT)/values-$(ENV).yaml

helm-upgrade:
	cd helm && \
	helm upgrade evelyn-$(COMPONENT)-$(ENV) evelyn-$(COMPONENT) -n evelyn-$(ENV) -f evelyn-$(COMPONENT)/values-$(ENV).yaml

helm-uninstall:
	cd helm && \
	helm uninstall evelyn-$(COMPONENT)-$(ENV) -n evelyn-$(ENV)


# Skaffold
skaffold-run:
	skaffold run -m evelyn-$(COMPONENT) -p $(ENV) --tail --port-forward

skaffold-dev:
	skaffold dev -m evelyn-$(COMPONENT) -p $(ENV) --tail --port-forward


# MLFlow
mlflow-install:
	make mlflow-object-credentials-add
	make mlflow-postgres-install
	make mlflow-docker-build
	make mlflow-helm-deploy

mlflow-object-credentials-add:
	- kubectl -n evelyn-$(ENV) delete secret gcsfs-creds
	kubectl -n evelyn-$(ENV) create secret generic gcsfs-creds --from-file=secrets/keyfile.json

mlflow-postgres-install:
	helm repo add bitnami https://charts.bitnami.com/bitnami

	- helm delete mlf-db -n evelyn-$(ENV)
	- kubectl -n evelyn-$(ENV) delete pvc data-mlf-db-postgresql-0

	helm install mlf-db bitnami/postgresql \
		-f mlflow/postgresql-values.yaml \
		-n evelyn-$(ENV)

mlflow-docker-build:
	docker build --tag ${GCR_REPO}/mlflow-tracking-server:v1 -f mlflow/Dockerfile .
	docker push ${GCR_REPO}/mlflow-tracking-server:v1

mlflow-helm-deploy:
	helm repo add mlflow-tracking https://artefactory.github.io/mlflow-tracking-server/

	- helm delete mlflow-tracking-server -n evelyn-$(ENV)

	helm install mlflow-tracking-server mlflow-tracking/mlflow-tracking-server \
		--set env.mlflowArtifactPath=${MLFLOW_GS_ARTIFACT_PATH} \
		--set env.mlflowDBAddr=mlf-db-postgresql \
		--set env.mlflowDBName=mlflow_db \
		--set env.mlflowUser=postgres \
		--set env.mlflowPass=mlflow \
		--set env.mlflowDBPort=5432 \
		--set image.repository=${GCR_REPO}/mlflow-tracking-server \
		--set image.tag=v1 \
		-n evelyn-$(ENV) \
		# --set service.type=LoadBalancer

mlflow-port-forward:
	# kubectl get -n evelyn-$(ENV) svc -w mlflow-tracking-server
	$(eval MLFLOW_POD_NAME := $(shell kubectl get pods -n evelyn-$(ENV) -l "app.kubernetes.io/name=mlflow-tracking-server,app.kubernetes.io/instance=mlflow-tracking-server" -o jsonpath="{.items[0].metadata.name}"))
	kubectl -n evelyn-$(ENV) port-forward $(MLFLOW_POD_NAME) 8080:80


# Helm Prometheus
helm-prometheus-repo-add:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

helm-prometheus-install:
	helm install prometheus prometheus-community/kube-prometheus-stack -n evelyn-$(ENV)

grafana-port-forward:
	kubectl port-forward deployment/prometheus-grafana 3000 -n evelyn-$(ENV)	# admin/prom-operator

prometheus-port-forward:
	kubectl port-forward prometheus-prometheus-kube-prometheus-prometheus-0 9090 -n evelyn-$(ENV)


# Argo
argo-cli-install:
	curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.2.9/argo-darwin-amd64.gz
	gunzip argo-darwin-amd64.gz
	chmod +x argo-darwin-amd64
	mv ./argo-darwin-amd64 /usr/local/bin/argo
	argo version

argo-deploy-components:
	kubectl -n evelyn-$(ENV) apply -f pipeline/argo-component-manifest/argo-workflow.yaml

	# kubectl -n evelyn-$(ENV) apply -f pipeline/argo-component-manifest/argo-events.yaml
	# kubectl -n evelyn-$(ENV) apply -f pipeline/argo-component-manifest/event-bus.yaml
	# kubectl -n evelyn-$(ENV) apply -f pipeline/argo-component-manifest/event-source.yaml

	# kubectl -n evelyn-$(ENV) apply -f pipeline/argo-component-manifest/workflow-service-account.yaml

argo-workflow-port-forward:
	kubectl -n evelyn-$(ENV) port-forward deployment/argo-server 2746:2746

argo-workflow-template-deploy:
	argo template -n evelyn-$(ENV) lint pipeline/argo-manifest/workflow-template.yaml
	- argo template -n evelyn-$(ENV) delete my-workflow-template
	argo template -n evelyn-$(ENV) create pipeline/argo-manifest/workflow-template.yaml

argo-workflow-submit:
	argo submit -n evelyn-$(ENV) --from workflowtemplate/my-workflow-template

argo-events-deploy:
	kubectl -n evelyn-$(ENV) delete -f pipeline/argo-manifest/webhook-sensor.yaml
	kubectl -n evelyn-$(ENV) apply -f pipeline/argo-manifest/webhook-sensor.yaml
	make argo-events-port-foward

argo-events-port-foward:
	$(eval ARGO_WEBHOOK_POD_NAME := $(shell kubectl -n evelyn-$(ENV) get pod -l eventsource-name=webhook -o name))
	kubectl -n evelyn-$(ENV) port-forward $(ARGO_WEBHOOK_POD_NAME) 12000:12000

curl-argo-events:
	curl -d '{"message":"Hello there"}' -H "Content-Type: application/json" -X POST http://localhost:12000/deploy


# MongoDB
helm-install-mongodb:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install evelyn-mongo bitnami/mongodb -n evelyn-$(ENV)

mongodb-password:
	kubectl get secret --namespace evelyn-$(ENV) evelyn-mongo-mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 --decode

mongodb-port-forward:
	kubectl port-forward --namespace evelyn-$(ENV) svc/evelyn-mongo-mongodb 27011:27017


# Redis
helm-install-redis:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install evelyn-redis bitnami/redis -n evelyn-$(ENV)


# ElasticSearch
helm-install-elasticsearch:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install evelyn-elasticsearch bitnami/elasticsearch -n evelyn-$(ENV)

elasticsearch-port-forward:
	kubectl port-forward --namespace evelyn-dev svc/evelyn-elasticsearch-coordinating-only 9200:9200 & \
    	curl http://127.0.0.1:9200/


# Fluentd
helm-install-fluentd:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install evelyn-fluentd bitnami/fluentd -n evelyn-$(ENV)
