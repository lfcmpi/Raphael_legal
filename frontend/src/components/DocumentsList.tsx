import type { DocumentInfo } from "../hooks/useCases";

interface DocumentsListProps {
  documents: DocumentInfo[];
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const ICONS: Record<string, string> = {
  docx: "📄",
  doc: "📄",
  pdf: "📕",
  jpg: "🖼️",
  jpeg: "🖼️",
  png: "🖼️",
  txt: "📝",
  json: "📋",
  md: "📝",
};

function getIcon(filename: string): string {
  const ext = filename.split(".").pop()?.toLowerCase() || "";
  return ICONS[ext] || "📎";
}

export default function DocumentsList({ documents }: DocumentsListProps) {
  const generated = documents.filter((d) => d.tipo !== "upload");
  const uploaded = documents.filter((d) => d.tipo === "upload");

  function handleDownload(doc: DocumentInfo) {
    const token = localStorage.getItem("token");
    const url = `/api/documents/${doc.id}/download`;
    const link = document.createElement("a");
    // Use fetch to handle auth
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        link.href = URL.createObjectURL(blob);
        link.download = doc.nome_arquivo;
        link.click();
        URL.revokeObjectURL(link.href);
      });
  }

  function renderSection(title: string, docs: DocumentInfo[]) {
    if (docs.length === 0) return null;
    return (
      <section className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">{title}</h4>
        <ul className="space-y-2">
          {docs.map((doc) => (
            <li
              key={doc.id}
              className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="text-lg shrink-0">
                  {getIcon(doc.nome_arquivo)}
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {doc.nome_arquivo}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatSize(doc.tamanho)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDownload(doc)}
                className="text-navy-600 hover:text-navy-800 text-sm font-medium shrink-0 ml-3"
              >
                Download
              </button>
            </li>
          ))}
        </ul>
      </section>
    );
  }

  if (documents.length === 0) {
    return <p className="text-sm text-gray-500">Nenhum documento disponível.</p>;
  }

  return (
    <div>
      {renderSection("Documentos Gerados", generated)}
      {renderSection("Documentos Enviados", uploaded)}
    </div>
  );
}
