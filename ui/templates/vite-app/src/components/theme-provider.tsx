import { createContext, useContext, useEffect, useState } from "react";

type Theme = "dark" | "light" | "system";
type ColorScheme = "agrospai" | "nature" | "soft-pop" | "twitter";

type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: Theme;
  defaultColorScheme?: ColorScheme;
  storageKey?: string;
  colorSchemeStorageKey?: string;
};

type ThemeProviderState = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  colorScheme: ColorScheme;
  setColorScheme: (scheme: ColorScheme) => void;
};

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
  colorScheme: "agrospai",
  setColorScheme: () => null,
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

const COLOR_SCHEMES: Record<ColorScheme, string> = {
  agrospai: new URL("../styles/agrospai.css", import.meta.url).href,
  nature: new URL("../styles/nature.css", import.meta.url).href,
  "soft-pop": new URL("../styles/soft-pop.css", import.meta.url).href,
  twitter: new URL("../styles/twitter.css", import.meta.url).href,
};

const loadColorSchemeCSS = (scheme: ColorScheme) => {
  const id = "color-scheme-link";
  let link = document.getElementById(id) as HTMLLinkElement | null;

  if (!link) {
    link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    document.head.appendChild(link);
  }

  link.href = COLOR_SCHEMES[scheme];
};

export function ThemeProvider({
  children,
  defaultTheme = "system",
  defaultColorScheme = "agrospai",
  storageKey = "vite-ui-theme",
  colorSchemeStorageKey = "vite-color-scheme",
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  );

  const [colorScheme, setColorScheme] = useState<ColorScheme>(
    () =>
      (localStorage.getItem(colorSchemeStorageKey) as ColorScheme) ||
      defaultColorScheme
  );

  useEffect(() => {
    const root = window.document.documentElement;

    root.classList.remove("light", "dark");

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";

      root.classList.add(systemTheme);
      return;
    }

    root.classList.add(theme);
  }, [theme]);

  useEffect(() => {
    loadColorSchemeCSS(colorScheme);
  }, [colorScheme]);

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme);
      setTheme(theme);
    },
    colorScheme,
    setColorScheme: (scheme: ColorScheme) => {
      localStorage.setItem(colorSchemeStorageKey, scheme);
      setColorScheme(scheme);
    },
  };

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext);

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider");

  return context;
};
