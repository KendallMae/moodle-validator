## Part 1: Local Deployment Setup

This project uses Docker Compose to orchestrate a local Moodle application instance connected to a MariaDB database.

### Prerequisites
* Docker and Docker Compose installed on your machine.

### Installation Steps
1. Clone this repository and navigate to the root directory.
2. Spin up the environment by running:
   ```bash
   docker compose up -d
   ```
3. Allow 2–3 minutes for the database tables to initialize on the first launch.
4. Access the local Moodle instance at: **http://localhost:8080**

### Default Admin Credentials
* **Username:** `user`
* **Password:** `AdminPass123!`

### Stopping and Cleaning Up

* **Stop the environment (preserves data):**
  ```bash
  docker compose down
  ```
* **Wipe the environment completely (resets database to a clean slate):**
  ```bash
  docker compose down -v
  ```
