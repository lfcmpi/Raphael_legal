import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";
import { ReactNode } from "react";

interface PanoramaViewProps {
  markdown: string;
}

function highlightVerificar(children: ReactNode): ReactNode {
  if (typeof children === "string") {
    const parts = children.split(/(\[VERIFICAR(?::.*?)?\])/g);
    if (parts.length === 1) return children;
    return parts.map((part, i) => {
      if (/^\[VERIFICAR/.test(part)) {
        return (
          <span
            key={i}
            className="inline-flex items-center gap-0.5 bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded text-[0.8em] font-semibold border border-amber-200"
            title="Citacao legal requer verificacao pelo advogado"
          >
            {part}
          </span>
        );
      }
      return part;
    });
  }
  if (Array.isArray(children)) {
    return children.map((child, i) => (
      <span key={i}>{highlightVerificar(child)}</span>
    ));
  }
  return children;
}

const components: Components = {
  h2: ({ children }) => (
    <h2 className="text-xl font-bold text-navy-800 mt-8 mb-4 pb-2 border-b border-gray-200 first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-lg font-semibold text-navy-700 mt-6 mb-3">
      {children}
    </h3>
  ),
  h4: ({ children }) => (
    <h4 className="text-base font-semibold text-gray-800 mt-4 mb-2">
      {children}
    </h4>
  ),
  p: ({ children }) => (
    <p className="text-gray-700 leading-relaxed mb-3">
      {highlightVerificar(children)}
    </p>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-gray-900">{children}</strong>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-amber-400 bg-amber-50 pl-4 pr-3 py-3 my-4 rounded-r-lg text-sm text-amber-900">
      {children}
    </blockquote>
  ),
  ul: ({ children }) => (
    <ul className="list-disc list-outside ml-5 mb-4 space-y-1.5 text-gray-700">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-outside ml-5 mb-4 space-y-1.5 text-gray-700">
      {children}
    </ol>
  ),
  li: ({ children }) => (
    <li className="leading-relaxed">{highlightVerificar(children)}</li>
  ),
  hr: () => <hr className="my-6 border-gray-200" />,
  table: ({ children }) => (
    <div className="overflow-x-auto my-4 rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-gray-50">{children}</thead>
  ),
  th: ({ children }) => (
    <th className="px-4 py-2.5 text-left font-semibold text-gray-700 whitespace-nowrap">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-4 py-2.5 text-gray-700">
      {highlightVerificar(children)}
    </td>
  ),
  code: ({ children, className }) => {
    if (className) {
      return (
        <code className="block bg-gray-50 rounded-lg p-4 text-sm overflow-x-auto border border-gray-200">
          {children}
        </code>
      );
    }
    return (
      <code className="bg-gray-100 text-navy-700 px-1.5 py-0.5 rounded text-[0.9em] font-mono">
        {children}
      </code>
    );
  },
};

export default function PanoramaView({ markdown }: PanoramaViewProps) {
  // Strip the "## 2. PANORAMA..." header since we already show it as the tab title
  const content = markdown.replace(
    /^##\s*2[\.\s\-—]+.*?PANORAMA.*?\n+/i,
    ""
  );

  return (
    <div className="panorama-view">
      <Markdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </Markdown>
    </div>
  );
}
