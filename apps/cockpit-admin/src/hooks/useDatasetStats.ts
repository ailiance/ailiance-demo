import { api } from '@/lib/api';
import type { components } from '@cockpit/shared';
import { useQuery } from '@tanstack/react-query';

type DatasetStats = components['schemas']['DatasetStats'];

export function useDatasetStats(domain: string) {
  return useQuery<DatasetStats>({
    queryKey: ['dataset-stats', domain],
    queryFn: ({ signal }) =>
      api.get<DatasetStats>(`/api/admin/datasets/${domain}/stats`, { signal }),
    staleTime: 60_000,
  });
}
