import { useState, useRef, type FormEvent } from "react";

interface BriefingFormProps {
  onSubmit: (briefing: string, files: File[]) => void;
  loading: boolean;
}

const ACCEPT = ".pdf,.jpg,.jpeg,.png,.txt,.docx,.doc";

export default function BriefingForm({ onSubmit, loading }: BriefingFormProps) {
  const [briefing, setBriefing] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...dropped]);
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!briefing.trim()) return;
    onSubmit(briefing, files);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Briefing do Caso
        </label>
        <textarea
          value={briefing}
          onChange={(e) => setBriefing(e.target.value)}
          placeholder="Descreva o caso do cliente. Pode ser informal, como uma transcrição de áudio..."
          required
          rows={8}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-navy-500 focus:border-navy-500 outline-none resize-y min-h-[200px] text-sm"
        />
      </div>

      {/* Drop zone */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Documentos Anexos (opcional)
        </label>
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-navy-400 hover:bg-navy-50 transition"
        >
          <p className="text-gray-500 text-sm">
            Arraste arquivos aqui ou clique para selecionar
          </p>
          <p className="text-gray-400 text-xs mt-1">
            PDF, imagens, TXT, DOCX (máx. 10MB cada)
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPT}
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((f, i) => (
            <li
              key={i}
              className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-lg text-sm"
            >
              <span className="truncate">{f.name}</span>
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="text-red-500 hover:text-red-700 ml-3 shrink-0"
              >
                Remover
              </button>
            </li>
          ))}
        </ul>
      )}

      <button
        type="submit"
        disabled={loading || !briefing.trim()}
        className="w-full bg-navy-700 text-white py-3 rounded-lg font-medium hover:bg-navy-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? "Enviando..." : "Processar Caso"}
      </button>
    </form>
  );
}
