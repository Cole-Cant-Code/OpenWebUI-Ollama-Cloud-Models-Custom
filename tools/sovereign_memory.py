"""
title: Sovereign Memory
author: Cole
author_url: https://github.com/Cole-Cant-Code
description: Persistent memory across sessions. Store and recall user preferences, context, and insights.
required_open_webui_version: 0.4.0
requirements: aiosqlite
version: 1.0.0
licence: MIT
"""

import aiosqlite
import os
from datetime import datetime
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        db_path: str = Field(
            default="/app/backend/data/sovereign_memory.db",
            description="Path to the memory database file",
        )
        max_memories_per_user: int = Field(
            default=200,
            ge=10,
            le=1000,
            description="Maximum memories stored per user before oldest are pruned",
        )

    def __init__(self):
        self.valves = self.Valves()
        self._initialized = False

    async def _ensure_db(self):
        if self._initialized:
            return
        os.makedirs(os.path.dirname(self.valves.db_path), exist_ok=True)
        async with aiosqlite.connect(self.valves.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mem_user_topic
                ON memories(user_id, topic)
                """
            )
            await db.commit()
        self._initialized = True

    async def _prune(self, db, user_id: str):
        count = await db.execute_fetchall(
            "SELECT COUNT(*) FROM memories WHERE user_id = ?", (user_id,)
        )
        if count[0][0] > self.valves.max_memories_per_user:
            await db.execute(
                """
                DELETE FROM memories WHERE id IN (
                    SELECT id FROM memories WHERE user_id = ?
                    ORDER BY updated_at ASC
                    LIMIT ?
                )
                """,
                (user_id, count[0][0] - self.valves.max_memories_per_user),
            )

    async def remember(
        self,
        topic: str,
        content: str,
        __user__: dict = None,
        __event_emitter__=None,
    ) -> str:
        """
        Store a persistent memory. Use this to save user preferences, important context, project details, or decisions that should be available in future conversations. If a memory with the same topic exists, it is updated.
        :param topic: Short label for this memory (e.g., "preferred_language", "project_stack", "communication_style").
        :param content: The information to remember. Be specific and concise.
        :return: Confirmation of what was stored.
        """
        await self._ensure_db()
        user_id = __user__["id"] if __user__ else "anonymous"
        now = datetime.now().isoformat()

        async with aiosqlite.connect(self.valves.db_path) as db:
            existing = await db.execute(
                "SELECT id FROM memories WHERE user_id = ? AND topic = ?",
                (user_id, topic),
            )
            row = await existing.fetchone()

            if row:
                await db.execute(
                    "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
                    (content, now, row[0]),
                )
                action = "Updated"
            else:
                await db.execute(
                    "INSERT INTO memories (user_id, topic, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, topic, content, now, now),
                )
                action = "Stored"

            await self._prune(db, user_id)
            await db.commit()

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Memory {action.lower()}: {topic}",
                        "done": True,
                    },
                }
            )

        return f"{action} memory **[{topic}]**: {content[:200]}{'...' if len(content) > 200 else ''}"

    async def recall(
        self, query: str, __user__: dict = None, __event_emitter__=None
    ) -> str:
        """
        Search stored memories. Use this at the start of conversations to load user context, or anytime you need to retrieve previously stored information. Use "*" to list all memories.
        :param query: Search term to match against memory topics and content. Use "*" for all.
        :return: Matching memories with topics, content, and timestamps.
        """
        await self._ensure_db()
        user_id = __user__["id"] if __user__ else "anonymous"

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Searching memories...", "done": False},
                }
            )

        async with aiosqlite.connect(self.valves.db_path) as db:
            if query.strip() == "*":
                cursor = await db.execute(
                    "SELECT topic, content, updated_at FROM memories WHERE user_id = ? ORDER BY updated_at DESC",
                    (user_id,),
                )
            else:
                cursor = await db.execute(
                    "SELECT topic, content, updated_at FROM memories WHERE user_id = ? AND (topic LIKE ? OR content LIKE ?) ORDER BY updated_at DESC",
                    (user_id, f"%{query}%", f"%{query}%"),
                )
            rows = await cursor.fetchall()

        if not rows:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "No memories found", "done": True},
                    }
                )
            return "No memories found."

        result = f"**{len(rows)} memory(ies):**\n\n"
        for topic, content, updated_at in rows:
            result += f"- **[{topic}]** _{updated_at[:10]}_\n  {content}\n\n"

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Found {len(rows)} memories",
                        "done": True,
                    },
                }
            )

        return result.strip()

    async def forget(
        self, topic: str, __user__: dict = None, __event_emitter__=None
    ) -> str:
        """
        Delete a stored memory by its exact topic. Use when information is outdated or the user explicitly asks to forget something.
        :param topic: The exact topic label of the memory to delete.
        :return: Confirmation of deletion.
        """
        await self._ensure_db()
        user_id = __user__["id"] if __user__ else "anonymous"

        async with aiosqlite.connect(self.valves.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM memories WHERE user_id = ? AND topic = ?",
                (user_id, topic),
            )
            await db.commit()
            deleted = cursor.rowcount

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"{'Deleted' if deleted else 'Not found'}: {topic}",
                        "done": True,
                    },
                }
            )

        return f"Forgotten: **[{topic}]**" if deleted else f"No memory found with topic **[{topic}]**."
