FROM python:3.12-slim

WORKDIR /app
COPY scoreboard ./scoreboard
COPY static ./static
USER 65534:65534
EXPOSE 8080
CMD ["python", "-m", "scoreboard"]
