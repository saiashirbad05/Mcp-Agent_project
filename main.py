import json
import os
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent
from weather_service import fetch_weather_by_city

APP_NAME = "mcp_weather_service"
USER_ID = "public_api_user"

app = FastAPI(
    title="mcp-agent",
    version="1.0.0",
    description="MCP-powered weather agent built with Google ADK and FastAPI.",
)

session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


class WeatherRequest(BaseModel):
    city: str = Field(..., min_length=1, description="City name, for example Delhi")


class WeatherResponse(BaseModel):
    city: str
    weather_data: dict[str, Any] | None
    answer: str
    status: str


def extract_json_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    return cleaned


async def run_agent(city: str) -> dict[str, Any]:
    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    prompt = (
        f"Input JSON: {json.dumps({'city': city}, ensure_ascii=True)}\n"
        "Use the get_weather MCP tool exactly once.\n"
        "Return only valid JSON with keys city, weather_data, answer, status.\n"
        "Do not add markdown."
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text and part.text.strip():
                    final_text = part.text.strip()

    if not final_text:
        raise RuntimeError("The ADK agent returned no final response.")

    payload = json.loads(extract_json_text(final_text))
    if not isinstance(payload, dict):
        raise ValueError("The ADK agent returned JSON, but it was not a JSON object.")

    return payload


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "mcp-agent"}


@app.post("/weather", response_model=WeatherResponse)
async def weather(request: WeatherRequest) -> WeatherResponse:
    city = request.city.strip()
    if not city:
        raise HTTPException(status_code=400, detail="The 'city' field must not be empty.")

    try:
        payload = await run_agent(city)
    except json.JSONDecodeError:
        try:
            fallback_weather = await fetch_weather_by_city(city)
            return WeatherResponse(
                city=city,
                weather_data=fallback_weather,
                answer="The ADK agent returned malformed JSON. Check Cloud Run logs and troubleshooting steps.",
                status="error",
            )
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Agent returned malformed JSON and fallback lookup failed: {fallback_error}",
            )
    except Exception as agent_error:
        try:
            fallback_weather = await fetch_weather_by_city(city)
            return WeatherResponse(
                city=city,
                weather_data=fallback_weather,
                answer=f"Agent execution failed, but direct weather retrieval worked: {agent_error}",
                status="error",
            )
        except Exception:
            raise HTTPException(status_code=500, detail=f"Agent execution failed: {agent_error}")

    payload["city"] = str(payload.get("city") or city)
    payload["weather_data"] = payload.get("weather_data")
    payload["answer"] = str(payload.get("answer") or "Weather lookup completed.")
    payload["status"] = str(payload.get("status") or "success")

    if payload["status"] not in {"success", "error"}:
        payload["status"] = "success" if payload["weather_data"] else "error"

    return WeatherResponse(**payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
    )
