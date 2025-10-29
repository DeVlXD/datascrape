# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    gpg \
    unzip \
    curl \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub

# Install ChromeDriver that matches Chrome version
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') \
    && echo "Installed Chrome version: $CHROME_VERSION" \
    && CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d '.' -f 1) \
    && echo "Looking for ChromeDriver version matching Chrome $CHROME_MAJOR..." \
    && CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
       jq -r ".channels.Stable.version") \
    && echo "Found ChromeDriver version: $CHROMEDRIVER_VERSION" \
    && CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    && echo "Downloading from: $CHROMEDRIVER_URL" \
    && wget -q "$CHROMEDRIVER_URL" -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 \
    && echo "ChromeDriver installed successfully:" \
    && chromedriver --version

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p downloads

# Expose port
EXPOSE 8080

# Run the application with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 600 --workers 1 app:app
