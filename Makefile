ROOT_DIR := www_root
TEST_SUITE_DIR := tests/http-test-suite/httptest
HTTP_WORKERS := 260

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
