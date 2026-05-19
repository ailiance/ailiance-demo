import { api } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface AbortResponse {
  aborted?: boolean;
  [key: string]: unknown;
}

export function useAbortCampaign() {
  const qc = useQueryClient();
  return useMutation<AbortResponse, Error, void>({
    mutationFn: () => api.post<AbortResponse>('/api/admin/training/campaign/abort', {}),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['campaign-status'] });
    },
  });
}
