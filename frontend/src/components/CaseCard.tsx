import { useNavigate } from "react-router-dom";
import type { CaseSummary } from "../hooks/useCases";

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  processing: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "Pendente",
  processing: "Processando",
  completed: "Concluído",
  error: "Erro",
};

const COMPLEXIDADE_STYLES: Record<string, string> = {
  Simples: "bg-green-100 text-green-700",
  "Médio": "bg-yellow-100 text-yellow-700",
  Complexo: "bg-red-100 text-red-700",
};

export default function CaseCard({ caso }: { caso: CaseSummary }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/cases/${caso.id}`)}
      className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-navy-300 transition cursor-pointer"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-mono text-gray-500">
            {caso.caso_id || caso.id.slice(0, 8)}
          </span>
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              STATUS_STYLES[caso.status] || "bg-gray-100 text-gray-700"
            }`}
          >
            {STATUS_LABELS[caso.status] || caso.status}
          </span>
        </div>
        {caso.alerta_complexo && (
          <span className="text-red-600" title={caso.alerta_complexo}>
            🔴
          </span>
        )}
      </div>

      <h3 className="font-medium text-gray-900 mb-1">
        {caso.cliente_nome || "⚠️ Sem nome"}
      </h3>

      <div className="flex items-center gap-2 mb-2 flex-wrap">
        {caso.materia && (
          <span className="text-xs px-2 py-0.5 rounded bg-navy-100 text-navy-700">
            {caso.materia}
          </span>
        )}
        {caso.complexidade && (
          <span
            className={`text-xs px-2 py-0.5 rounded ${
              COMPLEXIDADE_STYLES[caso.complexidade] || "bg-gray-100 text-gray-700"
            }`}
          >
            {caso.complexidade}
          </span>
        )}
      </div>

      {caso.resumo && (
        <p className="text-sm text-gray-600 line-clamp-2">{caso.resumo}</p>
      )}

      <p className="text-xs text-gray-400 mt-3">
        {new Date(caso.created_at).toLocaleDateString("pt-BR")}
      </p>
    </div>
  );
}
