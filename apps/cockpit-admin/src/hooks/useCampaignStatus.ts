import { api } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';

/**
 * Shape of the gateway's ``/admin/training/status`` payload.
 *
 * Mirrors ``src/gateway/training/orchestrator.py::status()`` — see the
 * gateway repo for the source of truth. The cockpit-api proxies the
 * response verbatim, so anything new on the gateway shows up here.
 */
export interface CampaignVerdict {
  // The gateway returns a string per domain; concrete values are
  // OK | SUSPECT_OVERFIT | SUSPECT_UNDERTRAIN | FAILED_OOM | INCOMPLETE | NO_DATA.
  [domain: string]: string;
}

export interface CampaignStatus {
  // Overall orchestrator state: IDLE | TRAINING | DONE | FAILED | ABORTED
  status: string;
  campaign?: string | null;
  current_domain?: string | null;
  domain_index?: number | null;
  domains_total?: number | null;
  phase?: number | null;
  phase_total?: number | null;
  iter?: number | null;
  iter_total?: number | null;
  abort_requested?: boolean;
  verdicts?: CampaignVerdict;
  reload_failed?: boolean;
  error?: string | null;
  // Tolerant of unknown fields the gateway may add.
  [key: string]: unknown;
}

export function useCampaignStatus() {
  return useQuery<CampaignStatus>({
    queryKey: ['campaign-status'],
    queryFn: ({ signal }) =>
      api.get<CampaignStatus>('/api/admin/training/campaign/status', { signal }),
    refetchInterval: 30_000,
  });
}
