'use client';

import { useEffect, useState } from 'react';
import { API_BASE, LeaderboardRow } from '../lib/api';

export default function LeaderboardTable() {
  const [rows, setRows] = useState<LeaderboardRow[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/leaderboard`).then(async (res) => {
      if (res.ok) setRows(await res.json());
    });
  }, []);

  return (
    <section>
      <h1>Ranking</h1>
      <ol>
        {rows.map((row) => (
          <li key={row.user_id}>
            {row.username}: {row.balance.toFixed(2)} PLN
          </li>
        ))}
      </ol>
    </section>
  );
}
