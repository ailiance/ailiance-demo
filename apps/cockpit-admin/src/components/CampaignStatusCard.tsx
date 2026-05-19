import type { CampaignStatus } from '@/hooks/useCampaignStatus';
import { Activity, AlertCircle, CheckCircle2, Pause, XCircle } from 'lucide-react';

interface Props {
  status: CampaignStatus;
}

function statusVisuals(s: string): { Icon: typeof Activity; color: string } {
  switch (s) {
    case 'TRAINING':
      return { Icon: Activity, color: 'text-emerald-600' };
    case 'DONE':
      return { Icon: CheckCircle2, color: 'text-slate-500' };
    case 'FAILED':
      return { Icon: XCircle, color: 'text-rose-600' };
    case 'ABORTED':
      return { Icon: AlertCircle, color: 'text-amber-600' };
    case 'IDLE':
    default:
      return { Icon: Pause, color: 'text-slate-400' };
  }
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div className="h-2 rounded bg-slate-200 overflow-hidden" aria-label={`${pct}%`}>
      <div
        className="h-full bg-violet-500 transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export function CampaignStatusCard({ status }: Props) {
  const { Icon, color } = statusVisuals(status.status);
  const di = status.domain_index ?? 0;
  const dt = status.domains_total ?? 0;
  const it = status.iter ?? 0;
  const itTotal = status.iter_total ?? 0;
  const phase = status.phase ?? 0;
  const phaseTotal = status.phase_total ?? 3;

  return (
    <section className="rounded border border-slate-200 bg-white p-4">
      <header className="flex items-center justify-between">
        <h3 className="font-bold">
          {status.campaign ?? 'medium35 campaign'}
        </h3>
        <span className={`inline-flex items-center gap-1 text-xs ${color}`}>
          <Icon size={14} /> {status.status}
        </span>
      </header>

      <dl className="mt-3 grid grid-cols-2 gap-y-1 text-sm">
        <dt className="text-slate-500">Current domain</dt>
        <dd className="font-mono">{status.current_domain ?? '—'}</dd>
        <dt className="text-slate-500">Phase</dt>
        <dd className="font-mono">
          {phase}/{phaseTotal}
        </dd>
        <dt className="text-slate-500">Iter</dt>
        <dd className="font-mono">
          {it}
          {itTotal ? ` / ${itTotal}` : ''}
        </dd>
        <dt className="text-slate-500">Domain</dt>
        <dd className="font-mono">
          {di}
          {dt ? ` / ${dt}` : ''}
        </dd>
      </dl>

      {dt > 0 && (
        <div className="mt-4 space-y-2">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Overall progress</span>
              <span className="font-mono">
                {di}/{dt}
              </span>
            </div>
            <ProgressBar value={di} max={dt} />
          </div>
          {itTotal > 0 && (
            <div>
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span>Current domain progress</span>
                <span className="font-mono">
                  {it}/{itTotal}
                </span>
              </div>
              <ProgressBar value={it} max={itTotal} />
            </div>
          )}
        </div>
      )}

      {status.error && (
        <p className="mt-3 text-xs text-rose-600">Error: {status.error}</p>
      )}
      {status.reload_failed && (
        <p className="mt-2 text-xs text-amber-600">
          Reload failed — workers may need manual recovery.
        </p>
      )}
      {status.abort_requested && status.status === 'TRAINING' && (
        <p className="mt-2 text-xs text-amber-600">
          Abort requested — current domain finishing.
        </p>
      )}
    </section>
  );
}
