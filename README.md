Distributed Online Auction Platform

This repository implements a distributed online auction platform using two contrasting system architectures:

Go-based microservices with a lightweight gRPC-inspired communication layer (go-architecture)

Python layered architecture communicating over HTTP (python_architecture)

Both architectures satisfy the functional requirements of creating auctions, bidding, broadcasting updates, closing auctions, and viewing history across at least five containerized nodes. A simple web GUI is provided in the Python stack.

🚀 Prerequisites

Docker
 and Docker Compose

(Optional) Go 1.21+
 and Python 3.11+
 for running services directly during development

🟦 Running the Go Microservice Architecture
cd go-architecture
# build and start all six services
docker compose up --build


The gateway listens on localhost:7000. Example interaction:

curl -X POST http://localhost:7000/auction.AuctionGateway/Execute \
  -H 'Content-Type: application/json' \
  -d '{"command":"create","auction":{"name":"Laptop","description":"Lightly used","starting_bid":50,"duration_seconds":120}}'


Use the same endpoint with different command payloads (place_bid, close, list) to exercise the API.

🐍 Running the Python Layered Architecture with GUI
cd python_architecture
# launch five HTTP services (frontend, gateway, auction, bidding, history)
docker compose up --build


Only the gateway (8000) and frontend (8080) publish host ports, so the supporting services do not conflict with local apps using ports 8001-8003.

Open http://localhost:8080
 to access the dashboard.

The GUI allows you to:

Create auctions

Queue multiple bids for a single auction

Close auctions manually

Review historical activity

The interface consumes a server-sent events (SSE) stream for real-time updates. New bids, closures, and history entries appear instantly without manual refresh or polling. Auction durations default to 60 seconds and automatically expire with a "Bid time ended" status.

📊 Benchmarking Throughput and Latency

After either architecture is running, execute the lightweight benchmark script to gather baseline latency and throughput metrics:

# replace BASE_URL with http://localhost:7000 for Go or http://localhost:8080 for Python
python evaluation/benchmark.py http://localhost:8080


💡 Tip: You can also export an environment variable (e.g. export BASE_URL=http://localhost:8080) and run:

python evaluation/benchmark.py $BASE_URL


The script performs a series of create → bid → close operations and reports the average latency and achieved throughput.

🤖 Leveraging AI Tools

This implementation was produced with the assistance of AI coding tools.
Comments and documentation capture design decisions and trade-offs between the two architectural styles.
