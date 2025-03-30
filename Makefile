ROOT_DIR := www_root
HTTP_WORKERS := 260

TEST_CHECKING_URL := http://localhost/httptest/wikipedia_russia.html
TEST_SUITE_DIR := tests/http-test-suite/httptest
TEST_SCRIPT := ${TEST_SUITE_DIR}.py

TIMEOUT := 30
SLEEP_INTERVAL := 2

all: run_server

.PHONY: prepare_www_root
prepare_www_root:
	@if [ ! -e "${ROOT_DIR}/index.html" ]; then \
		echo "Generating ${ROOT_DIR}..."; \
		bash ./generate_${ROOT_DIR}.sh; \
	fi
	@if [ ! -d "${ROOT_DIR}/httptest" ] && [ -d "${TEST_SUITE_DIR}" ]; then \
		echo "Copy test suite..."; \
		cp -r ${TEST_SUITE_DIR} ${ROOT_DIR}; \
	fi

.PHONY: run_server
run_server: prepare_www_root
	@echo "Starting HTTP server..."
	@python3 main.py -r ./www_root -w ${HTTP_WORKERS}

.PHONY: run_server_from_package
run_server_from_package: prepare_www_root
	@echo "Install HTTP server package..."
	@pip install --no-cache-dir -e .
	@echo "Starting HTTP server..."
	@httpd -r ./www_root -w ${HTTP_WORKERS}

.PHONY: docker_up
docker_up:
	docker-compose up --build -d

.PHONY: docker_down
docker_down:
	docker-compose down

.PHONY: test
test: check_server_available
	@echo "Running test suite..."
	@python3 ${TEST_SCRIPT}
# 	@make docker_down

.PHONY: check_server_available
check_server_available:
	@echo "Checking server availability..."
	@if ! curl -sSf ${TEST_CHECKING_URL} > /dev/null 2>&1 ; then \
		echo "Server not running, starting docker..."; \
		make docker_up; \
		make wait_for_server; \
	fi

.PHONY: wait_for_server
wait_for_server:
	@echo "Waiting for server to become available (max ${TIMEOUT}s)..."
	@timeout=${TIMEOUT}; \
	while ! curl -sSf ${TEST_CHECKING_URL} > /dev/null 2>&1 ; do \
		if [ $$timeout -le 0 ]; then \
			echo "Timeout: Server did not start in ${TIMEOUT}s"; \
			exit 1; \
		fi; \
		sleep ${SLEEP_INTERVAL}; \
		timeout=$$((timeout-$(SLEEP_INTERVAL))); \
	done; \
	echo "Server is ready"
