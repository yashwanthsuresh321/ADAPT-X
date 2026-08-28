FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y openssh-server netcat rsyslog && \
    rm -rf /var/lib/apt/lists/*

# Setup test user
RUN useradd -m -s /bin/bash testuser && \
    echo "testuser:password123" | chpasswd

# Setup SSH directory
RUN mkdir /var/run/sshd

# Configure SSH for logging
RUN echo "LogLevel VERBOSE" >> /etc/ssh/sshd_config
# Do not detach
RUN sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

CMD ["/entrypoint.sh"]
