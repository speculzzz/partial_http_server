# Partial HTTP Server

A minimal HTTP server with test environment.  
It is a part of Homework for the OTUS course and is intended for educational purposes.

## 🗂 Project Structure

```text
partial_http_server/
├── server/
│   ├── handle.py        # HTTP request handler
│   └── httpd.py         # Main server
├── tests/
│   └── http-test-suite/ # Test suite (submodule)
├── www_root/            # Server root directory
└── generate_www_root.sh # Test data generator script
```

# 🚀 Quick Start

1. Clone the repository with submodules:
```bash
  git clone https://github.com/speculzzz/partial_http_server.git
  cd partial_http_server
```
2. Generate server root directory:
```bash
   bash ./generate_www_root.sh
```
3. Start server:
```bash
  make run_server
```

## 🛠 Main Commands (make)

```makefile
    run_server     - Run server locally (port 8080)
    test           - Run the test suite (uses docker_up)
    docker_up      - Build and start via docker-compose (port 80)
    docker_down    - Stop container
```

## 🐳 Docker Deployment

1. Build image:
```bash
  docker-compose build
```
2. Run in background:
```bash
  docker-compose up -d
```

Server will be available at:  
http://localhost

## 🏗 Server Architecture

**Type**: Thread Pool HTTP Server  
**Model**: Fixed worker pool + queue  

### Key Components:
```text
[Main Thread] (PartialHTTPServer)
       │
       ▼
[Thread Pool] (ThreadPoolExecutor)
       │
       ▼
[Handlers] (PartialHTTPRequestHandler)
```
### Key Features:
* Main Thread - Accepts connections (non-blocking)
* Thread Pool - Processes requests (configurable size)
* Handlers - Synchronous request handling

### Load Testing Results (ab -n 50000 -c 100 -r http://localhost/httptest/wikipedia_russia.html):
| Parameter               | 260 Workers | 600 Workers (updated) |
|-------------------------|-------------|-----------------------|
| Requests per second     | 2,863.32    | 866.64                |
| Average latency         | 34.92 ms    | 115.39 ms             |
| 95th percentile         | 6 ms        | 6 ms                  |
| 99th percentile         | 1,046 ms    | 1,031 ms              |
| Data transferred        | 47.7 GB     | 47.7 GB               |
| Max latency             | 8,044 ms    | 57,691 ms             |

### Performance Analysis:
```text
1. Peak performance: 2,863 RPS (260 workers)
2. 99% of requests complete under 1.1s
3. Throughput drops 70% at 600 workers
4. Consistent 95th percentile latency (6ms)
```

### Key Observations:
```text
1. Sweet spot: 200-300 workers
2. Critical threshold: Performance degrades after 300 workers
3. Stability: 99% of requests remain under 1.1s even at 600 workers
```

## 🧪 Testing

To run the test suite:

```bash
  make test
```

## 📋 Requirements

- Python 3.11+
- Docker (for container deployment)
- Git (for submodules)

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

## 👨 Author

- **speculzzz** (speculzzz@gmail.com)

---

Feel free to use it!
