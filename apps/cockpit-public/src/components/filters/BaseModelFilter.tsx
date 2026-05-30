const BASES = [
  'mistral-medium-128b',
  'qwen3.6-35b',
  'devstral-24b',
  'eurollm-22b',
  'granite-4.1-30b',
  'gemma-4-e4b',
  'apertus-70b',
] as const;

interface Props {
  value: string | undefined;
  onChange: (v: string | undefined) => void;
}

export function BaseModelFilter({ value, onChange }: Props) {
  return (
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value || undefined)}
      className="rounded border border-slate-300 p-1 text-sm"
    >
      <option value="">All base models</option>
      {BASES.map((b) => (
        <option key={b} value={b}>
          {b}
        </option>
      ))}
    </select>
  );
}
