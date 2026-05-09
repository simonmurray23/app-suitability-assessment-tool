import json
import os
import boto3
import anthropic

ssm = boto3.client("ssm")
s3 = boto3.client("s3")

_api_key: str | None = None
_skill_prompt: str | None = None


def _get_api_key() -> str:
    global _api_key
    if _api_key is None:
        response = ssm.get_parameter(
            Name=os.environ["SSM_PARAM_NAME"],
            WithDecryption=True,
        )
        _api_key = response["Parameter"]["Value"]
    return _api_key


def _get_skill_prompt() -> str:
    """Read SKILL.md from S3 on first invocation; cached for the lifetime of the container."""
    global _skill_prompt
    if _skill_prompt is None:
        response = s3.get_object(
            Bucket=os.environ["PROMPTS_BUCKET"],
            Key="SKILL.md",
        )
        _skill_prompt = response["Body"].read().decode("utf-8")
    return _skill_prompt


def handler(event: dict, context) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
        app_name = body.get("app_name", "").strip()
        if not app_name:
            return _response(400, {"error": "app_name is required"})

        client = anthropic.Anthropic(api_key=_get_api_key())
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=_get_skill_prompt(),
            messages=[{"role": "user", "content": f"Please assess this app: {app_name}"}],
        )
        reply = message.content[0].text
        return _response(200, {"reply": reply})

    except Exception as exc:
        print(f"ERROR: {exc}")
        return _response(500, {"error": "Internal server error"})


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
