import { useState } from "react";
import { useParams } from "react-router-dom";
import { useCaseDetail, useReprocessCase, useUpdateCase } from "../hooks/useCases";
import { useAuth } from "../hooks/useAuth";
import AlertBanner from "../components/AlertBanner";
import FichaView from "../components/FichaView";
import PanoramaView from "../components/PanoramaView";
import DocumentsList from "../components/DocumentsList";
import ProcessingStatus from "../components/ProcessingStatus";
import { toast } from "../components/Toast";

type Tab = "ficha" | "panorama" | "documentos" | "briefing";

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: caso, isLoading, isError } = useCaseDetail(id || "");
  const reprocess = useReprocessCase();
  const updateCase = useUpdateCase();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>("ficha");
  const [editing, setEditing] = useState(false);

  const canEdit = user?.role === "admin" || user?.role === "manager";

  if (isLoading) {
    return (
      <div className="animate-pulse max-w-4xl mx-auto">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-64 bg-gray-200 rounded" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-16">
        <p className="text-red-600 text-lg mb-2">Erro ao carregar caso.</p>
        <p className="text-gray-500 text-sm">
          Verifique sua conexao e tente recarregar a pagina.
        </p>
      </div>
    );
  }

  if (!caso) {
    return <p className="text-gray-500">Caso nao encontrado.</p>;
  }

  const COMPLEXIDADE_STYLES: Record<string, string> = {
    Simples: "bg-green-100 text-green-700",
    "Medio": "bg-yellow-100 text-yellow-700",
    Complexo: "bg-red-100 text-red-700",
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: "ficha", label: "Ficha do Caso" },
    { key: "panorama", label: "Panorama Estrategico" },
    { key: "documentos", label: "Documentos" },
    { key: "briefing", label: "Briefing Original" },
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 flex-wrap mb-2">
          <h2 className="text-2xl font-bold text-gray-900">
            {caso.caso_id || caso.id.slice(0, 8)}
          </h2>
          {caso.materia && (
            <span className="text-sm px-3 py-1 rounded bg-navy-100 text-navy-700">
              {caso.materia}
            </span>
          )}
          {caso.complexidade && (
            <span
              className={`text-sm px-3 py-1 rounded ${
                COMPLEXIDADE_STYLES[caso.complexidade] || "bg-gray-100"
              }`}
            >
              {caso.complexidade}
            </span>
          )}
          {canEdit && caso.status === "completed" && (
            <button
              onClick={() => setEditing(!editing)}
              className={`ml-auto text-sm px-4 py-1.5 rounded-lg font-medium transition ${
                editing
                  ? "bg-yellow-100 text-yellow-700 border border-yellow-300"
                  : "border border-gray-300 text-gray-600 hover:bg-gray-50"
              }`}
            >
              {editing ? "Modo Edicao" : "Editar"}
            </button>
          )}
        </div>
        <p className="text-sm text-gray-500">
          Criado em {new Date(caso.created_at).toLocaleDateString("pt-BR")}
          {caso.cliente_nome && ` · ${caso.cliente_nome}`}
        </p>
      </div>

      {/* Alert */}
      {caso.alerta_complexo && <AlertBanner message={caso.alerta_complexo} />}

      {/* Processing / Error states */}
      {(caso.status === "processing" || caso.status === "pending") && (
        <ProcessingStatus
          status={caso.status}
          progress={
            caso.status === "processing"
              ? "Processando com Claude AI..."
              : "Aguardando processamento..."
          }
        />
      )}

      {caso.status === "error" && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
          <p className="text-red-800 font-medium mb-2">
            Erro no processamento
          </p>
          <p className="text-red-700 text-sm mb-4">
            {caso.output_completo_md || "Erro desconhecido"}
          </p>
          <button
            onClick={() =>
              reprocess.mutate(caso.id, {
                onSuccess: () => toast("Reprocessamento iniciado.", "success"),
                onError: () => toast("Falha ao reprocessar. Tente novamente."),
              })
            }
            disabled={reprocess.isPending}
            className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700 disabled:opacity-50"
          >
            {reprocess.isPending ? "Reprocessando..." : "Reprocessar"}
          </button>
        </div>
      )}

      {/* Tabs */}
      {caso.status === "completed" && (
        <>
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

          <div className="bg-white border border-gray-200 rounded-xl p-6">
            {activeTab === "ficha" && caso.ficha_json && (
              editing ? (
                <EditableFicha
                  caseId={caso.id}
                  ficha={caso.ficha_json}
                  caseFields={{
                    caso_id: caso.caso_id,
                    materia: caso.materia,
                    complexidade: caso.complexidade,
                    cliente_nome: caso.cliente_nome,
                    resumo: caso.resumo,
                    alerta_complexo: caso.alerta_complexo,
                  }}
                />
              ) : (
                <FichaView ficha={caso.ficha_json} />
              )
            )}
            {activeTab === "ficha" && !caso.ficha_json && (
              <p className="text-gray-500 text-sm">
                Ficha nao disponivel para este caso.
              </p>
            )}

            {activeTab === "panorama" && (
              editing ? (
                <EditableTextArea
                  caseId={caso.id}
                  field="panorama_md"
                  value={caso.panorama_md || ""}
                  label="Panorama Estrategico"
                />
              ) : caso.panorama_md ? (
                <PanoramaView markdown={caso.panorama_md} />
              ) : (
                <p className="text-gray-500 text-sm">
                  Panorama nao disponivel para este caso.
                </p>
              )
            )}

            {activeTab === "documentos" && (
              <DocumentsList documents={caso.documentos} />
            )}

            {activeTab === "briefing" && (
              editing ? (
                <EditableTextArea
                  caseId={caso.id}
                  field="briefing"
                  value={caso.briefing}
                  label="Briefing Original"
                />
              ) : (
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg">
                    {caso.briefing}
                  </pre>
                </div>
              )
            )}
          </div>
        </>
      )}
    </div>
  );
}

function EditableTextArea({
  caseId,
  field,
  value,
  label,
}: {
  caseId: string;
  field: string;
  value: string;
  label: string;
}) {
  const updateCase = useUpdateCase();
  const [text, setText] = useState(value);
  const dirty = text !== value;

  function handleSave() {
    updateCase.mutate(
      { caseId, data: { [field]: text } },
      {
        onSuccess: () => toast(`${label} atualizado.`, "success"),
        onError: () => toast(`Erro ao salvar ${label.toLowerCase()}.`),
      }
    );
  }

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={15}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-navy-500 outline-none resize-y min-h-[200px]"
      />
      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={!dirty || updateCase.isPending}
          className="bg-navy-700 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-navy-600 disabled:opacity-50 transition"
        >
          {updateCase.isPending ? "Salvando..." : "Salvar"}
        </button>
        {dirty && (
          <span className="text-sm text-yellow-600">Alteracoes nao salvas</span>
        )}
      </div>
    </div>
  );
}

function EditableFicha({
  caseId,
  ficha,
  caseFields,
}: {
  caseId: string;
  ficha: Record<string, unknown>;
  caseFields: Record<string, string | null>;
}) {
  const updateCase = useUpdateCase();
  const [fields, setFields] = useState({ ...caseFields });
  const [fichaData, setFichaData] = useState(ficha);
  const [dirty, setDirty] = useState(false);

  const cliente = (fichaData.cliente as Record<string, unknown>) || {};
  const parteContraria =
    (fichaData.parte_contraria as Record<string, unknown>) || null;

  function updateField(key: string, value: string) {
    setFields((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  }

  function updateFichaField(path: string, value: string) {
    setFichaData((prev) => {
      const copy = JSON.parse(JSON.stringify(prev));
      const parts = path.split(".");
      let obj = copy;
      for (let i = 0; i < parts.length - 1; i++) {
        if (!obj[parts[i]]) obj[parts[i]] = {};
        obj = obj[parts[i]];
      }
      obj[parts[parts.length - 1]] = value;
      return copy;
    });
    setDirty(true);
  }

  function handleSave() {
    updateCase.mutate(
      {
        caseId,
        data: {
          ...fields,
          ficha_json: fichaData,
        },
      },
      {
        onSuccess: () => {
          toast("Ficha atualizada.", "success");
          setDirty(false);
        },
        onError: () => toast("Erro ao salvar ficha."),
      }
    );
  }

  return (
    <div className="space-y-6">
      {/* Case fields */}
      <section>
        <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">
          Dados do Caso
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <EditField
            label="ID do Caso"
            value={fields.caso_id || ""}
            onChange={(v) => updateField("caso_id", v)}
          />
          <EditField
            label="Materia"
            value={fields.materia || ""}
            onChange={(v) => updateField("materia", v)}
            type="select"
            options={[
              "Marcas",
              "Patentes",
              "Franchising",
              "Consumidor",
              "Empresarial",
              "Familia",
              "Civil",
              "Outro",
            ]}
          />
          <EditField
            label="Complexidade"
            value={fields.complexidade || ""}
            onChange={(v) => updateField("complexidade", v)}
            type="select"
            options={["Simples", "Medio", "Complexo"]}
          />
          <EditField
            label="Nome do Cliente"
            value={fields.cliente_nome || ""}
            onChange={(v) => updateField("cliente_nome", v)}
          />
          <div className="sm:col-span-2">
            <EditField
              label="Resumo"
              value={fields.resumo || ""}
              onChange={(v) => updateField("resumo", v)}
              multiline
            />
          </div>
          <div className="sm:col-span-2">
            <EditField
              label="Alerta Complexo"
              value={fields.alerta_complexo || ""}
              onChange={(v) => updateField("alerta_complexo", v)}
            />
          </div>
        </div>
      </section>

      {/* Ficha - Cliente */}
      <section>
        <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">
          Dados do Cliente (Ficha)
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <EditField
            label="Nome"
            value={String(cliente.nome ?? "")}
            onChange={(v) => updateFichaField("cliente.nome", v)}
          />
          <EditField
            label="CPF/CNPJ"
            value={String(cliente.cpf_cnpj ?? "")}
            onChange={(v) => updateFichaField("cliente.cpf_cnpj", v)}
          />
          <EditField
            label="Contato"
            value={String(cliente.contato ?? "")}
            onChange={(v) => updateFichaField("cliente.contato", v)}
          />
          <EditField
            label="Endereco"
            value={String(cliente.endereco ?? "")}
            onChange={(v) => updateFichaField("cliente.endereco", v)}
          />
        </div>
      </section>

      {/* Ficha - Parte Contraria */}
      <section>
        <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">
          Parte Contraria (Ficha)
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <EditField
            label="Nome"
            value={String(parteContraria?.nome ?? "")}
            onChange={(v) => updateFichaField("parte_contraria.nome", v)}
          />
          <EditField
            label="CPF/CNPJ"
            value={String(parteContraria?.cpf_cnpj ?? "")}
            onChange={(v) => updateFichaField("parte_contraria.cpf_cnpj", v)}
          />
        </div>
      </section>

      {/* Save button */}
      <div className="flex items-center gap-3 pt-2 border-t">
        <button
          onClick={handleSave}
          disabled={!dirty || updateCase.isPending}
          className="bg-navy-700 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-navy-600 disabled:opacity-50 transition"
        >
          {updateCase.isPending ? "Salvando..." : "Salvar Alteracoes"}
        </button>
        {dirty && (
          <span className="text-sm text-yellow-600">Alteracoes nao salvas</span>
        )}
      </div>
    </div>
  );
}

function EditField({
  label,
  value,
  onChange,
  multiline = false,
  type = "text",
  options = [],
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  multiline?: boolean;
  type?: "text" | "select";
  options?: string[];
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
        {label}
      </label>
      {type === "select" ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
        >
          <option value="">—</option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none resize-y"
        />
      ) : (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
        />
      )}
    </div>
  );
}
