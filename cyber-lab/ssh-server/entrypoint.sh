#!/bin/bash

# Start rsyslog for auth logging
service rsyslog start

# Start SSH daemon in the foreground, logging to stderr so Docker captures it
exec /usr/sbin/sshd -D -e
