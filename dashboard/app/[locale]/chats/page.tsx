import { PageHeader } from "@/components/page-header"
import { getExtracted } from "next-intl/server"

export default async function Chats() {
  const t = await getExtracted()
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6 space-y-6">
        <PageHeader
          title={t("Chats")}
          description={t("View and manage your conversations")}
        />
        {/* Chat content will go here */}
      </div>
    </div>
  )
}
