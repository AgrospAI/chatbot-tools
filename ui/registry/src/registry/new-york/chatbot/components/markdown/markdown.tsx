import { cn } from "@/lib/utils"
import ReactMarkdown from "react-markdown"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import darkStyle from "react-syntax-highlighter/dist/esm/styles/prism/one-dark"
import lightStyle from "react-syntax-highlighter/dist/esm/styles/prism/one-light"
import remarkGfm from "remark-gfm"
import styles from "./markdown.module.css"

interface Props {
  theme?: "light" | "dark"
  children?: string
  className?: string
  references?: Array<string>
}

export default function Markdown({
  theme = "light",
  children,
  className,
  references = [],
}: Props) {
  const hlStyle = theme === "dark" ? darkStyle : lightStyle

  return (
    <div
      className={cn(
        "prose dark:prose-invert flex max-h-fit w-full flex-col",
        styles.markdown,
        className,
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[]}
        urlTransform={uri => uri}
        components={{
          code(props) {
            const { children, className, ...rest } = props
            const match = /language-(\w+)/.exec(className ?? "")
            return match ? (
              <SyntaxHighlighter
                {...rest}
                PreTag="div"
                ref={undefined}
                language={match[1]}
                style={hlStyle}
                customStyle={{
                  margin: 0,
                }}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code {...rest} className={className}>
                {children}
              </code>
            )
          },
          a: ({ href, children }) => {
            if (href?.startsWith("ref:")) {
              const id = parseInt(href.slice(4))
              const url = references[id]

              if (!url) return <span>{children}</span>

              return (
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ref-button"
                >
                  {children}
                </a>
              )
            }

            return <a href={href}>{children}</a>
          },
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
