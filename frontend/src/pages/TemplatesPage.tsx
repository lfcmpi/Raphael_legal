import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import {
  useTemplatesList,
  useCreateTemplate,
  useUpdateTemplate,
  useDeleteTemplate,
  useUploadTemplateDOCX,
  TemplateInfo,
} from "../hooks/useTemplates";
import { toast } from "../components/Toast";

const CATEGORIAS = [
  { value: "procuracao", label: "Procuracao" },
  { value: "contrato", label: "Contrato" },
  { value: "peticao", label: "Peticao" },
  { value: "custom", label: "Personalizado" },
];

const MATERIAS = [
  "Marcas",
  "Patentes",
  "Franchising",
  "Consumidor",
  "Empresarial",
  "Familia",
  "Civil",
  "Outro",
];

export default function TemplatesPage() {
  const { user } = useAuth();
  const [search, setSearch] = useState("");
  const [categoriaFilter, setCategoriaFilter] = useState("");
  const { data, isLoading } = useTemplatesList({
    search: search || undefined,
    categoria: categoriaFilter || undefined,
  });
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<TemplateInfo | null>(null);

  const canEdit = user?.role === "admin" || user?.role === "manager";

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Modelos</h2>
          <p className="text-sm text-gray-500 mt-1">
            Gerencie os modelos de documentos disponiveis para casos
          </p>
        </div>
        {canEdit && (
          <button
            onClick={() => {
              setEditingTemplate(null);
              setShowForm(true);
            }}
            className="bg-navy-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-navy-600 transition flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Novo Modelo
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <input
          type="text"
          placeholder="Buscar modelos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
        />
        <select
          value={categoriaFilter}
          onChange={(e) => setCategoriaFilter(e.target.value)}
          className="px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
        >
          <option value="">Todas categorias</option>
          {CATEGORIAS.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      {/* Template Form Modal */}
      {showForm && (
        <TemplateFormModal
          template={editingTemplate}
          onClose={() => {
            setShowForm(false);
            setEditingTemplate(null);
          }}
        />
      )}

      {/* Template List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse bg-gray-200 h-24 rounded-xl" />
          ))}
        </div>
      ) : !data?.templates.length ? (
        <div className="text-center py-16 bg-white border border-gray-200 rounded-xl">
          <svg className="mx-auto w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-500">Nenhum modelo encontrado.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.templates.map((t) => (
            <TemplateCard
              key={t.id}
              template={t}
              canEdit={canEdit}
              onEdit={() => {
                setEditingTemplate(t);
                setShowForm(true);
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TemplateCard({
  template,
  canEdit,
  onEdit,
}: {
  template: TemplateInfo;
  canEdit: boolean;
  onEdit: () => void;
}) {
  const deleteTemplate = useDeleteTemplate();
  const uploadDOCX = useUploadTemplateDOCX();

  const CATEGORIA_STYLES: Record<string, string> = {
    procuracao: "bg-blue-100 text-blue-700",
    contrato: "bg-green-100 text-green-700",
    peticao: "bg-purple-100 text-purple-700",
    custom: "bg-gray-100 text-gray-700",
  };

  function handleUploadClick() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".docx";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        uploadDOCX.mutate(
          { id: template.id, file },
          {
            onSuccess: () => toast("Arquivo DOCX enviado.", "success"),
            onError: () => toast("Erro ao enviar arquivo."),
          }
        );
      }
    };
    input.click();
  }

  function handleDownload() {
    const token = localStorage.getItem("token");
    const link = document.createElement("a");
    link.href = `/api/templates/${template.id}/download`;
    // Use fetch to include auth header
    fetch(`/api/templates/${template.id}/download`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        link.href = url;
        link.download = `${template.nome.replace(/ /g, "_")}.docx`;
        link.click();
        URL.revokeObjectURL(url);
      })
      .catch(() => toast("Erro ao baixar arquivo."));
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 transition ${!template.ativo ? "opacity-60" : ""}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-semibold text-gray-900 truncate">
              {template.nome}
            </h3>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${CATEGORIA_STYLES[template.categoria] || CATEGORIA_STYLES.custom}`}>
              {CATEGORIAS.find((c) => c.value === template.categoria)?.label || template.categoria}
            </span>
            {!template.ativo && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600 font-medium">
                Inativo
              </span>
            )}
          </div>
          {template.descricao && (
            <p className="text-sm text-gray-500 line-clamp-2 mb-2">{template.descricao}</p>
          )}
          <div className="flex items-center gap-3 flex-wrap">
            {template.materias_aplicaveis.length > 0 && (
              <div className="flex items-center gap-1 flex-wrap">
                {template.materias_aplicaveis.slice(0, 4).map((m) => (
                  <span key={m} className="text-xs px-1.5 py-0.5 bg-navy-50 text-navy-600 rounded">
                    {m}
                  </span>
                ))}
                {template.materias_aplicaveis.length > 4 && (
                  <span className="text-xs text-gray-400">
                    +{template.materias_aplicaveis.length - 4}
                  </span>
                )}
              </div>
            )}
            {template.caminho_docx && (
              <span className="text-xs text-green-600 flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                DOCX vinculado
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 shrink-0">
          {template.caminho_docx && (
            <button
              onClick={handleDownload}
              className="p-2 text-gray-400 hover:text-navy-600 hover:bg-navy-50 rounded-lg transition"
              title="Baixar DOCX"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>
          )}
          {canEdit && (
            <>
              <button
                onClick={handleUploadClick}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                title="Upload DOCX"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </button>
              <button
                onClick={onEdit}
                className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded-lg transition"
                title="Editar"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                onClick={() => {
                  if (confirm(`Excluir modelo "${template.nome}"?`)) {
                    deleteTemplate.mutate(template.id, {
                      onSuccess: () => toast("Modelo excluido.", "success"),
                      onError: () => toast("Erro ao excluir modelo."),
                    });
                  }
                }}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                title="Excluir"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function TemplateFormModal({
  template,
  onClose,
}: {
  template: TemplateInfo | null;
  onClose: () => void;
}) {
  const createTemplate = useCreateTemplate();
  const updateTemplate = useUpdateTemplate();
  const uploadDOCX = useUploadTemplateDOCX();

  const [nome, setNome] = useState(template?.nome || "");
  const [descricao, setDescricao] = useState(template?.descricao || "");
  const [categoria, setCategoria] = useState(template?.categoria || "custom");
  const [materias, setMaterias] = useState<string[]>(template?.materias_aplicaveis || []);
  const [ativo, setAtivo] = useState(template?.ativo ?? true);
  const [docxFile, setDocxFile] = useState<File | null>(null);

  const isEditing = !!template;

  function toggleMateria(m: string) {
    setMaterias((prev) =>
      prev.includes(m) ? prev.filter((x) => x !== m) : [...prev, m]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nome.trim()) return;

    try {
      if (isEditing) {
        await updateTemplate.mutateAsync({
          id: template.id,
          data: { nome, descricao: descricao || null, categoria, materias_aplicaveis: materias, ativo },
        });
        if (docxFile) {
          await uploadDOCX.mutateAsync({ id: template.id, file: docxFile });
        }
        toast("Modelo atualizado.", "success");
      } else {
        const created = await createTemplate.mutateAsync({
          nome,
          descricao: descricao || undefined,
          categoria,
          materias_aplicaveis: materias,
        });
        if (docxFile) {
          await uploadDOCX.mutateAsync({ id: created.id, file: docxFile });
        }
        toast("Modelo criado.", "success");
      }
      onClose();
    } catch {
      toast("Erro ao salvar modelo.");
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-900">
              {isEditing ? "Editar Modelo" : "Novo Modelo"}
            </h3>
          </div>

          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome *
              </label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
                placeholder="Ex: Peticao Inicial - Consumidor"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descricao
              </label>
              <textarea
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                rows={3}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none resize-y"
                placeholder="Descreva o modelo e quando ele deve ser usado..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categoria
              </label>
              <select
                value={categoria}
                onChange={(e) => setCategoria(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
              >
                {CATEGORIAS.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Materias Aplicaveis
              </label>
              <div className="flex flex-wrap gap-2">
                {MATERIAS.map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => toggleMateria(m)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition ${
                      materias.includes(m)
                        ? "bg-navy-700 text-white border-navy-700"
                        : "bg-white text-gray-600 border-gray-300 hover:border-navy-400"
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Arquivo DOCX
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept=".docx"
                  onChange={(e) => setDocxFile(e.target.files?.[0] || null)}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-navy-50 file:text-navy-700 hover:file:bg-navy-100"
                />
              </div>
              {isEditing && template.caminho_docx && !docxFile && (
                <p className="text-xs text-green-600 mt-1">Arquivo DOCX ja vinculado</p>
              )}
            </div>

            {isEditing && (
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="ativo"
                  checked={ativo}
                  onChange={(e) => setAtivo(e.target.checked)}
                  className="rounded border-gray-300 text-navy-600 focus:ring-navy-500"
                />
                <label htmlFor="ativo" className="text-sm text-gray-700">
                  Modelo ativo
                </label>
              </div>
            )}
          </div>

          <div className="p-6 border-t border-gray-200 flex items-center gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 text-sm text-gray-600 hover:text-gray-800 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={!nome.trim() || createTemplate.isPending || updateTemplate.isPending}
              className="bg-navy-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-navy-600 disabled:opacity-50 transition"
            >
              {createTemplate.isPending || updateTemplate.isPending
                ? "Salvando..."
                : isEditing
                ? "Salvar"
                : "Criar Modelo"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
