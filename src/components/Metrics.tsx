import React from 'react';
import data from '../data/validator-metrics.json';

type Group = {name: string; rows: number; recall: number | null; precision: number | null};
const fmtLatency = (ms: number) => (ms >= 1000 ? `${(ms / 1000).toFixed(1)} s` : ms >= 10 ? `${Math.round(ms)} ms` : `${+ms.toFixed(2)} ms`);
const pct = (x: number | null) => (x == null ? '—' : `${x}%`);

export function MetricsHeadline({validator}: {validator: string}) {
  const m = (data as any)[validator];
  return (
    <table>
      <thead><tr><th>Accuracy</th><th>Response time</th></tr></thead>
      <tbody><tr><td><strong>{m.accuracy}%</strong></td><td><strong>{fmtLatency(m.latency_ms)}</strong></td></tr></tbody>
    </table>
  );
}

export function MetricsDetails({validator, method}: {validator: string; method: string}) {
  const m = (data as any)[validator];
  const groups: Group[] = m.groups;
  return (
    <>
      <table>
        <thead><tr><th>Method</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>Sample size</th></tr></thead>
        <tbody><tr><td>{method}</td><td>{m.accuracy}%</td><td>{m.precision}%</td><td>{m.recall}%</td><td>{m.f1}%</td><td>{m.rows.toLocaleString()}</td></tr></tbody>
      </table>
      <table>
        <thead><tr><th>Group</th><th>Messages</th><th>Recall</th><th>Precision</th></tr></thead>
        <tbody>{groups.map(g => <tr key={g.name}><td>{g.name}</td><td>{g.rows}</td><td>{pct(g.recall)}</td><td>{pct(g.precision)}</td></tr>)}</tbody>
      </table>
      <p>
        Evaluation run of {data._run.date}. <strong>Precision ({m.precision}%)</strong> is how often a flagged message really had a problem.{' '}
        <strong>Recall ({m.recall}%)</strong> is how many real problems were caught. <strong>F1 ({m.f1}%)</strong> balances the two.
      </p>
    </>
  );
}
