import { useState, useEffect } from "react";
import {
  useEnvVars,
  useUpdateEnvVars,
  usePrompt,
  useUpdatePrompt,
} from "../hooks/useSettings";
import { toast } from "../components/Toast";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<"env" | "prompt">("env");

  const tabs = [
    { key: "env" as const, label: "Variaveis de Ambiente" },
    { key: "prompt" as const, label: "Prompt do Sistema" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Configuracoes</h2>

      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-3 text-sm font-medium border-b-2 transition ${
                activeTab === tab.key
                  ? "border-navy-600 text-navy-700"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {activeTab === "env" ? <EnvVarsSection /> : <PromptSection />}
    </div>
  );
}

function EnvVarsSection() {
  const { data, isLoading } = useEnvVars();
  const updateEnv = useUpdateEnvVars();
  const [vars, setVars] = useState<Record<string, string>>({});
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (data?.vars) {
      setVars(data.vars);
      setDirty(false);
    }
  }, [data]);

  function handleChange(key: string, value: string) {
    setVars((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  }

  function handleSave() {
    updateEnv.mutate(vars, {
      onSuccess: () => {
        toast("Variaveis salvas. Reinicie o servidor para aplicar.", "success");
        setDirty(false);
      },
      onError: () => toast("Erro ao salvar variaveis."),
    });
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 bg-gray-100 rounded-lg" />
        ))}
      </div>
    );
  }

  const ENV_LABELS: Record<string, string> = {
    ANTHROPIC_API_KEY: "Chave API Anthropic",
    MODEL_NAME: "Modelo Claude",
    OUTPUT_DIR: "Diretorio de Saida",
    TEMPLATES_DIR: "Diretorio de Templates",
    JWT_SECRET: "JWT Secret",
    CORS_ORIGINS: "CORS Origins",
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="space-y-4">
        {Object.entries(vars).map(([key, value]) => (
          <div key={key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {ENV_LABELS[key] || key}
              <span className="text-xs text-gray-400 ml-2 font-normal">
                {key}
              </span>
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-navy-500 outline-none"
            />
          </div>
        ))}
      </div>

      <div className="mt-6 flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={!dirty || updateEnv.isPending}
          className="bg-navy-700 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-navy-600 disabled:opacity-50 transition"
        >
          {updateEnv.isPending ? "Salvando..." : "Salvar"}
        </button>
        {dirty && (
          <span className="text-sm text-yellow-600">
            Alteracoes nao salvas
          </span>
        )}
      </div>
    </div>
  );
}

function PromptSection() {
  const { data, isLoading } = usePrompt();
  const updatePrompt = useUpdatePrompt();
  const [content, setContent] = useState("");
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (data?.content !== undefined) {
      setContent(data.content);
      setDirty(false);
    }
  }, [data]);

  function handleSave() {
    updatePrompt.mutate(content, {
      onSuccess: () => {
        toast("Prompt atualizado.", "success");
        setDirty(false);
      },
      onError: () => toast("Erro ao salvar prompt."),
    });
  }

  if (isLoading) {
    return <div className="h-64 bg-gray-100 rounded-lg animate-pulse" />;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <p className="text-sm text-gray-500 mb-3">
        Este prompt e enviado como instrucao de sistema para o Claude ao
        processar cada caso. Alteracoes sao aplicadas imediatamente.
      </p>
      <textarea
        value={content}
        onChange={(e) => {
          setContent(e.target.value);
          setDirty(true);
        }}
        rows={20}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-navy-500 outline-none resize-y min-h-[300px]"
      />

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={!dirty || updatePrompt.isPending}
          className="bg-navy-700 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-navy-600 disabled:opacity-50 transition"
        >
          {updatePrompt.isPending ? "Salvando..." : "Salvar Prompt"}
        </button>
        {dirty && (
          <span className="text-sm text-yellow-600">
            Alteracoes nao salvas
          </span>
        )}
      </div>
    </div>
  );
}
