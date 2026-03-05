import Markdown from "react-markdown";

interface PanoramaViewProps {
  markdown: string;
}

export default function PanoramaView({ markdown }: PanoramaViewProps) {
  // Highlight [VERIFICAR] markers
  const processed = markdown.replace(
    /\[VERIFICAR\]/g,
    '<span class="verificar-marker" title="Verificar citação legal">[VERIFICAR]</span>'
  );

  return (
    <div className="prose prose-sm max-w-none">
      <style>{`
        .verificar-marker {
          background-color: #fed7aa;
          color: #9a3412;
          padding: 1px 6px;
          border-radius: 4px;
          font-weight: 600;
          font-size: 0.85em;
        }
      `}</style>
      <Markdown
        components={{
          // Render raw HTML for our VERIFICAR markers
          p: ({ children }) => {
            if (typeof children === "string" && children.includes("[VERIFICAR]")) {
              const html = children.replace(
                /\[VERIFICAR\]/g,
                '<span class="verificar-marker" title="Verificar citação legal">[VERIFICAR]</span>'
              );
              return <p dangerouslySetInnerHTML={{ __html: html }} />;
            }
            return <p>{children}</p>;
          },
        }}
      >
        {markdown}
      </Markdown>
    </div>
  );
}
