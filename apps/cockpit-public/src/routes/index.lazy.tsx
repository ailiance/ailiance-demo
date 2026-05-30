import { Link, createLazyFileRoute } from '@tanstack/react-router';

export const Route = createLazyFileRoute('/')({
  component: OffrePage,
});

/* ── L'offre en quatre volets ──────────────────────────────────────────── */
const OFFER = [
  {
    num: 'I',
    t: 'Adaptation de modèles ouverts',
    d: 'Llama, Mistral, Qwen, Gemma… sélectionnés puis fine-tunés pour votre domaine. Génératifs ou non (classification, extraction, scoring). Aucun modèle propriétaire fermé.',
    tag: 'OPEN-WEIGHTS',
  },
  {
    num: 'II',
    t: 'Structuration de vos données',
    d: 'Audit, cartographie et mise en qualité de vos données métier : formats, volumes, sensibilité. La donnée structurée est le carburant de l’entraînement.',
    tag: 'DATA',
  },
  {
    num: 'III',
    t: 'Entraînement souverain',
    d: 'Fine-tuning supervisé dans un environnement isolé. LoRA, QLoRA ou full fine-tuning selon le volume. Vos données ne quittent jamais votre périmètre.',
    tag: 'ON-PREMISE',
  },
  {
    num: 'IV',
    t: 'Orchestration en production',
    d: 'Routeur intelligent, agents de vérification et de fallback, monitoring continu. Le modèle reste sous contrôle et s’améliore avec l’usage.',
    tag: 'INFERENCE',
  },
];

/* ── La méthode en six étapes (docs/ailiance-methodologie.pdf) ──────────── */
const METHOD = [
  {
    n: 1,
    short: 'Audit',
    t: 'Audit du besoin et des sources de données',
    d: 'Cartographie de vos cas d’usage, inventaire des données disponibles (formats, volumes, qualité, sensibilité). Identification des contraintes réglementaires et techniques.',
    chips: ['interviews métier', 'cartographie données', 'analyse de faisabilité'],
  },
  {
    n: 2,
    short: 'Objectifs',
    t: 'Définition des objectifs — retour d’audit',
    d: 'Restitution structurée de l’audit. Co-définition des objectifs mesurables : métriques de performance attendues, périmètre fonctionnel, critères d’acceptation.',
    chips: ['kpis cibles', 'périmètre validé', 'critères d’acceptation'],
  },
  {
    n: 3,
    short: 'Sélection',
    t: 'Sélection de modèles et performance de réponse',
    d: 'Benchmark de modèles ouverts (Llama, Mistral, Qwen, Gemma…) sur vos données réelles. Évaluation comparative via l’orchestration multi-agents : précision, latence, coût d’inférence.',
    chips: ['benchmark comparatif', 'orchestration agents', 'rapport de performance'],
  },
  {
    n: 4,
    short: 'Fine-tuning',
    t: 'Fine-tuning et entraînement',
    d: 'Entraînement supervisé sur vos données, dans un environnement sécurisé. Techniques adaptées au volume : LoRA, QLoRA, full fine-tuning. Vos données ne quittent jamais votre périmètre.',
    chips: ['lora / qlora', 'environnement isolé', 'données on-premise'],
  },
  {
    n: 5,
    short: 'Itération',
    t: 'Boucle itérative d’évaluation par le client',
    d: 'Sessions d’évaluation structurées avec vos équipes. Chaque itération affine le modèle sur les cas limites identifiés. Vous validez chaque palier avant de passer au suivant.',
    chips: ['tests utilisateurs', 'itérations ciblées', 'validation métier'],
  },
  {
    n: 6,
    short: 'Production',
    t: 'Mise en œuvre et maintenance',
    d: 'Déploiement en production avec l’architecture d’orchestration complète. Monitoring continu, alertes de dérive, ré-entraînement périodique. Votre modèle s’améliore avec l’usage.',
    chips: ['déploiement', 'pipeline agents', 'monitoring continu'],
  },
];

/* ── Pipelines d'orchestration (les deux « zooms » du PDF) ──────────────── */
type Node = { n: string; title: string; sub: string; tone?: string };

const PIPELINE_EVAL: Node[] = [
  { n: '01', title: 'Requête', sub: 'client' },
  {
    n: '02',
    title: 'Agent routage',
    sub: 'analyse la requête, sélectionne le modèle le plus adapté',
    tone: 'tone-accent',
  },
  { n: '03', title: 'Modèle A ou B', sub: 'candidats en compétition sur vos données' },
  {
    n: '04',
    title: 'Agent vérification',
    sub: 'contrôle la cohérence de la réponse',
    tone: 'tone-accent',
  },
  {
    n: '05',
    title: 'Réponse qualifiée',
    sub: 'au-delà d’un test sur modèle isolé',
    tone: 'tone-direct',
  },
];

const PIPELINE_PROD: Node[] = [
  { n: '01', title: 'API client', sub: 'requête entrante' },
  {
    n: '02',
    title: 'Routeur intelligent',
    sub: 'distribue entre modèles spécialisés selon le contexte',
    tone: 'tone-accent',
  },
  {
    n: '03',
    title: 'Modèle spécialisé',
    sub: 'avec agent de fallback pour la continuité de service',
  },
  {
    n: '04',
    title: 'Monitoring qualité',
    sub: 'surveille la qualité, déclenche le ré-entraînement sur dérive',
    tone: 'tone-validator',
  },
  {
    n: '05',
    title: 'Réponse + métriques',
    sub: 'traçabilité de bout en bout',
    tone: 'tone-direct',
  },
];

function Pipeline({ nodes }: { nodes: Node[] }) {
  return (
    <div className="router-flow">
      {nodes.map((node, i) => (
        <div key={node.n}>
          <div className={`router-step${node.tone ? ` ${node.tone}` : ''}`}>
            <div className="num">{node.n}</div>
            <div>
              <div className="title">{node.title}</div>
              <div className="sub">{node.sub}</div>
            </div>
          </div>
          {i < nodes.length - 1 && (
            <div className="router-arrow small">
              <span className="line" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/* ── Chiffres clés ─────────────────────────────────────────────────────── */
const STATS = [
  { big: '6', label: 'étapes structurées' },
  { big: '100 %', label: 'données on-premise' },
  { big: '∞', label: 'itérations jusqu’à validation' },
  { big: 'Apache-2.0', label: 'modèles ouverts uniquement' },
];

function OffrePage() {
  return (
    <div style={{ margin: '0 calc(-1 * var(--pad))' }}>
      {/* Hero */}
      <section className="wrap hero">
        <div>
          <div className="kicker">
            <span className="num">№ 07</span> · offre entreprise · modèles ouverts · données privées
          </div>
          <h1>
            L’IA adaptée à <em>votre</em> métier.
            <br />
            Vos données restent <em>chez vous</em>.
          </h1>
        </div>
        <div>
          <p className="hero-lede">
            Ailiance adapte des modèles d’IA ouverts — génératifs ou non — à vos process. Nous
            structurons et exploitons vos données pour les entraîner, de l’audit initial à la mise
            en production. Déployés on-premise ou dans votre cloud privé.
          </p>
          <div className="hero-meta">
            <div>
              <span>6</span> étapes structurées · <span>100 %</span> de vos données restent
              on-premise
            </div>
            <div>
              modèles ouverts · <span>Llama</span> · <span>Mistral</span> · <span>Qwen</span> ·{' '}
              <span>Gemma</span>
            </div>
            <div>
              <span>LoRA</span> · <span>QLoRA</span> · full fine-tuning · orchestration multi-agents
            </div>
          </div>
          <div className="hero-cta">
            <a
              className="btn accent"
              href="mailto:contact@ailiance.fr?subject=Offre%20entreprise%20Ailiance"
            >
              Discuter de votre cas <ArrowRight />
            </a>
            <Link className="btn ghost" to="/transparency">
              Démarche Qualité IA Act
            </Link>
          </div>
        </div>
      </section>

      {/* L'offre — 4 volets */}
      <section className="wrap block">
        <div className="block-head">
          <h2>
            L’offre,
            <br />
            en quatre volets.
          </h2>
          <p className="lede">
            Vos données restent chez vous. Nos modèles s’adaptent à votre métier. Nous travaillons
            exclusivement avec des <em>modèles ouverts</em>, déployables on-premise ou dans votre
            cloud privé — jamais d’API tierce opaque.
          </p>
        </div>
        <div className="pillars">
          {OFFER.map((p) => (
            <div className="pillar" key={p.num}>
              <span className="num">№ {p.num}</span>
              <h3>{p.t}</h3>
              <p>{p.d}</p>
              <span className="tag">{p.tag}</span>
            </div>
          ))}
        </div>
      </section>

      {/* La méthode — 6 étapes */}
      <section className="wrap block">
        <div className="block-head">
          <h2>
            La méthode,
            <br />
            en six étapes.
          </h2>
          <p className="lede">
            Une démarche structurée, de l’audit initial à la mise en production. Vous validez chaque
            palier avant de passer au suivant — pas de boîte noire, pas d’engagement irréversible.
          </p>
        </div>
        {METHOD.map((s) => (
          <div className="disclosure" key={s.n}>
            <div className="num">
              {s.n}
              <span className="label">{s.short}</span>
            </div>
            <div>
              <h4>{s.t}</h4>
              <p style={{ margin: '0 0 12px', color: 'var(--ink-3)', lineHeight: 1.55 }}>{s.d}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {s.chips.map((c) => (
                  <span className="tag-pill" key={c}>
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </section>

      {/* Zoom orchestration — les deux pipelines */}
      <section className="wrap block">
        <div className="block-head">
          <h2>
            L’orchestration,
            <br />
            au cœur du résultat.
          </h2>
          <p className="lede">
            Un modèle seul ne suffit pas. Une architecture multi-agents — routage, vérification,
            monitoring — révèle le potentiel réel de vos données, dès l’évaluation et jusqu’en
            production.
          </p>
        </div>
        <div className="cta-split" style={{ alignItems: 'start' }}>
          <div>
            <div className="kicker" style={{ marginBottom: 18 }}>
              <span className="num">Zoom 1</span> · orchestration à l’évaluation
            </div>
            <p
              style={{ color: 'var(--ink-3)', fontSize: 14, lineHeight: 1.55, margin: '0 0 18px' }}
            >
              Dès l’évaluation initiale, un agent de routage choisit le modèle le plus adapté et un
              agent de vérification contrôle la cohérence de la réponse. Le résultat dépasse celui
              d’un modèle testé isolément.
            </p>
            <Pipeline nodes={PIPELINE_EVAL} />
          </div>
          <div>
            <div className="kicker" style={{ marginBottom: 18 }}>
              <span className="num">Zoom 2</span> · orchestration en production
            </div>
            <p
              style={{ color: 'var(--ink-3)', fontSize: 14, lineHeight: 1.55, margin: '0 0 18px' }}
            >
              En production, un routeur intelligent distribue les requêtes entre modèles
              spécialisés, un agent de fallback garantit la continuité de service, et un agent de
              monitoring déclenche le ré-entraînement quand la performance dérive.
            </p>
            <Pipeline nodes={PIPELINE_PROD} />
          </div>
        </div>
      </section>

      {/* Chiffres clés */}
      <section className="wrap block" style={{ borderBottom: 'none' }}>
        <div className="summary-grid">
          {STATS.map((s, i) => (
            <div
              key={s.label}
              style={{
                padding: '32px 24px',
                borderRight: i < STATS.length - 1 ? '1px solid var(--rule)' : 'none',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--serif)',
                  fontSize: 'clamp(40px, 5vw, 56px)',
                  lineHeight: 1,
                  letterSpacing: '-0.02em',
                  color: 'var(--accent)',
                }}
              >
                {s.big}
              </div>
              <div
                style={{
                  fontFamily: 'var(--mono)',
                  fontSize: 11,
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  color: 'var(--ink-4)',
                  marginTop: 10,
                }}
              >
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Garantie confidentialité + CTA */}
      <section
        style={{
          background: 'var(--paper-2)',
          padding: '64px var(--pad)',
          marginLeft: 0,
          marginRight: 0,
        }}
      >
        <div className="wrap" style={{ padding: 0 }}>
          <div className="cta-split">
            <h2
              style={{
                fontFamily: 'var(--serif)',
                fontSize: 'clamp(40px, 5vw, 64px)',
                lineHeight: 0.95,
                letterSpacing: '-0.02em',
                fontWeight: 400,
                margin: 0,
              }}
            >
              Confidentialité{' '}
              <em style={{ color: 'var(--accent)', fontStyle: 'italic' }}>garantie</em>.
            </h2>
            <div>
              <p
                style={{ color: 'var(--ink-3)', fontSize: 17, lineHeight: 1.5, margin: '0 0 24px' }}
              >
                Vos données ne quittent jamais votre infrastructure. Nous travaillons exclusivement
                avec des modèles ouverts, déployables on-premise ou dans votre cloud privé. Modèles
                ouverts · données souveraines.
              </p>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <a
                  className="btn accent"
                  href="mailto:contact@ailiance.fr?subject=Offre%20entreprise%20Ailiance"
                >
                  contact@ailiance.fr
                </a>
                <Link className="btn ghost" to="/models">
                  Voir les modèles servis
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function ArrowRight({ size = 14 }: { size?: number }) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ flexShrink: 0 }}
    >
      <path d="M3 8h10M9 4l4 4-4 4" />
    </svg>
  );
}
