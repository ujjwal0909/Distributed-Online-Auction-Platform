FROM python:3.11-slim
ARG SERVICE
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app
CMD ["python", "-m", "python_architecture.services.${SERVICE}.server"]
