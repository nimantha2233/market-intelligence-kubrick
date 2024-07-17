FROM selenium/standalone-chrome:latest as build

USER root

# Install additional dependencies if needed
RUN sudo apt-get update && sudo apt-get install -y python3-pip xvfb && sudo apt-get upgrade -y unzip

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99  
# Set DISPLAY to :99 for Xvfb

# Set up Xvfb
RUN Xvfb :99 -ac &

# Set working directory and copy files
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean

# Define the command to run your application
CMD xvfb-run --server-args="-screen 0 1900x1200x24" python3 main.py