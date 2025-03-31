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
| Parameter               | 260 Workers         | 600 Workers         | Delta    |
|-------------------------|---------------------|---------------------|----------|
| **Requests per second** | 963.46 RPS         | 1021.18 RPS        | ▲ +6%    |
| **Avg latency**         | 103.79 ms          | 97.93 ms           | ▼ -5.6%  |
| **Max latency**         | 7434 ms            | 29872 ms           | ▲ +302%  |
| **95th percentile**     | 1035 ms            | 1030 ms            | ▼ -0.5%  |
| **99th percentile**     | 2045 ms            | 1524 ms            | ▼ -25.5% |
| **Data transferred**    | 47.7 GB            | 47.7 GB            | =        |
| **Transfer rate**       | 898.5 MB/s         | 952.4 MB/s         | ▲ +6%    |

### Key Observations:
```text
1. **Increased productivity** by 6% with 600 workers
2. **99th percentile improvement** by 25% (2045ms → 1524ms)
3. **A sharp increase in the maximum delay** (7.4 → 29.9s) indicates:
   - Periodic blockages under high load
   - Competition for resources
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
