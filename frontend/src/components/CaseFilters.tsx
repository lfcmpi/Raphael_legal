interface CaseFiltersProps {
  search: string;
  materia: string;
  complexidade: string;
  onSearchChange: (v: string) => void;
  onMateriaChange: (v: string) => void;
  onComplexidadeChange: (v: string) => void;
}

const MATERIAS = [
  "Marcas",
  "Patentes",
  "Franchising",
  "Consumidor",
  "Empresarial",
  "Família",
  "Civil",
  "Outro",
];

const COMPLEXIDADES = ["Simples", "Médio", "Complexo"];

export default function CaseFilters({
  search,
  materia,
  complexidade,
  onSearchChange,
  onMateriaChange,
  onComplexidadeChange,
}: CaseFiltersProps) {
  return (
    <div className="flex flex-wrap gap-3">
      <input
        type="text"
        placeholder="Buscar por cliente, caso_id..."
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        className="flex-1 min-w-[200px] px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-navy-500 focus:border-navy-500 outline-none text-sm"
      />

      <select
        value={materia}
        onChange={(e) => onMateriaChange(e.target.value)}
        className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-navy-500 outline-none"
      >
        <option value="">Todas as matérias</option>
        {MATERIAS.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>

      <select
        value={complexidade}
        onChange={(e) => onComplexidadeChange(e.target.value)}
        className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-navy-500 outline-none"
      >
        <option value="">Todas as complexidades</option>
        {COMPLEXIDADES.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>
    </div>
  );
}
