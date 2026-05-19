import { CampaignControls } from '@/components/CampaignControls';
import { CampaignDomainGrid } from '@/components/CampaignDomainGrid';
import { CampaignStatusCard } from '@/components/CampaignStatusCard';
import { LogTail } from '@/components/LogTail';
import type { LogEvent } from '@/hooks/useTrainingLogs';
import { useCampaignLog } from '@/hooks/useCampaignLog';
import { useCampaignStatus } from '@/hooks/useCampaignStatus';
import { createFileRoute } from '@tanstack/react-router';
import { useMemo } from 'react';

export const Route = createFileRoute('/training/campaign')({
  component: CampaignPage,
});

function isTerminalOrIdle(s: string): boolean {
  return s === 'IDLE' || s === 'DONE' || s === 'FAILED' || s === 'ABORTED';
}

function CampaignPage() {
  const statusQ = useCampaignStatus();
  const currentDomain = statusQ.data?.current_domain ?? null;
  const logQ = useCampaignLog(currentDomain, 200);

  const logEvents = useMemo<LogEvent[]>(() => {
    if (!logQ.data) return [];
    return logQ.data
      .split('\n')
      .filter((line) => line.length > 0)
      .map((line) => ({ type: 'raw' as const, raw: line }));
  }, [logQ.data]);

  if (statusQ.isLoading) {
    return <p className="text-slate-500">Loading campaign status…</p>;
  }
  if (statusQ.error || !statusQ.data) {
    return (
      <p className="text-rose-700">
        Failed to load campaign status: {statusQ.error?.message ?? 'unknown error'}
      </p>
    );
  }

  const status = statusQ.data;
  const idle = isTerminalOrIdle(status.status);

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">medium35 campaign</h2>
        <CampaignControls status={status} />
      </header>

      <CampaignStatusCard status={status} />

      {idle && (
        <p className="text-sm text-slate-500">
          {status.status === 'IDLE'
            ? 'Aucune campagne active.'
            : `Campagne ${status.status.toLowerCase()}. Les verdicts ci-dessous sont l’historique de la dernière exécution.`}
        </p>
      )}

      <CampaignDomainGrid
        verdicts={status.verdicts}
        currentDomain={currentDomain}
      />

      {currentDomain && (
        <section className="space-y-2">
          <h3 className="font-bold">
            Log tail —{' '}
            <span className="font-mono text-sm">{currentDomain}</span>
            {logQ.isFetching && (
              <span className="ml-2 text-xs text-slate-400">refreshing…</span>
            )}
          </h3>
          {logQ.error ? (
            <p className="text-sm text-rose-600">
              Failed to load log: {logQ.error.message}
            </p>
          ) : (
            <LogTail events={logEvents} />
          )}
        </section>
      )}
    </div>
  );
}
