import LanguageSelect from "@/app/[locale]/settings/_components/language-select"
import ThemePicker from "@/app/[locale]/settings/_components/theme-picker"
import { PageHeader } from "@/components/page-header"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { getExtracted } from "next-intl/server"

export default async function Settings() {
  const t = await getExtracted()

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6 space-y-6">
        <PageHeader
          title={t("Settings")}
          description={t(
            "Manage your preferences and customize your experience",
          )}
        />

        <div className="space-y-6">
          {/* Theme Section */}
          <Card className="border-border bg-card">
            <div className="p-6">
              <div className="mb-4">
                <h2 className="text-xl font-semibold text-card-foreground">
                  {t("Appearance")}
                </h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  {t("Choose how the interface looks and feels")}
                </p>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label
                    htmlFor="theme"
                    className="text-sm font-medium text-foreground"
                  >
                    {t("Theme")}
                  </Label>
                  <ThemePicker />
                </div>
              </div>
            </div>
          </Card>

          {/* Language Section */}
          <Card className="border-border bg-card">
            <div className="p-6">
              <div className="mb-4">
                <h2 className="text-xl font-semibold text-card-foreground">
                  {t("Language & Region")}
                </h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  {t("Select your preferred language for the interface")}
                </p>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label
                    htmlFor="language"
                    className="text-sm font-medium text-foreground"
                  >
                    {t("Display Language")}
                  </Label>
                  <LanguageSelect />
                  <p className="text-xs text-muted-foreground">
                    {t(
                      "This will change the language used throughout the application",
                    )}
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
