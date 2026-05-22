FROM alpine:3.20 AS builder

WORKDIR /app
RUN addgroup -S appuser && adduser -S appuser -G appuser && chown -R appuser:appuser /app

RUN apk add --no-cache curl
COPY --chown=appuser:appuser init.sh /app
USER appuser

CMD ["sh", "/app/init.sh"]
