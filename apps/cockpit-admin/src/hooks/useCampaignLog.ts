import { useQuery } from '@tanstack/react-query';

/**
 * Fetch the tail of the current campaign domain's training log as plain
 * text. The proxy endpoint returns ``text/plain`` so we use raw fetch
 * rather than the JSON ``api`` client.
 */
export function useCampaignLog(domain: string | null | undefined, tail = 200) {
  return useQuery<string>({
    queryKey: ['campaign-log', domain, tail],
    enabled: !!domain,
    queryFn: async ({ signal }) => {
      const url = `/api/admin/training/campaign/log/${domain}?tail=${tail}`;
      const response = await fetch(url, { signal });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status} fetching campaign log`);
      }
      return response.text();
    },
    refetchInterval: 30_000,
  });
}
