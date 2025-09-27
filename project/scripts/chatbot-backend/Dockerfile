# --- STAGE 1: The Builder ---
FROM node:20-slim as builder
RUN npm install -g mcp-remote

# --- STAGE 2: The Final Application ---
FROM python:3.10-slim

# --- FIX ---
# Add the Node.js binary directory to the system's PATH
ENV PATH="/usr/local/bin:${PATH}"

# Copy the necessary files from the builder stage
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/node_modules /usr/local/lib/node_modules

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install Python dependencies
COPY ./chatbot-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY ./src ./src
COPY ./chatbot-backend/ ./

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
