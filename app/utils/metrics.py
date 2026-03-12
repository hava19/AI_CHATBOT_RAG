from prometheus_client import Counter, Histogram
import time

request_count = Counter("http_requests_total", "Total HTTP requests")
request_duration = Histogram("http_request_duration_seconds", "HTTP request duration")
llm_calls = Counter("llm_calls_total", "Total LLM API calls")
token_usage = Counter("llm_tokens_total", "Total tokens used")
