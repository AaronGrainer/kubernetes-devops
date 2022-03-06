ENV ?= dev
COMPONENT ?= frontend

# frontend PORT=8501, backend PORT=8502
PORT ?= 8501


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
	flake8
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
	docker image tag evelyn-$(COMPONENT):latest aarongrainer/evelyn-$(COMPONENT):latest
	docker push aarongrainer/evelyn-$(COMPONENT):latest


# Kubernetes
minikube-start:
	minikube start
	minikube dashboard

create-namespaces:
	kubectl create namespace evelyn-dev
	kubectl create namespace evelyn-staging
	kubectl create namespace evelyn-prod

kubectl-deploy:
	kubectl delete -f kubernetes-manifest/$(COMPONENT).yaml
	kubectl apply -f kubernetes-manifest/$(COMPONENT).yaml

kubectl-rollout:
	docker image build -f $(COMPONENT)/Dockerfile . \
		-t evelyn-$(COMPONENT):latest

	docker image tag evelyn-$(COMPONENT):latest aarongrainer/evelyn-$(COMPONENT):latest
	docker push aarongrainer/evelyn-$(COMPONENT):latest

	kubectl rollout restart deployment/evelyn-$(COMPONENT)


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


# Support deployments
helm-install-mongodb:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install evelyn bitnami/mongodb -n evelyn-$(ENV)

mongodb-password:
	kubectl get secret --namespace evelyn-$(ENV) evelyn-mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 --decode

mongodb-port-forward:
	kubectl port-forward --namespace evelyn-$(ENV) svc/evelyn-mongodb 27011:27017
