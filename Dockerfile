FROM python:3.14-bookworm

# Set working directory
WORKDIR /app

# Copy the entire project into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p /output/sim_output

# Make the bash script executable
RUN chmod +x /app/execute_experiments.sh

# Keep the container running
CMD ["tail", "-f", "/dev/null"]
