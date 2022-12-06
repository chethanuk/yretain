PYTHON_NIXPKG ?= python39

.PHONY: build
build:  ## Build yretain Nix package
	echo "[nix][build] Build yretain Nix package."
	@nix-build -E 'with import <nixpkgs> { overlays = [ (import ./overlay.nix) ]; }; callPackage ./default.nix {python = pkgs.${PYTHON_NIXPKG}; poetry2nix = pkgs.poetry2nix;}'

.PHONY: install
install:  ## Install yretain env with Nix
	echo "[nix][install] Install yretain env with Nix"
	@nix-build -E 'with import <nixpkgs> { overlays = [ (import ./overlay.nix) ]; }; callPackage ./editable.nix {python = pkgs.${PYTHON_NIXPKG}; poetry2nix = pkgs.poetry2nix;}'

.PHONY: image
image:  ## Build yretain image with Nix
	echo "[nix][image] Build yretain image with Nix."
	@nix-build image.nix

.PHONY: docs
docs: install  ## Build yretain documentation
	echo "[docs] Build yretain documentation."
	result/bin/sphinx-build docs site

.PHONY: metrics
metrics: install  ## Run yretain metrics checks
	echo "[nix][metrics] Run yretain PEP 8 checks."
	result/bin/flake8 --select=E,W,I --max-line-length 80 --import-order-style pep8 --statistics --count yretain
	echo "[nix][metrics] Run yretain PEP 257 checks."
	result/bin/flake8 --select=D --ignore D301 --statistics --count yretain
	echo "[nix][metrics] Run yretain pyflakes checks."
	result/bin/flake8 --select=F --statistics --count yretain
	echo "[nix][metrics] Run yretain code complexity checks."
	result/bin/flake8 --select=C901 --statistics --count yretain
	echo "[nix][metrics] Run yretain open TODO checks."
	result/bin/flake8 --select=T --statistics --count yretain tests
	echo "[nix][metrics] Run yretain black checks."
	result/bin/black -l 80 --check yretain

.PHONY: unit-test
unit-test: install  ## Run yretain unit tests
	echo "[nix][unit-test] Run yretain unit tests."
	result/bin/pytest tests/unit

.PHONY: integration-test
integration-test: install  ## Run yretain integration tests
	echo "[nix][integration-test] Run yretain unit tests."
	result/bin/pytest tests/integration

.PHONY: coverage
coverage: install  ## Run yretain tests coverage
	echo "[nix][coverage] Run yretain tests coverage."
	result/bin/pytest --cov-config=.coveragerc --cov=yretain --cov-fail-under=90 --cov-report=xml --cov-report=term-missing tests

.PHONY: test
test: unit-test integration-test  ## Run yretain tests

