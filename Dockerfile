# Use the image available for timeloop and accelergy
FROM mitdlh/timeloop-accelergy-pytorch:latest

# Find and set ACCELERGYPATH as a env path
RUN accel=$(dirname $(find /usr/local/lib -name accelergy)) && cd .. && echo "export PYTHONPATH=$accel" >> /etc/bash.bashrc