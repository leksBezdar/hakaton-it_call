# Service for hakaton named "It-call"

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## Features

- Authorization with otp
- Sending reminder emails

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL, redis
- **Message broker:** Aiokafka
- **Containerization:** Docker, Docker Compose

## Architecture

This project is organized following a simplified Domain-Driven Design (DDD) approach.

## Getting Started

### Prerequisites

Ensure you have the following installed on your local machine:

- Docker
- Docker Compose
- GNU Make

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/leksbezdar/hakation-it_call.git
    cd hakation-it_call
    ```

2. Create a `.env` file in the project root directory and add your environment variables. You can use the `.env.example` as a reference.

    ```sh
    cp .env.example .env
    ```

### Running the Project

1. Build and start the Docker containers:

    ```sh
    make all
    ```

2. The application will be available at `http://0.0.0.0:8000`.
3. You can use this command to up only storages
    ```sh
    make storages
    ```
4. You can migrate database
  ```sh
  make upgrade
  ```
5. You can create new migrations
   ```sh
   make revision name="Your migration name"
   ```
6. You can use this command to down an application
    ```sh
    make app-down
    ```

Other commands are available for viewing in Makefile

## API Documentation

The API documentation is automatically generated by OpenAPI and is available at `http://0.0.0.0:8000/docs`.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

Feel free to explore and modify the project as needed for your own purposes!
