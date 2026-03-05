import { useEffect, useState, useCallback, useSyncExternalStore } from "react";

interface ToastItem {
  id: number;
  message: string;
  type: "error" | "success" | "info";
}

let toasts: ToastItem[] = [];
let nextId = 0;
const listeners = new Set<() => void>();

function emit() {
  listeners.forEach((l) => l());
}

export function toast(message: string, type: ToastItem["type"] = "error") {
  const id = nextId++;
  toasts = [...toasts, { id, message, type }];
  emit();
  setTimeout(() => {
    toasts = toasts.filter((t) => t.id !== id);
    emit();
  }, 6000);
}

export function ToastContainer() {
  const items = useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => toasts,
  );

  if (items.length === 0) return null;

  const bgMap = {
    error: "bg-red-600",
    success: "bg-green-600",
    info: "bg-navy-700",
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {items.map((t) => (
        <div
          key={t.id}
          className={`${bgMap[t.type]} text-white px-5 py-3 rounded-lg shadow-lg text-sm animate-[slideIn_0.3s_ease-out]`}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
