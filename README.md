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
3. The first launch takes **3–5 minutes** while Moodle installs and configures the database. Subsequent starts are much faster thanks to persistent volumes.
4. Monitor progress with:
   ```bash
   docker compose logs -f moodle
   ```
   You'll know it's ready when you see `moodle 08:...:.. INFO  ==> ** Moodle setup finished! **` in the logs.
5. You can also check container health status:
   ```bash
   docker compose ps
   ```
   Wait until the `moodle` service shows `healthy` in the STATUS column.
6. Access the local Moodle instance at: **http://localhost:8080**

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
