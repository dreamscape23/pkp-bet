'use client';

import { useEffect, useState } from 'react';
import { API_BASE, Run } from '../lib/api';

export default function RunsList() {
  const [runs, setRuns] = useState<Run[]>([]);

  const loadRuns = async () => {
    const res = await fetch(`${API_BASE}/runs/today`);
    if (!res.ok) return;
    setRuns(await res.json());
  };

  useEffect(() => {
    loadRuns();
    const id = setInterval(loadRuns, 15000);
    return () => clearInterval(id);
  }, []);

  return (
    <section>
      <h1>Dzisiejsze pociągi IC</h1>
      {runs.map((run) => (
        <div key={run.id} className="card">
          <strong>{run.train_number}</strong> {run.route_name ?? ''}
          <div>Opóźnienie live: {run.latest_delay_minutes} min</div>
        </div>
      ))}
      {runs.length === 0 && <p>Brak danych. Sprawdź klucz API i działanie backendu.</p>}
    </section>
  );
}
