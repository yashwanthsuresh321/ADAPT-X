#!/bin/bash

# Start SSH daemon in the foreground, logging to stderr so Docker captures it
exec /usr/sbin/sshd -D -e
