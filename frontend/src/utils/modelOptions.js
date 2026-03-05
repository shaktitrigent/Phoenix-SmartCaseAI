const FALLBACK_MODELS = [
  { id: "gemini-2.5-flash", label: "Gemini 2.5 Flash", available: true },
  { id: "openai-gpt-4.1-mini", label: "OpenAI GPT-4.1 Mini", available: true },
  { id: "claude-3-7-sonnet", label: "Claude 3.7 Sonnet", available: true },
  { id: "openrouter:deepseek/deepseek-chat", label: "OpenRouter - DeepSeek Chat", available: false },
  { id: "openrouter:deepseek/deepseek-coder", label: "OpenRouter - DeepSeek Coder", available: false },
  { id: "openrouter:meta-llama/llama-3-8b-instruct", label: "OpenRouter - Llama 3 8B", available: false },
  { id: "openrouter:meta-llama/llama-3-70b-instruct", label: "OpenRouter - Llama 3 70B", available: false },
  { id: "openrouter:mistralai/mixtral-8x7b-instruct", label: "OpenRouter - Mixtral 8x7B", available: false },
  { id: "openrouter:mistralai/mistral-7b-instruct", label: "OpenRouter - Mistral 7B", available: false },
  { id: "llama-local", label: "Local Llama (GGUF)", available: false },
  { id: "fallback-rule", label: "Rule-based Fallback", available: true },
];

const RECOMMENDATIONS = {
  test_case_generation: {
    title: "Recommended for Test Case Generation *",
    ids: [
      "openrouter:meta-llama/llama-3-70b-instruct",
      "openrouter:mistralai/mixtral-8x7b-instruct",
      "openrouter:deepseek/deepseek-chat",
    ],
  },
  locator_generation: {
    title: "Recommended for Locator Generation *",
    ids: [
      "openrouter:deepseek/deepseek-chat",
      "openrouter:deepseek/deepseek-coder",
      "openrouter:meta-llama/llama-3-70b-instruct",
    ],
  },
  automation_templates: {
    title: "Recommended for Automation Templates *",
    ids: [
      "openrouter:deepseek/deepseek-coder",
      "openrouter:meta-llama/llama-3-70b-instruct",
      "openrouter:mistralai/mixtral-8x7b-instruct",
    ],
  },
};

const withAvailabilityLabel = (model, recommended = false) => {
  const base = model?.available ? model.label : `${model.label} (API key required)`;
  return recommended ? `${base} (Recommended)` : base;
};

export const getModelOptions = (models = []) => {
  return Array.isArray(models) && models.length ? models : FALLBACK_MODELS;
};

export const buildModelSections = (models = [], task = "test_case_generation") => {
  const options = getModelOptions(models);
  const recommendation = RECOMMENDATIONS[task] || RECOMMENDATIONS.test_case_generation;
  const byId = new Map(options.map((model) => [model.id, model]));

  const recommended = recommendation.ids
    .map((id) => byId.get(id))
    .filter(Boolean)
    .map((model) => ({
      ...model,
      displayLabel: withAvailabilityLabel(model, true),
    }));

  const recommendedIds = new Set(recommended.map((model) => model.id));
  const otherCandidates = options
    .filter((model) => !recommendedIds.has(model.id))
    .map((model) => ({
      ...model,
      displayLabel: withAvailabilityLabel(model),
    }));
  const openrouter = otherCandidates.filter(
    (model) => String(model?.provider || "").toLowerCase() === "openrouter" || String(model.id || "").startsWith("openrouter:")
  );
  const others = otherCandidates.filter((model) => !openrouter.some((item) => item.id === model.id));

  return {
    recommendedTitle: recommendation.title,
    recommended,
    openrouter,
    others,
  };
};
