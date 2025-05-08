FROM gcc:latest

# Install required packages
RUN apt-get update && apt-get install -y \
    time \
    timeout \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /judge

# Add a non-root user for running judging
RUN useradd -m -d /judge -s /bin/bash judge \
    && chown -R judge:judge /judge

# Switch to the judge user
USER judge

# Entry point that will be used for compilation or execution
ENTRYPOINT ["/bin/bash", "-c"]
