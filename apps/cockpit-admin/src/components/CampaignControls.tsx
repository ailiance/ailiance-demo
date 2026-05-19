import { useAbortCampaign } from '@/hooks/useAbortCampaign';
import type { CampaignStatus } from '@/hooks/useCampaignStatus';
import { useStartCampaign } from '@/hooks/useStartCampaign';
import { Play, Square } from 'lucide-react';
import { useState } from 'react';

interface Props {
  status: CampaignStatus;
}

// Default domain selection, copied from the prompt. Hardware tier first,
// then generalist tier — both pre-checked by default.
const HARDWARE_DOMAINS = [
  'kicad-dsl',
  'kicad-pcb',
  'platformio',
  'rust-embedded',
  'spice-sim',
  'iot',
  'freecad',
  'emc-dsp-power',
  'embedded',
];

const GENERALIST_DOMAINS = [
  'python',
  'rust',
  'typescript',
  'web-backend',
  'web-frontend',
  'sql',
  'shell',
  'yaml-json',
  'html-css',
  'lua-upy',
  'ml-training',
  'llm-ops',
  'llm-orch',
  'math-gsm8k',
  'math-reasoning',
  'music-audio',
  'multilingual-eu',
  'traduction-tech',
  'security-fenrir',
];

const ALL_DOMAINS = [...HARDWARE_DOMAINS, ...GENERALIST_DOMAINS];

function isTerminal(s: string): boolean {
  return s === 'IDLE' || s === 'DONE' || s === 'FAILED' || s === 'ABORTED';
}

export function CampaignControls({ status }: Props) {
  const start = useStartCampaign();
  const abort = useAbortCampaign();

  const [startOpen, setStartOpen] = useState(false);
  const [abortOpen, setAbortOpen] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set(ALL_DOMAINS));

  const startDisabled = status.status !== 'IDLE' && !isTerminal(status.status);
  const abortDisabled = isTerminal(status.status);

  const toggle = (d: string) =>
    setSelected((cur) => {
      const next = new Set(cur);
      if (next.has(d)) next.delete(d);
      else next.add(d);
      return next;
    });

  const handleStart = () => {
    const domains = ALL_DOMAINS.filter((d) => selected.has(d));
    start.mutate(
      { domains: domains.length === ALL_DOMAINS.length ? undefined : domains },
      { onSuccess: () => setStartOpen(false) },
    );
  };

  const handleAbort = () => {
    abort.mutate(undefined, { onSuccess: () => setAbortOpen(false) });
  };

  return (
    <section className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => setStartOpen(true)}
        disabled={startDisabled}
        title={startDisabled ? 'campagne déjà active' : 'Démarrer la campagne'}
        className="inline-flex items-center gap-2 rounded bg-emerald-600 px-3 py-1 text-sm text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        <Play size={14} /> Start
      </button>
      <button
        type="button"
        onClick={() => setAbortOpen(true)}
        disabled={abortDisabled}
        title={abortDisabled ? 'Aucune campagne active' : 'Abandonner la campagne'}
        className="inline-flex items-center gap-2 rounded bg-rose-600 px-3 py-1 text-sm text-white hover:bg-rose-500 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        <Square size={14} /> Abort
      </button>

      {start.error && (
        <span className="text-xs text-rose-600">Start failed: {start.error.message}</span>
      )}
      {abort.error && (
        <span className="text-xs text-rose-600">Abort failed: {abort.error.message}</span>
      )}

      {startOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/50"
          onClick={() => setStartOpen(false)}
        >
          <div
            className="max-h-[80vh] w-full max-w-2xl overflow-y-auto rounded bg-white p-6 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold mb-2">Start medium35 campaign</h3>
            <p className="text-sm text-slate-600 mb-4">
              Sélectionnez les domaines à entraîner. Tous sont cochés par défaut.
            </p>

            <div className="space-y-4">
              <DomainCheckboxGroup
                title="Hardware tier"
                domains={HARDWARE_DOMAINS}
                selected={selected}
                toggle={toggle}
              />
              <DomainCheckboxGroup
                title="Generalist tier"
                domains={GENERALIST_DOMAINS}
                selected={selected}
                toggle={toggle}
              />
            </div>

            <footer className="mt-6 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setStartOpen(false)}
                className="rounded border border-slate-300 px-3 py-1 text-sm hover:bg-slate-50"
              >
                Annuler
              </button>
              <button
                type="button"
                onClick={handleStart}
                disabled={start.isPending || selected.size === 0}
                className="rounded bg-emerald-600 px-3 py-1 text-sm text-white hover:bg-emerald-500 disabled:bg-slate-300"
              >
                {start.isPending ? 'Démarrage…' : `Submit (${selected.size})`}
              </button>
            </footer>
          </div>
        </div>
      )}

      {abortOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/50"
          onClick={() => setAbortOpen(false)}
        >
          <div
            className="w-full max-w-md rounded bg-white p-6 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold mb-2">Abandonner la campagne ?</h3>
            <p className="text-sm text-slate-600">
              Le domaine en cours finira, puis les workers seront rechargés.
            </p>
            <footer className="mt-6 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setAbortOpen(false)}
                className="rounded border border-slate-300 px-3 py-1 text-sm hover:bg-slate-50"
              >
                Annuler
              </button>
              <button
                type="button"
                onClick={handleAbort}
                disabled={abort.isPending}
                className="rounded bg-rose-600 px-3 py-1 text-sm text-white hover:bg-rose-500 disabled:bg-slate-300"
              >
                {abort.isPending ? 'Abandon…' : 'Confirmer l’abandon'}
              </button>
            </footer>
          </div>
        </div>
      )}
    </section>
  );
}

function DomainCheckboxGroup({
  title,
  domains,
  selected,
  toggle,
}: {
  title: string;
  domains: string[];
  selected: Set<string>;
  toggle: (d: string) => void;
}) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-slate-700 mb-2">{title}</h4>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-1">
        {domains.map((d) => (
          <label
            key={d}
            className="flex items-center gap-2 text-sm cursor-pointer hover:bg-slate-50 px-1 py-0.5 rounded"
          >
            <input
              type="checkbox"
              checked={selected.has(d)}
              onChange={() => toggle(d)}
            />
            <span className="font-mono text-xs">{d}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
