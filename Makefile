ROOT_DIR := "www_root"

all: run_server

.PHONY: prepare_www_root
prepare_www_root:
	@if [ ! -d "$ROOT_DIR" ] || [ -z "$(find "$ROOT_DIR" -maxdepth 0 -empty)" ]; then \
		echo "Generating ${ROOT_DIR}..."; \
		bash ./generate_${ROOT_DIR}.sh; \
	fi

.PHONY: run_server
run_server: prepare_www_root
	@echo "Starting HTTP server..."
	@python3 main.py -r ./www_root

.PHONY: run_server_from_package
run_server_from_package: prepare_www_root
	@echo "Install HTTP server package..."
	@pip install --no-cache-dir -e .
	@echo "Starting HTTP server..."
	@httpd -r ./www_root

.PHONY: docker_up
docker_up:
	docker-compose up --build -d

.PHONY: docker_down
docker_down:
	docker-compose down
