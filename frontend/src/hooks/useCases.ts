import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../api/client";

export interface CaseSummary {
  id: string;
  caso_id: string | null;
  status: string;
  materia: string | null;
  complexidade: string | null;
  cliente_nome: string | null;
  resumo: string | null;
  alerta_complexo: string | null;
  created_at: string;
  processed_at: string | null;
}

export interface DocumentInfo {
  id: string;
  tipo: string;
  nome_arquivo: string;
  tamanho: number;
  created_at: string;
}

export interface CaseDetail extends CaseSummary {
  briefing: string;
  ficha_json: Record<string, unknown> | null;
  panorama_md: string | null;
  output_completo_md: string | null;
  documentos: DocumentInfo[];
}

interface CaseListResponse {
  cases: CaseSummary[];
  total: number;
}

interface CaseFilters {
  materia?: string;
  complexidade?: string;
  search?: string;
  page?: number;
}

export function useCasesList(filters: CaseFilters = {}) {
  const params = new URLSearchParams();
  if (filters.materia) params.set("materia", filters.materia);
  if (filters.complexidade) params.set("complexidade", filters.complexidade);
  if (filters.search) params.set("search", filters.search);
  if (filters.page) params.set("page", String(filters.page));

  return useQuery<CaseListResponse>({
    queryKey: ["cases", filters],
    queryFn: () => api.get(`/cases?${params}`).then((r) => r.data),
  });
}

export function useCaseDetail(id: string) {
  return useQuery<CaseDetail>({
    queryKey: ["case", id],
    queryFn: () => api.get(`/cases/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCaseStatus(id: string, enabled: boolean, onCompleted?: () => void) {
  return useQuery<{ status: string; progress: string }>({
    queryKey: ["case-status", id],
    queryFn: async () => {
      const res = await api.get(`/cases/${id}/status`);
      if (res.data.status === "completed" || res.data.status === "error") {
        onCompleted?.();
      }
      return res.data;
    },
    enabled,
    refetchInterval: enabled ? 3000 : false,
  });
}

export function useCreateCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (briefing: string) =>
      api.post("/cases", { briefing }).then((r) => r.data as CaseSummary),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cases"] }),
  });
}

export function useReprocessCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (caseId: string) =>
      api.post(`/cases/${caseId}/process`).then((r) => r.data),
    onSuccess: (_data, caseId) => {
      queryClient.invalidateQueries({ queryKey: ["cases"] });
      queryClient.invalidateQueries({ queryKey: ["case", caseId] });
    },
  });
}

export function useUpdateCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      caseId,
      data,
    }: {
      caseId: string;
      data: Record<string, unknown>;
    }) => api.patch(`/cases/${caseId}`, data).then((r) => r.data as CaseDetail),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["case", variables.caseId] });
      queryClient.invalidateQueries({ queryKey: ["cases"] });
    },
  });
}

export function useUploadFiles() {
  return useMutation({
    mutationFn: ({ caseId, files }: { caseId: string; files: File[] }) => {
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));
      return api.post(`/cases/${caseId}/upload`, formData).then((r) => r.data);
    },
  });
}
