interface ProcessingStatusProps {
  status: string;
  progress: string;
  onRetry?: () => void;
  onBack?: () => void;
  retryLabel?: string;
}

const STEPS = [
  { key: 1, label: "Ficha do Caso" },
  { key: 2, label: "Panorama Estrategico" },
  { key: 3, label: "Documentos" },
];

export default function ProcessingStatus({
  status,
  progress,
  onRetry,
  onBack,
  retryLabel = "Tentar novamente",
}: ProcessingStatusProps) {
  const isProcessing = status === "processing";
  const isCompleted = status === "completed";
  const isError = status === "error";

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
      {/* Stepper */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {STEPS.map((step, i) => (
          <div key={step.key} className="flex items-center gap-2">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                isCompleted
                  ? "bg-green-100 text-green-700"
                  : isError
                  ? "bg-red-100 text-red-700"
                  : isProcessing
                  ? "bg-navy-100 text-navy-700 animate-pulse"
                  : "bg-gray-100 text-gray-500"
              }`}
            >
              {isCompleted ? "\u2713" : isError ? "!" : step.key}
            </div>
            <span className="text-sm text-gray-600 hidden sm:inline">
              {step.label}
            </span>
            {i < STEPS.length - 1 && (
              <div className="w-8 h-0.5 bg-gray-200 hidden sm:block" />
            )}
          </div>
        ))}
      </div>

      {/* Status text */}
      <p
        className={`text-lg font-medium ${
          isError ? "text-red-600" : "text-gray-700"
        }`}
      >
        {progress}
      </p>

      {isProcessing && (
        <div className="mt-4">
          <div className="w-48 h-2 bg-gray-200 rounded-full mx-auto overflow-hidden">
            <div className="h-full bg-navy-500 rounded-full animate-[progress_2s_ease-in-out_infinite]" />
          </div>
          <p className="text-sm text-gray-400 mt-3">
            Isso pode levar de 30 a 90 segundos...
          </p>
        </div>
      )}

      {isError && (
        <div className="mt-6 flex items-center justify-center gap-3">
          {onRetry && (
            <button
              onClick={onRetry}
              className="bg-navy-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-navy-600 transition"
            >
              {retryLabel}
            </button>
          )}
          {onBack && (
            <button
              onClick={onBack}
              className="border border-gray-300 text-gray-700 px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-50 transition"
            >
              Voltar
            </button>
          )}
        </div>
      )}
    </div>
  );
}
