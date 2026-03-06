import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../api/client";

export interface TemplateInfo {
  id: string;
  nome: string;
  descricao: string | null;
  categoria: string;
  materias_aplicaveis: string[];
  ativo: boolean;
  caminho_docx: string | null;
  created_at: string;
}

export interface CaseTemplateInfo {
  id: string;
  template_id: string;
  template_nome: string;
  template_categoria: string;
  template_descricao: string | null;
  status: string;
  caminho_gerado: string | null;
  created_at: string;
}

interface TemplateListResponse {
  templates: TemplateInfo[];
  total: number;
}

interface SuggestionResponse {
  suggested: TemplateInfo[];
  already_selected: string[];
}

export function useTemplatesList(filters: { search?: string; categoria?: string; ativo?: boolean } = {}) {
  const params = new URLSearchParams();
  if (filters.search) params.set("search", filters.search);
  if (filters.categoria) params.set("categoria", filters.categoria);
  if (filters.ativo !== undefined) params.set("ativo", String(filters.ativo));

  return useQuery<TemplateListResponse>({
    queryKey: ["templates", filters],
    queryFn: () => api.get(`/templates?${params}`).then((r) => r.data),
  });
}

export function useTemplateDetail(id: string) {
  return useQuery<TemplateInfo>({
    queryKey: ["template", id],
    queryFn: () => api.get(`/templates/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      nome: string;
      descricao?: string;
      categoria?: string;
      materias_aplicaveis?: string[];
    }) => api.post("/templates", data).then((r) => r.data as TemplateInfo),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["templates"] }),
  });
}

export function useUpdateTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Record<string, unknown>;
    }) => api.patch(`/templates/${id}`, data).then((r) => r.data as TemplateInfo),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["templates"] }),
  });
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/templates/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["templates"] }),
  });
}

export function useUploadTemplateDOCX() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) => {
      const formData = new FormData();
      formData.append("file", file);
      return api.post(`/templates/${id}/upload`, formData).then((r) => r.data as TemplateInfo);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["templates"] }),
  });
}

export function useCaseTemplateSuggestions(caseId: string, enabled: boolean) {
  return useQuery<SuggestionResponse>({
    queryKey: ["case-template-suggestions", caseId],
    queryFn: () => api.get(`/cases/${caseId}/templates/suggestions`).then((r) => r.data),
    enabled,
  });
}

export function useCaseTemplates(caseId: string) {
  return useQuery<CaseTemplateInfo[]>({
    queryKey: ["case-templates", caseId],
    queryFn: () => api.get(`/cases/${caseId}/templates`).then((r) => r.data),
    enabled: !!caseId,
  });
}

export function useSelectCaseTemplates() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ caseId, templateIds }: { caseId: string; templateIds: string[] }) =>
      api.post(`/cases/${caseId}/templates`, { template_ids: templateIds }).then((r) => r.data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["case-templates", variables.caseId] });
      queryClient.invalidateQueries({ queryKey: ["case-template-suggestions", variables.caseId] });
    },
  });
}
