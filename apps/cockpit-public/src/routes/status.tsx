import { getStatus, getTelemetry } from '@/lib/server-fns';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/status')({
  loader: async () => ({
    status: await getStatus(),
    telemetry: await getTelemetry(),
  }),
});
