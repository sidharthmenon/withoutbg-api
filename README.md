# withoutbg Backend API

FastAPI-based REST API for AI-powered background removal. (API Version)

For more details: https://github.com/withoutbg/withoutbg

## docker compose
```
  version: "3.9"
  
  services:
    withoutbg-api:
      image: ghcr.io/sidharthmenon/withoutbg-api:latest
      container_name: withoutbg-api
      restart: always
  
      ports:
        - "${PORT}:8000"  # Expose internal port 8000 to host
  
      environment:
        # You may override or define extra environment variables here
        PYTHONUNBUFFERED: "${PYTHONUNBUFFERED}"
        API_TOKENS: "${API_TOKEN}"  # For multi-token authentication
        PORT: "${PORT}"
```

## License

Apache 2.0 - See parent LICENSE file
