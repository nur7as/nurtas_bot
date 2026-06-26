import sqlite3
from datetime import datetime


class Database:
    def __init__(self, path: str = "nurtas_bot.db"):
        self.path = path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _init(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id    INTEGER PRIMARY KEY,
                    full_name  TEXT,
                    username   TEXT,
                    added_at   TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending (
                    user_id    INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER NOT NULL,
                    event      TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    # ── Subscribers ──────────────────────────────────────────────────────────
    def is_subscriber(self, user_id: int) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM subscribers WHERE user_id = ?", (user_id,)
            ).fetchone()
        return row is not None

    def add_subscriber(self, user_id: int, full_name: str, username: str):
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO subscribers (user_id, full_name, username, added_at)
                   VALUES (?, ?, ?, ?)""",
                (user_id, full_name, username, datetime.now().strftime("%d.%m.%Y %H:%M"))
            )

    def get_all_subscribers(self) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT user_id, full_name, username, added_at FROM subscribers ORDER BY added_at DESC"
            ).fetchall()
        return [{"user_id": r[0], "full_name": r[1], "username": r[2], "added_at": r[3]} for r in rows]

    def get_count(self) -> int:
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]

    # ── Pending ───────────────────────────────────────────────────────────────
    def has_pending(self, user_id: int) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM pending WHERE user_id = ?", (user_id,)
            ).fetchone()
        return row is not None

    def add_pending(self, user_id: int):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO pending (user_id, created_at) VALUES (?, ?)",
                (user_id, datetime.now().strftime("%d.%m.%Y %H:%M"))
            )

    def remove_pending(self, user_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM pending WHERE user_id = ?", (user_id,))

    # ── Analytics ─────────────────────────────────────────────────────────────
    def track(self, user_id: int, event: str):
        """
        Events:
        - start        → /start басты
        - pay_click    → төлем кнопкасын басты
        - screenshot   → скриншот жіберді
        - approved     → сатып алды
        - rejected     → қабылданбады
        """
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO analytics (user_id, event, created_at) VALUES (?, ?, ?)",
                (user_id, event, datetime.now().strftime("%Y-%m-%d %H:%M"))
            )

    def get_analytics(self, date_from: str = None, date_to: str = None) -> dict:
        """Воронка аналитикасы — жалпы немесе кезең бойынша"""
        with self._conn() as conn:
            events = ["start", "pay_click", "screenshot", "approved", "rejected"]
            result = {}

            for event in events:
                if date_from and date_to:
                    row = conn.execute(
                        """SELECT COUNT(DISTINCT user_id) FROM analytics
                           WHERE event = ? AND created_at >= ? AND created_at <= ?""",
                        (event, date_from, date_to)
                    ).fetchone()
                else:
                    row = conn.execute(
                        "SELECT COUNT(DISTINCT user_id) FROM analytics WHERE event = ?",
                        (event,)
                    ).fetchone()
                result[event] = row[0] if row else 0

        return result

    def get_daily_stats(self, days: int = 7) -> list:
        """Соңғы N күннің күнделікті статистикасы"""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT DATE(created_at) as day,
                          SUM(CASE WHEN event='start' THEN 1 ELSE 0 END) as starts,
                          SUM(CASE WHEN event='approved' THEN 1 ELSE 0 END) as sales
                   FROM analytics
                   WHERE created_at >= DATE('now', ?)
                   GROUP BY day
                   ORDER BY day DESC""",
                (f"-{days} days",)
            ).fetchall()
        return [{"day": r[0], "starts": r[1], "sales": r[2]} for r in rows]
