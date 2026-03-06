import { useState, useEffect } from "react";
import {
  useCaseTemplateSuggestions,
  useCaseTemplates,
  useSelectCaseTemplates,
  TemplateInfo,
  CaseTemplateInfo,
} from "../hooks/useTemplates";
import { toast } from "./Toast";

const CATEGORIA_STYLES: Record<string, string> = {
  procuracao: "bg-blue-100 text-blue-700",
  contrato: "bg-green-100 text-green-700",
  peticao: "bg-purple-100 text-purple-700",
  custom: "bg-gray-100 text-gray-700",
};

export default function TemplateSuggestions({ caseId }: { caseId: string }) {
  const { data: suggestions, isLoading: loadingSuggestions } =
    useCaseTemplateSuggestions(caseId, true);
  const { data: caseTemplates, isLoading: loadingCaseTemplates } =
    useCaseTemplates(caseId);
  const selectTemplates = useSelectCaseTemplates();

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [initialized, setInitialized] = useState(false);

  // Initialize selection from already-selected templates
  useEffect(() => {
    if (!initialized && suggestions && caseTemplates !== undefined) {
      const existing = new Set(
        (caseTemplates || []).map((ct: CaseTemplateInfo) => ct.template_id)
      );
      if (existing.size > 0) {
        setSelectedIds(existing);
      } else if (suggestions.suggested.length > 0) {
        // Pre-select all suggested templates
        setSelectedIds(new Set(suggestions.suggested.map((t) => t.id)));
      }
      setInitialized(true);
    }
  }, [suggestions, caseTemplates, initialized]);

  const hasSaved = (caseTemplates || []).length > 0;

  function toggleTemplate(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function handleSave() {
    selectTemplates.mutate(
      { caseId, templateIds: Array.from(selectedIds) },
      {
        onSuccess: () => toast("Modelos selecionados salvos.", "success"),
        onError: () => toast("Erro ao salvar selecao de modelos."),
      }
    );
  }

  if (loadingSuggestions || loadingCaseTemplates) {
    return (
      <div className="animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="space-y-3">
          <div className="h-16 bg-gray-200 rounded" />
          <div className="h-16 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  const allTemplates = suggestions?.suggested || [];
  if (allTemplates.length === 0 && !hasSaved) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500 text-sm">
          Nenhum modelo disponivel para sugestao.
        </p>
      </div>
    );
  }

  return (
    <div>
      {!hasSaved && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-blue-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-blue-800">
                Modelos sugeridos para este caso
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Com base na materia e briefing do caso, sugerimos os modelos abaixo. Selecione os que deseja utilizar ou adicione outros.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {allTemplates.map((t: TemplateInfo) => (
          <label
            key={t.id}
            className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition ${
              selectedIds.has(t.id)
                ? "border-navy-300 bg-navy-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
          >
            <input
              type="checkbox"
              checked={selectedIds.has(t.id)}
              onChange={() => toggleTemplate(t.id)}
              className="rounded border-gray-300 text-navy-600 focus:ring-navy-500"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-900">{t.nome}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${CATEGORIA_STYLES[t.categoria] || CATEGORIA_STYLES.custom}`}>
                  {t.categoria}
                </span>
              </div>
              {t.descricao && (
                <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{t.descricao}</p>
              )}
            </div>
          </label>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={selectTemplates.isPending}
          className="bg-navy-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-navy-600 disabled:opacity-50 transition"
        >
          {selectTemplates.isPending
            ? "Salvando..."
            : hasSaved
            ? "Atualizar Selecao"
            : "Confirmar Modelos"}
        </button>
        <span className="text-sm text-gray-500">
          {selectedIds.size} modelo{selectedIds.size !== 1 ? "s" : ""} selecionado{selectedIds.size !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Show saved templates info */}
      {hasSaved && caseTemplates && caseTemplates.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Modelos vinculados ao caso
          </h4>
          <div className="space-y-1">
            {caseTemplates.map((ct: CaseTemplateInfo) => (
              <div key={ct.id} className="flex items-center gap-2 text-sm text-gray-700">
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>{ct.template_nome}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${CATEGORIA_STYLES[ct.template_categoria] || CATEGORIA_STYLES.custom}`}>
                  {ct.template_categoria}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
