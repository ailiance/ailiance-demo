const STATUSES = ['featured', 'production', 'alpha', 'experimental', 'deprecated'] as const;

interface Props {
  value: string | undefined;
  onChange: (v: string | undefined) => void;
}

export function StatusFilter({ value, onChange }: Props) {
  return (
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value || undefined)}
      className="rounded border border-slate-300 p-1 text-sm"
    >
      <option value="">All statuses</option>
      {STATUSES.map((s) => (
        <option key={s} value={s}>
          {s}
        </option>
      ))}
    </select>
  );
}
