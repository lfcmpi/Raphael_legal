interface FichaViewProps {
  ficha: Record<string, unknown>;
}

function FieldValue({ value, label }: { value: unknown; label: string }) {
  const str = String(value ?? "");
  const isPendente = str.includes("PENDENTE");
  return (
    <div>
      <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide">
        {label}
      </dt>
      <dd
        className={`mt-1 text-sm ${
          isPendente ? "bg-yellow-100 text-yellow-800 px-2 py-1 rounded" : "text-gray-900"
        }`}
      >
        {str || "—"}
      </dd>
    </div>
  );
}

export default function FichaView({ ficha }: FichaViewProps) {
  const cliente = (ficha.cliente as Record<string, unknown>) || {};
  const parteContraria = ficha.parte_contraria as Record<string, unknown> | null;

  return (
    <div className="space-y-6">
      {/* Cliente */}
      <section>
        <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">
          Dados do Cliente
        </h4>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldValue value={cliente.nome} label="Nome" />
          <FieldValue value={cliente.cpf_cnpj} label="CPF/CNPJ" />
          <FieldValue value={cliente.contato} label="Contato" />
          <FieldValue value={cliente.endereco} label="Endereço" />
        </dl>
      </section>

      {/* Parte Contrária */}
      {parteContraria && (
        <section>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">
            Parte Contrária
          </h4>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FieldValue value={parteContraria.nome} label="Nome" />
            <FieldValue value={parteContraria.cpf_cnpj} label="CPF/CNPJ" />
          </dl>
        </section>
      )}

      {/* Info do Caso */}
      <section>
        <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">
          Informações do Caso
        </h4>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldValue value={ficha.materia} label="Matéria" />
          <FieldValue value={ficha.complexidade} label="Complexidade" />
          <div className="sm:col-span-2">
            <FieldValue value={ficha.resumo} label="Resumo" />
          </div>
          <div className="sm:col-span-2">
            <FieldValue
              value={ficha.justificativa_complexidade}
              label="Justificativa da Complexidade"
            />
          </div>
        </dl>
      </section>

      {/* Documentos */}
      {Array.isArray(ficha.documentos_recebidos) &&
        ficha.documentos_recebidos.length > 0 && (
          <section>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">
              Documentos Recebidos
            </h4>
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              {(ficha.documentos_recebidos as string[]).map((d, i) => (
                <li key={i}>{d}</li>
              ))}
            </ul>
          </section>
        )}

      {Array.isArray(ficha.documentos_pendentes) &&
        ficha.documentos_pendentes.length > 0 && (
          <section>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">
              Documentos Pendentes
            </h4>
            <ul className="space-y-1">
              {(ficha.documentos_pendentes as string[]).map((d, i) => (
                <li
                  key={i}
                  className="text-sm bg-yellow-50 text-yellow-800 px-3 py-1 rounded inline-block mr-2 mb-1"
                >
                  ⚠️ {d}
                </li>
              ))}
            </ul>
          </section>
        )}
    </div>
  );
}
