# Mcp-Agent-Project

`mcp-agent-project` is a beginner-friendly but production-shaped weather agent built with Google ADK, MCP, FastAPI, Docker, Artifact Registry, and Cloud Run.

It accepts a city in JSON, retrieves structured weather data through an MCP tool backed by Open-Meteo, and returns a structured JSON response with both raw weather data and a natural-language answer.

## Live Deployment

- Cloud Run base URL: EX-- [https://mcp-agent-60096438952.us-central1.run.app](https://mcp-agent-60096438952.us-central1.run.app)
- Health endpoint: `GET /health`
- Main endpoint: `POST /weather`

## Features

- Google ADK agent orchestration
- MCP-based external tool integration
- FastAPI HTTP API
- Structured JSON responses
- Cloud Run deployment-ready
- Cloud Shell-only workflow
- Error-aware fallback behavior

## Request Example

```json
{
  "city": "Delhi"
}
```

## Response Example

```json
{
  "city": "Delhi",
  "weather_data": {
    "resolved_city": "Delhi",
    "country": "India",
    "admin1": "Delhi",
    "latitude": 28.65195,
    "longitude": 77.23149,
    "timezone": "Asia/Kolkata",
    "observation_time": "2026-03-23T23:30",
    "temperature_c": 20.1,
    "apparent_temperature_c": 21.7,
    "relative_humidity_pct": 84,
    "wind_speed_kmh": 6.4,
    "wind_direction_degrees": 106,
    "cloud_cover_pct": 46,
    "precipitation_mm": 0.0,
    "is_day": false,
    "weather_code": 2,
    "weather_description": "Partly cloudy",
    "source": "Open-Meteo"
  },
  "answer": "Delhi is partly cloudy right now with warm conditions and light wind.",
  "status": "success"
}
```

## Project Structure

```text
mcp-agent-project/
|-- README.md
|-- requirements.txt
|-- weather_service.py
|-- weather_mcp_server.py
|-- agent.py
|-- main.py
|-- Dockerfile
|-- .dockerignore
|-- .gitignore
|-- MCP_WEATHER_AGENT_GUIDE.txt
`-- service_sab.txt
```

## Core Design

1. FastAPI receives a request on `/weather`
2. Google ADK runs the `mcp_agent`
3. ADK calls an MCP tool named `get_weather`
4. The MCP server calls Open-Meteo
5. The final response returns JSON

## Important Notes

- Public service name should stay `mcp-agent`
- Internal ADK agent name must be `mcp_agent`
- Recommended model is `gemini-2.5-flash`
- The project is designed to be created in Cloud Shell, not on a local PC

## Quick Test

```bash
SERVICE_URL="https://mcp-agent-60096438952.us-central1.run.app"

curl -X POST "${SERVICE_URL}/weather" \
  -H "Content-Type: application/json" \
  -d '{"city":"Delhi"}' | python3 -m json.tool
```

## Pretty Summary Test

```bash
SERVICE_URL="https://mcp-agent-60096438952.us-central1.run.app"

curl -s -X POST "${SERVICE_URL}/weather" \
  -H "Content-Type: application/json" \
  -d '{"city":"Delhi"}' | python3 -c '
import json,sys
data=json.load(sys.stdin)
print("=" * 52)
print("MCP WEATHER AGENT STATUS")
print("=" * 52)
print(f"City        : {data.get(\"city\")}")
print(f"Status      : {data.get(\"status\")}")
print(f"Answer      : {data.get(\"answer\")}")
weather=data.get("weather_data") or {}
if weather:
    print("-" * 52)
    print("WEATHER SUMMARY")
    print("-" * 52)
    print(f"Resolved    : {weather.get(\"resolved_city\")}, {weather.get(\"country\")}")
    print(f"Condition   : {weather.get(\"weather_description\")}")
    print(f"Temperature : {weather.get(\"temperature_c\")} C")
    print(f"Feels Like  : {weather.get(\"apparent_temperature_c\")} C")
    print(f"Humidity    : {weather.get(\"relative_humidity_pct\")} %")
    print(f"Wind Speed  : {weather.get(\"wind_speed_kmh\")} km/h")
    print(f"Cloud Cover : {weather.get(\"cloud_cover_pct\")} %")
    print(f"Observed At : {weather.get(\"observation_time\")}")
    print(f"Source      : {weather.get(\"source\")}")
print("=" * 52)
'
```

## Deployment Stack

- Python 3.10+
- Google ADK
- MCP
- FastAPI
- Docker
- Artifact Registry
- Cloud Run

## Setup and Deployment Guide

Full step-by-step instructions are included in `MCP_WEATHER_AGENT_GUIDE.txt`.
