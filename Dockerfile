FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV CLIENT_ID=""
ENV CLIENT_SECRET=""
ENV MERCHANT_ID=""

# Expose the port the app runs on
EXPOSE 8888

# Command to run the application with SSE transport
CMD ["sh", "-c", "python server.py --sse --port ${PORT:-8888}"]
