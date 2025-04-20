# Builder stage
FROM apache/airflow:2.6.0 AS builder

# Switch to root for system package installation
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential

# Switch back to airflow user for Rust/Python installations
USER airflow

# Install Rust toolchain in airflow user's home
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/home/airflow/.cargo/bin:${PATH}"

WORKDIR /opt/airflow
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM apache/airflow:2.6.0

# Copy installed components from builder
USER airflow
COPY --from=builder /home/airflow/.local /home/airflow/.local
COPY --from=builder /home/airflow/.cargo /home/airflow/.cargo

# Set environment variables
ENV PATH="/home/airflow/.local/bin:/home/airflow/.cargo/bin:${PATH}"

WORKDIR /opt/airflow
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins

EXPOSE 8080
CMD ["airflow", "webserver"]
