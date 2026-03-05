import { useState } from "react";
import { Link } from "react-router-dom";
import { useCasesList } from "../hooks/useCases";
import CaseCard from "../components/CaseCard";
import CaseFilters from "../components/CaseFilters";
import { toast } from "../components/Toast";

export default function DashboardPage() {
  const [search, setSearch] = useState("");
  const [materia, setMateria] = useState("");
  const [complexidade, setComplexidade] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading, isError } = useCasesList({
    search: search || undefined,
    materia: materia || undefined,
    complexidade: complexidade || undefined,
    page,
  });

  const totalPages = data ? Math.ceil(data.total / 20) : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Meus Casos</h2>
        <Link
          to="/cases/new"
          className="bg-navy-700 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-navy-600 transition"
        >
          Novo Caso
        </Link>
      </div>

      <div className="mb-6">
        <CaseFilters
          search={search}
          materia={materia}
          complexidade={complexidade}
          onSearchChange={(v) => {
            setSearch(v);
            setPage(1);
          }}
          onMateriaChange={(v) => {
            setMateria(v);
            setPage(1);
          }}
          onComplexidadeChange={(v) => {
            setComplexidade(v);
            setPage(1);
          }}
        />
      </div>

      {isError ? (
        <div className="text-center py-16">
          <p className="text-red-600 text-lg mb-2">Erro ao carregar casos.</p>
          <p className="text-gray-500 text-sm">
            Verifique sua conexao e tente recarregar a pagina.
          </p>
        </div>
      ) : isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-white border border-gray-200 rounded-xl p-5 animate-pulse"
            >
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-3" />
              <div className="h-5 bg-gray-200 rounded w-2/3 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-1/4 mb-3" />
              <div className="h-3 bg-gray-200 rounded w-full" />
            </div>
          ))}
        </div>
      ) : data && data.cases.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {data.cases.map((caso) => (
              <CaseCard key={caso.id} caso={caso} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 rounded border disabled:opacity-50 text-sm"
              >
                Anterior
              </button>
              <span className="px-3 py-1 text-sm text-gray-600">
                Página {page} de {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 rounded border disabled:opacity-50 text-sm"
              >
                Próxima
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg mb-2">Nenhum caso encontrado.</p>
          <p className="text-sm">
            Clique em{" "}
            <Link to="/cases/new" className="text-navy-600 underline">
              Novo Caso
            </Link>{" "}
            para começar.
          </p>
        </div>
      )}
    </div>
  );
}
