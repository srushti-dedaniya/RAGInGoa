export const API_PREFIX = "/api";

export const DEMO_QUERY = "What is the best time to visit Palolem in Goa?";

export const PIPELINE_STAGES = [
  { id: "stt", label: "STT", icon: "mic", description: "Speech to text" },
  { id: "retrieval", label: "VECTOR SEARCH", icon: "database", description: "Embed + retrieve" },
  { id: "rerank", label: "RERANK", icon: "swap_vert", description: "Order by relevance" },
  { id: "generation", label: "GENERATION", icon: "auto_awesome", description: "Grounded answer" },
  { id: "guardrails", label: "GUARDRAILS", icon: "verified_user", description: "Safety + grounding" },
];

export const GUARDRAIL_NAMES = [
  { id: "safety", label: "Safety", icon: "shield" },
  { id: "relevance", label: "Relevance", icon: "target" },
  { id: "grounding", label: "Grounding", icon: "anchor" },
  { id: "refusal", label: "Refusal", icon: "block" },
];

export const DEMO_RESULT = {
  query: "What is the best time to visit Palolem in Goa?",
  answer:
    "Based on the retrieved Goa context, the best time to visit Palolem is between November and February, when the post-monsoon landscape is lush and the sea is relatively calm and swimmable. Palolem is a crescent-shaped bay in South Goa known for calm, clean waters, and Agonda nearby offers a quieter alternative. [Source: Palolem Beach Guide] [Source: Agonda Slow Travel]",
  sources: [
    {
      text: "The best time to visit Palolem is between November and February, when the post-monsoon landscape is lush and the sea is relatively calm and swimmable.",
      chunk_id: "doc-0001-c0",
      metadata: { source: "sample-goa-corpus", title: "Palolem Beach Guide", topic: "beaches" },
      score: 0.3317,
      score_type: "cosine",
    },
    {
      text: "For a quiet Goa, choose Agonda over Palolem: a long unspoilt beach, fewer shacks, and one of the region's few turtle-nesting stretches.",
      chunk_id: "doc-0007-c0",
      metadata: { source: "sample-goa-corpus", title: "Agonda Slow Travel", topic: "beaches" },
      score: 0.1684,
      score_type: "cosine",
    },
    {
      text: "Dudhsagar Falls is a four-tiered waterfall among the tallest in India, located on the Mandovi river about 60 km from Panaji.",
      chunk_id: "doc-0003-c0",
      metadata: { source: "sample-goa-corpus", title: "Dudhsagar Waterfalls", topic: "travel" },
      score: 0.2064,
      score_type: "cosine",
    },
  ],
  confidence: 0.818,
  guardrails: {
    passed: true,
    checks: [
      { name: "safety", passed: true, reason: "no unsafe patterns detected", score: 1.0 },
      { name: "relevance", passed: true, reason: "mean cross-similarity 0.331", score: 0.331 },
      { name: "grounding", passed: true, reason: "answer cites 2 source(s)", score: 0.67 },
      { name: "refusal", passed: true, reason: "no injection patterns detected", score: 1.0 },
    ],
  },
  latency_breakdown: {
    stt: 0.0,
    retrieval: 1.01,
    generation: 0.06,
    guardrails: 1.61,
    total: 2.7,
  },
  engine: {
    stt: "dev",
    llm: "dev",
    vector_db: "dev/hashing-384",
    embedding: "hashing-384",
  },
};

export const DEMO_BENCHMARK = {
  strategy: "sentence",
  top_k: 4,
  queries: 5,
  total_avg_ms: 2.1,
  latency: {
    embed: { avg_ms: 0.4, p50_ms: 0.3, p95_ms: 0.8, p99_ms: 1.0, count: 25 },
    retrieve: { avg_ms: 1.1, p50_ms: 1.0, p95_ms: 1.8, p99_ms: 2.1, count: 25 },
    generate: { avg_ms: 0.6, p50_ms: 0.6, p95_ms: 0.9, p99_ms: 1.0, count: 25 },
  },
  index_size: 18,
};

export const DEMO_HEALTH = {
  service: "RAGInGoa",
  status: "ONLINE",
  version: "1.0.0",
  uptime_seconds: 421.2,
  routers: { stt: "dev", llm: "dev", vector_db: "dev" },
  index_size: 18,
  ready: true,
};
