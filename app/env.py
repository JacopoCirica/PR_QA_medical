import os

from dotenv import load_dotenv

# Make logfire optional
try:
    import logfire

    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    print("ℹ️  Logfire not installed. Observability features disabled.")


def setup_env():
    load_dotenv()

    if LOGFIRE_AVAILABLE and (logfire_token := os.getenv("LOGFIRE_KEY")):
        logfire.configure(token=logfire_token)
        # Note: asyncpg instrumentation not needed for this project
        # logfire.instrument_asyncpg()


def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")
