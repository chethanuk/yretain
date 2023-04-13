POETRY_HOME ?= ${HOME}/.local/share/pypoetry
POETRY_BINARY ?= ${POETRY_HOME}/venv/bin/poetry
POETRY_VERSION ?= 1.4.0

.PHONY: build
build: ## Build yretain package
	echo "[build] Build yretain package."
	${POETRY_BINARY} build

.PHONY: install
install:  ## Install yretain with poetry
	@build/install.sh

.PHONY: image
image:  ## Build yretain image
	@build/image.sh

.PHONY: metrics
metrics: install ## Run yretain metrics checks
	echo "[metrics] Run yretain PEP 8 checks."
	${POETRY_BINARY} run flake8 --select=E,W,I --max-line-length 80 --import-order-style pep8 --statistics --count yretain
	echo "[metrics] Run yretain PEP 257 checks."
	${POETRY_BINARY} run flake8 --select=D --ignore D301 --statistics --count yretain
	echo "[metrics] Run yretain pyflakes checks."
	${POETRY_BINARY} run flake8 --select=F --statistics --count yretain
	echo "[metrics] Run yretain code complexity checks."
	${POETRY_BINARY} run flake8 --select=C901 --statistics --count yretain
	echo "[metrics] Run yretain open TODO checks."
	${POETRY_BINARY} run flake8 --select=T --statistics --count yretain tests
	echo "[metrics] Run yretain black checks."
	${POETRY_BINARY} run black -l 80 --check yretain

.PHONY: unit-test
unit-test: install ## Run yretain unit tests
	echo "[unit-test] Run yretain unit tests."
	${POETRY_BINARY} run pytest tests/unit

.PHONY: integration-test
integration-test: install ## Run yretain integration tests
	echo "[unit-test] Run yretain integration tests."
	${POETRY_BINARY} run pytest tests/integration

.PHONY: coverage
coverage: install  ## Run yretain tests coverage
	echo "[coverage] Run yretain tests coverage."
	${POETRY_BINARY} run pytest --cov-config=.coveragerc --cov=yretain --cov-fail-under=90 --cov-report=xml --cov-report=term-missing tests

.PHONY: test
test: unit-test integration-test  ## Run yretain tests

.PHONY: docs
docs: install ## Build yretain documentation
	echo "[docs] Build yretain documentation."
	${POETRY_BINARY} run sphinx-build docs site

.PHONY: dev-env
dev-env: image ## Start a local Kubernetes cluster using minikube and deploy application
	@build/dev-env.sh

.PHONY: clean
clean: ## Remove .cache directory and cached minikube
	minikube delete && rm -rf ~/.cache ~/.minikube

