import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/transparency')({
  component: TransparencyPage,
});

interface ProvenanceLink {
  alias: string;
  display: string;
  base: string;
  provider: string;
  license: string;
  provenance_url: string;
  notes?: string;
}

const ENTRIES: ProvenanceLink[] = [
  {
    alias: 'ailiance/apertus-70b',
    display: 'Apertus 70B Instruct',
    base: 'swiss-ai/Apertus-70B-Instruct-2509',
    provider: 'Swiss AI Initiative (EPFL/ETHZ/CSCS)',
    license: 'Apache-2.0',
    provenance_url:
      'https://github.com/L-electron-Rare/ailiance/blob/main/docs/provenance/apertus-70b-instruct-2509.json',
  },
  {
    alias: 'ailiance/devstral-24b',
    display: 'Devstral Small 2 24B Instruct',
    base: 'mistralai/Devstral-Small-2-24B-Instruct-2512',
    provider: 'Mistral AI',
    license: 'Apache-2.0',
    provenance_url:
      'https://github.com/L-electron-Rare/ailiance/blob/main/docs/provenance/devstral-small-2-24b-instruct-2512.json',
  },
  {
    alias: 'ailiance/eurollm-22b',
    display: 'EuroLLM 22B Instruct',
    base: 'utter-project/EuroLLM-22B-Instruct-2512',
    provider: 'Utter Project (EU consortium)',
    license: 'Apache-2.0',
    provenance_url:
      'https://github.com/L-electron-Rare/ailiance/blob/main/docs/provenance/eurollm-22b-instruct-2512.json',
  },
  {
    alias: 'ailiance/gemma3-4b',
    display: 'Gemma 3 4B IT',
    base: 'google/gemma-3-4b-it',
    provider: 'Google DeepMind',
    license: 'Gemma Terms of Use',
    provenance_url:
      'https://github.com/L-electron-Rare/ailiance/blob/main/docs/provenance/gemma3-4b-it.json',
    notes: 'Light-weight worker — runs on tower (NVIDIA Quadro P2000 5 GB).',
  },
  {
    alias: 'ailiance/qwen3-next-80b-a3b-instruct',
    display: 'Qwen3-Next 80B A3B Instruct',
    base: 'Qwen/Qwen3-Next-80B-A3B-Instruct',
    provider: 'Qwen (Alibaba Cloud)',
    license: 'Apache-2.0',
    provenance_url:
      'https://github.com/L-electron-Rare/ailiance/blob/main/docs/provenance/qwen3-next-80b-a3b-instruct.json',
    notes: 'MoE 80B / 3B active. Runs on kxkm-ai (RTX 4090) via llama.cpp with expert offload to RAM.',
  },
  {
    alias: 'ailiance/auto',
    display: 'Auto-router (MiniLM + MLP head)',
    base: 'sentence-transformers/all-MiniLM-L6-v2 + internal head',
    provider: 'Microsoft (encoder) + L\'Électron Rare (head)',
    license: 'Apache-2.0',
    provenance_url:
      'https://github.com/L-electron-Rare/ailiance/blob/main/docs/provenance/auto-router-minilm.json',
    notes: 'Routing classifier only — no chat output of its own.',
  },
  {
    alias: '(routing fallback) Gemma 3 4B IT',
    display: 'Gemma 3 4B IT — fallback worker',
    base: 'google/gemma-3-4b-it',
    provider: 'Google',
    license: 'Gemma Terms',
    provenance_url:
      'https://github.com/L-electron-Rare/ailiance/blob/main/docs/provenance/gemma-3-4b-it.json',
    notes: 'Used only by the auto-router as a quick fallback when no labelled domain matches.',
  },
];

function TransparencyPage() {
  return (
    <article className="max-w-4xl mx-auto prose prose-slate">
      <h1>Transparency &amp; provenance</h1>

      <p>
        This site is operated by <strong>L'Électron Rare</strong> as a public showcase of an
        EU-sovereign LLM stack. It is subject to the EU Artificial Intelligence Act (Regulation
        (EU) 2024/1689). The disclosures below cover Article 50 (transparency for users) and
        Annex IV (technical documentation).
      </p>

      <h2>You are interacting with an AI</h2>
      <p>
        Every chat reply on this site is produced by a Large Language Model. Outputs may be
        inaccurate, biased or fabricated. They are not professional advice. Do not act on a
        reply without independent verification, especially in regulated domains (health, law,
        finance, safety-critical engineering).
      </p>

      <h2>Models served</h2>
      <table className="text-sm">
        <thead>
          <tr>
            <th>Alias</th>
            <th>Base model</th>
            <th>Provider</th>
            <th>Licence</th>
            <th>Provenance</th>
          </tr>
        </thead>
        <tbody>
          {ENTRIES.map((e) => (
            <tr key={e.alias}>
              <td>
                <code>{e.alias}</code>
                {e.notes && <p className="text-xs text-slate-500 mt-1">{e.notes}</p>}
              </td>
              <td>
                <code>{e.base}</code>
              </td>
              <td>{e.provider}</td>
              <td>{e.license}</td>
              <td>
                <a href={e.provenance_url} target="_blank" rel="noopener noreferrer">
                  JSON ↗
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>What we record per model</h2>
      <ul>
        <li>Source repository and the exact upstream commit SHA we pinned to</li>
        <li>Licence (SPDX identifier where applicable)</li>
        <li>Architecture, total parameters, active parameters per token</li>
        <li>Quantisation method and who produced it</li>
        <li>Any post-download modification (LoRA fine-tunes, merges, distillation)</li>
        <li>Intended use and out-of-scope use cases</li>
      </ul>

      <h2>LoRA adapters published on HuggingFace</h2>
      <p>
        We publish ~25 domain-specific LoRA adapters under{' '}
        <a href="https://huggingface.co/clemsail" target="_blank" rel="noopener noreferrer">
          clemsail
        </a>{' '}
        and{' '}
        <a href="https://huggingface.co/electron-rare" target="_blank" rel="noopener noreferrer">
          electron-rare
        </a>
        . Each adapter ships a model card declaring its base model, training data summary, and
        intended use, in line with Article 53 obligations for general-purpose AI providers.
      </p>

      <h2>Training data &amp; copyright</h2>
      <p>
        Adapters are trained on a mix of L'Électron Rare in-house corpora (synthetic distillation
        from Claude Opus reasoning traces, public technical documentation, manually curated
        prompts) and licensed open datasets. We do not knowingly train on scraped copyrighted
        material; opt-out signals (robots.txt, ai.txt) are respected for any web data. The
        full per-dataset breakdown lives in{' '}
        <a
          href="https://github.com/L-electron-Rare/ailiance/tree/main/docs/transparency"
          target="_blank"
          rel="noopener noreferrer"
        >
          docs/transparency/
        </a>{' '}
        of the ailiance repository.
      </p>

      <h2>Logs &amp; data retention</h2>
      <p>
        The cockpit API logs request metadata (timestamp, model alias, token counts, response
        latency) for ≤ 30 days for operational debugging and rate-limit enforcement. Prompt
        and reply <strong>content</strong> is not persisted to disk by default. Streaming chat
        sessions only live in volatile memory.
      </p>

      <h2>Audit-grade benchmark — <code>iact-bench v0.2.0</code></h2>
      <p>
        Capability and reliability of every model in our catalogue is measured by{' '}
        <a
          href="https://github.com/electron-rare/iact-bench"
          target="_blank"
          rel="noopener noreferrer"
        >
          iact-bench
        </a>{' '}
        — an audit-grade evaluation harness aligned with EU AI Act Article 53(1)(d) and
        Annex XI. The matrix runs <strong>31 canonical domains × ≤ 23 GPAI-eligible models</strong>{' '}
        with a triple metric: perplexity + task-score + LLM-judge + <strong>sandboxed
        validators</strong>. For each cell we record:
      </p>
      <ul>
        <li><code>run_id</code>, <code>git_sha</code>, <code>methodology</code> version (currently <code>v1</code>)</li>
        <li><code>prompt_hash</code> and <code>output_hash</code> (sha256)</li>
        <li><code>seed</code> (crc32 deterministic per cell + sample index)</li>
        <li><code>validator_image_digest</code> — pinned sha256 of the Docker image used</li>
        <li><code>validator_exit_code</code>, truncated stdout/stderr — for reproducible re-runs</li>
      </ul>
      <p>
        Validators run inside Docker sandboxes with{' '}
        <code>--network=none --read-only --user 1000:1000 --cap-drop=ALL</code>, which makes
        the model output the <em>sole</em> input to the validator: no data exfiltration, no
        environment leakage. Twelve validators are sandbox-stable today (g++, arm-none-eabi-gcc,
        cargo embedded, shellcheck, tsc, ngspice, KiCad DRC/ERC, FreeCAD scripting, html5lib
        strict, sqlglot, JSON/YAML); ten additional v0.3 EDA/MCAD-as-code validators (SKiDL,
        tscircuit, Circuit-Synth, Xyce, Lcapy, CadQuery, build123d, OpenSCAD, JSCAD,
        ImplicitCAD) ship in v0.3.0.
      </p>
      <p>
        The full methodology document, audit walkthrough, and EU sovereignty charter live in{' '}
        <a
          href="https://github.com/electron-rare/iact-bench/blob/master/docs/methodology/2026-05-10-iact-bench-methodology-v1.md"
          target="_blank"
          rel="noopener noreferrer"
        >
          docs/methodology/v1.md
        </a>
        . An external auditor can pull any pinned validator image by digest, replay any cell
        trace, and verify the recorded score byte-for-byte.
      </p>

      <h2>Contact &amp; right to opt out</h2>
      <p>
        Reports of biased output, copyright concerns, or any other AI Act issue: email{' '}
        <a href="mailto:postmaster@saillant.cc">postmaster@saillant.cc</a>. We aim to respond
        within 7 working days.
      </p>
    </article>
  );
}
