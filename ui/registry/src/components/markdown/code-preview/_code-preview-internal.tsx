import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2Icon } from "lucide-react"
import { lazy, Suspense, type ReactNode } from "react"
import type { ComponentType } from "react"

type DemoComponent = ComponentType<Record<string, never>>

type DemoModule = {
  default?: DemoComponent
  [key: string]: unknown
}

interface Props {
  demo: Demo
  preview: ReactNode
  code: ReactNode
}

const modules = import.meta.glob<DemoModule>(
  "../../../registry/new-york/**/*.tsx",
)

export type Demo = keyof typeof componentMap

// Create ALL lazy components up-front
const componentMap: Record<
  string,
  React.LazyExoticComponent<DemoComponent>
> = Object.fromEntries(
  Object.keys(modules).map(path => {
    const demo = path
      .replace("../../../registry/new-york/", "")
      .replace(".tsx", "")

    return [
      demo,
      lazy(async () => {
        const module = await modules[path]()

        const namedExport = Object.values(module).find(
          value => typeof value === "function",
        ) as DemoComponent | undefined

        return {
          default: (module.default ?? namedExport) as DemoComponent,
        }
      }),
    ]
  }),
)

export function CodePreviewInternal({ demo, preview, code }: Props) {
  const Component = componentMap[demo]

  if (!Component) {
    throw new Error(`Component not found: ${demo}`)
  }

  return (
    <Tabs defaultValue="preview" className="not-content">
      <TabsList className="w-full">
        <TabsTrigger value="preview">Preview</TabsTrigger>
        <TabsTrigger value="code">Code</TabsTrigger>
      </TabsList>

      <Card className="no-scrollbar h-[450px] overflow-y-auto rounded-lg bg-transparent p-0">
        <CardContent className="h-full p-0">
          <TabsContent
            value="preview"
            className="flex h-full items-center justify-center p-4"
          >
            <Suspense
              fallback={<Loader2Icon className="size-16 animate-spin" />}
            >
              {preview}
              <Component />
            </Suspense>
          </TabsContent>

          <TabsContent value="code" className="h-full">
            {code}
          </TabsContent>
        </CardContent>
      </Card>
    </Tabs>
  )
}
