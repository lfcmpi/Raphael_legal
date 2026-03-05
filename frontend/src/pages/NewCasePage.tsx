import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCreateCase, useUploadFiles, useCaseStatus } from "../hooks/useCases";
import BriefingForm from "../components/BriefingForm";
import ProcessingStatus from "../components/ProcessingStatus";
import { toast } from "../components/Toast";

function extractErrorMessage(err: unknown): string {
  if (err && typeof err === "object" && "response" in err) {
    const resp = (err as { response?: { data?: { detail?: string } } }).response;
    if (resp?.data?.detail) return resp.data.detail;
  }
  if (err instanceof Error) return err.message;
  return "Erro inesperado. Tente novamente.";
}

export default function NewCasePage() {
  const navigate = useNavigate();
  const createCase = useCreateCase();
  const uploadFiles = useUploadFiles();
  const [caseId, setCaseId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isPolling = !!caseId;
  const statusQuery = useCaseStatus(caseId || "", isPolling);

  // Redirect when completed
  if (statusQuery.data?.status === "completed" && caseId) {
    navigate(`/cases/${caseId}`, { replace: true });
  }

  // Handle processing error from polling
  const processingError =
    statusQuery.data?.status === "error" ? statusQuery.data.progress : null;

  async function handleSubmit(briefing: string, files: File[]) {
    setSubmitting(true);
    setError(null);
    try {
      const newCase = await createCase.mutateAsync(briefing);
      if (files.length > 0) {
        try {
          await uploadFiles.mutateAsync({ caseId: newCase.id, files });
        } catch (uploadErr) {
          const msg = extractErrorMessage(uploadErr);
          toast(`Erro ao enviar arquivos: ${msg}`);
          // Continue — case was created, just files failed
        }
      }
      setCaseId(newCase.id);
    } catch (err) {
      const msg = extractErrorMessage(err);
      setError(msg);
      toast(msg);
      setSubmitting(false);
    }
  }

  function handleReset() {
    setCaseId(null);
    setSubmitting(false);
    setError(null);
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Novo Caso</h2>

      {caseId ? (
        <ProcessingStatus
          status={processingError ? "error" : statusQuery.data?.status || "processing"}
          progress={
            processingError ||
            statusQuery.data?.progress ||
            "Iniciando processamento..."
          }
          onRetry={() => navigate(`/cases/${caseId}`)}
          onBack={handleReset}
          retryLabel="Ver detalhes do caso"
        />
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">
              {error}
            </div>
          )}
          <BriefingForm onSubmit={handleSubmit} loading={submitting} />
        </div>
      )}
    </div>
  );
}
