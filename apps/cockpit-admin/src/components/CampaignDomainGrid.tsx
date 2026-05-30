import type { CampaignVerdict } from '@/hooks/useCampaignStatus';

interface Props {
  verdicts: CampaignVerdict | undefined;
  currentDomain?: string | null;
}

function verdictClass(v: string | undefined): string {
  if (!v) return 'bg-slate-100 text-slate-500';
  switch (v) {
    case 'OK':
      return 'bg-emerald-100 text-emerald-700';
    case 'SUSPECT_OVERFIT':
    case 'SUSPECT_UNDERTRAIN':
      return 'bg-amber-100 text-amber-700';
    case 'FAILED_OOM':
      return 'bg-rose-100 text-rose-700';
    case 'INCOMPLETE':
    case 'NO_DATA':
      return 'bg-slate-200 text-slate-600';
    default:
      return 'bg-slate-100 text-slate-700';
  }
}

export function CampaignDomainGrid({ verdicts, currentDomain }: Props) {
  // The gateway's /admin/training/status doesn't expose the ordered domain
  // list — only verdicts populated so far. We list those in arrival order
  // (insertion order is preserved by JSON parsing) and tag the in-flight
  // domain separately if it isn't yet in `verdicts`.
  const entries = Object.entries(verdicts ?? {});
  if (currentDomain && !entries.some(([d]) => d === currentDomain)) {
    entries.push([currentDomain, '']);
  }

  if (entries.length === 0) {
    return (
      <section className="rounded border border-slate-200 bg-white p-4 text-sm text-slate-500">
        No domain verdicts yet.
      </section>
    );
  }

  return (
    <section className="rounded border border-slate-200 bg-white p-4">
      <h3 className="font-bold mb-3">Domain verdicts ({entries.length})</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b border-slate-200">
            <th className="py-1 pr-2 font-medium">#</th>
            <th className="py-1 pr-2 font-medium">Domain</th>
            <th className="py-1 font-medium">Verdict</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([domain, verdict], idx) => {
            const isCurrent = domain === currentDomain;
            return (
              <tr
                key={domain}
                className={`border-b border-slate-100 ${isCurrent ? 'bg-violet-50' : ''}`}
              >
                <td className="py-1 pr-2 font-mono text-slate-400">{idx + 1}</td>
                <td className="py-1 pr-2 font-mono">
                  {domain}
                  {isCurrent && <span className="ml-2 text-xs text-violet-600">(active)</span>}
                </td>
                <td className="py-1">
                  {verdict ? (
                    <span
                      className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${verdictClass(verdict)}`}
                    >
                      {verdict}
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400">pending</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
