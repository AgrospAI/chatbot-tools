import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTheme } from "@/components/theme-provider";

type ColorScheme = "agrospai" | "nature" | "soft-pop" | "twitter";

const COLOR_SCHEMES: Array<{
  value: ColorScheme;
  label: string;
  description: string;
}> = [
  {
    value: "agrospai",
    label: "AgrospAI",
    description: "Green agriculture theme",
  },
  { value: "nature", label: "Nature", description: "Earthy nature colors" },
  { value: "soft-pop", label: "Soft Pop", description: "Soft modern colors" },
  { value: "twitter", label: "Twitter", description: "Twitter-inspired blues" },
];

export default function ThemePicker() {
  const { colorScheme, setColorScheme } = useTheme();

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="theme-select" className="text-sm font-medium">
        Theme:
      </label>
      <Select
        value={colorScheme}
        onValueChange={(value) => setColorScheme(value as ColorScheme)}
      >
        <SelectTrigger id="theme-select" className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {COLOR_SCHEMES.map((scheme) => (
            <SelectItem key={scheme.value} value={scheme.value}>
              {scheme.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
