import { Button } from "@/components/ui/button"

interface Props {
  suggestions: string[]
  onClickSuggestion: (prompt: string) => void
}

export default function PromptSuggestions({
  suggestions,
  onClickSuggestion,
}: Props) {
  if (!suggestions.length) return null

  return (
    <div className="flex h-full w-full items-center justify-center">
      <div className="flex flex-wrap items-center justify-center gap-4 py-2">
        {suggestions.map((prompt, index) => (
          <Button
            key={index}
            variant="secondary"
            className="inline-block h-auto max-w-full cursor-pointer rounded-xl px-4 py-2 text-left leading-snug whitespace-normal"
            onClick={() => onClickSuggestion(prompt)}
          >
            {prompt}
          </Button>
        ))}
      </div>
    </div>
  )
}
