'use client';

import { FormEvent, useState } from 'react';
import { API_BASE } from '../lib/api';

export default function BetForm() {
  const [userId, setUserId] = useState(1);
  const [runId, setRunId] = useState(1);
  const [minutes, setMinutes] = useState(10);
  const [stake, setStake] = useState(5);
  const [message, setMessage] = useState('');

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const res = await fetch(`${API_BASE}/bets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, train_run_id: runId, predicted_delay_minutes: minutes, stake }),
    });
    if (res.ok) {
      setMessage('Zakład zapisany!');
    } else {
      const data = await res.json();
      setMessage(`Błąd: ${data.detail ?? 'nieznany'}`);
    }
  };

  return (
    <form onSubmit={submit}>
      <h1>Obstaw opóźnienie</h1>
      <label>
        ID użytkownika
        <input type="number" value={userId} onChange={(e) => setUserId(Number(e.target.value))} min={1} />
      </label>
      <label>
        ID pociągu
        <input type="number" value={runId} onChange={(e) => setRunId(Number(e.target.value))} min={1} />
      </label>
      <label>
        Przewidywane opóźnienie: {minutes} min
        <input type="range" min={0} max={180} value={minutes} onChange={(e) => setMinutes(Number(e.target.value))} />
      </label>
      <label>
        Stawka (PLN)
        <input type="number" step="0.5" min={0.5} value={stake} onChange={(e) => setStake(Number(e.target.value))} />
      </label>
      <button type="submit">Obstaw</button>
      {message && <p>{message}</p>}
    </form>
  );
}
