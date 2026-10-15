import json
import logging
import os
from typing import Any

import psycopg


logger = logging.getLogger(__name__)


INSERT_QUERY = """
INSERT INTO chat_analytics (query, retrieved_chunks, answer)
VALUES (%s, %s::jsonb, %s)
"""


def record_query(
    query: str,
    retrieved_chunks: list[dict[str, Any]],
    answer: str,
    database_url: str | None = None,
) -> None:
    database_url = database_url or os.getenv("DATABASE_URL")
    if not database_url:
        return

    try:
        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_QUERY,
                    (query, json.dumps(retrieved_chunks, default=str), answer),
                )
    except Exception:
        logger.exception("Could not record chat analytics")
