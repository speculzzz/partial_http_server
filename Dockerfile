FROM python:3.12-slim

RUN    apt update \
    && apt install --no-install-recommends -y \
            make procps \
    && apt clean \
    && rm -rf /var/lib/apt/lists/

WORKDIR /app

COPY server/ ./server/
COPY tests/ ./tests/
COPY pyproject.toml setup.py ./
COPY Makefile .
COPY generate_www_root.sh .

VOLUME /app/www_root

EXPOSE 8080

ENTRYPOINT ["make"]
CMD ["run_server_from_package"]
