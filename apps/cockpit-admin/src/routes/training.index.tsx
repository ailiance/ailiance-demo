import { TrainingDesigner } from '@/components/TrainingDesigner';
import { TrainingRunCard } from '@/components/TrainingRunCard';
import { useTrainingRuns } from '@/hooks/useTrainingRuns';
import { Link, createFileRoute, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';

export const Route = createFileRoute('/training/')({
  component: TrainingListPage,
});

function TrainingListPage() {
  const { data, isLoading, error } = useTrainingRuns();
  const [designerOpen, setDesignerOpen] = useState(false);
  const navigate = useNavigate();

  if (isLoading) return <p className="text-slate-500">Loading runs…</p>;
  if (error) return <p className="text-rose-700">Failed to load runs</p>;
  if (!data || data.length === 0) {
    return (
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Training runs</h2>
          <div className="flex items-center gap-2">
            <Link
              to="/training/campaign"
              className="px-3 py-1 bg-slate-200 hover:bg-slate-300 rounded text-sm text-slate-800"
            >
              Campaign
            </Link>
            <button
              type="button"
              className="px-3 py-1 bg-violet-600 hover:bg-violet-500 rounded text-sm"
              onClick={() => setDesignerOpen(true)}
            >
              + Launch new run
            </button>
          </div>
        </div>
        <p className="text-slate-500">No training runs found in the configured directories.</p>
        {designerOpen && (
          <TrainingDesigner
            onClose={() => setDesignerOpen(false)}
            onLaunched={(runId) => navigate({ to: '/training/$id', params: { id: runId } })}
          />
        )}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Training runs ({data.length})</h2>
        <button
          type="button"
          className="px-3 py-1 bg-violet-600 hover:bg-violet-500 rounded text-sm"
          onClick={() => setDesignerOpen(true)}
        >
          + Launch new run
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.map((run) => (
          <TrainingRunCard key={run.id} run={run} />
        ))}
      </div>
      {designerOpen && (
        <TrainingDesigner
          onClose={() => setDesignerOpen(false)}
          onLaunched={(runId) => navigate({ to: '/training/$id', params: { id: runId } })}
        />
      )}
    </div>
  );
}
