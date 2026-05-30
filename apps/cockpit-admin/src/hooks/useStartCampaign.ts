import { api } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface StartBody {
  domains?: string[];
}

interface StartResponse {
  accepted?: boolean;
  [key: string]: unknown;
}

export function useStartCampaign() {
  const qc = useQueryClient();
  return useMutation<StartResponse, Error, StartBody>({
    mutationFn: (body) => api.post<StartResponse>('/api/admin/training/campaign/start', body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['campaign-status'] });
    },
  });
}
