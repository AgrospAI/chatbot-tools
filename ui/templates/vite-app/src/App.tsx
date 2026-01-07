import { RootComponents } from "@/components/examples";
import { ThemeProvider } from "@/components/theme-provider";
import { ModeToggle } from "@/components/mode-toggle";
import ThemePicker from "@/components/theme-picker";
import LocalChatbot from "@/components/chatbot/local-chatbot";

const endpoint = "http://localhost:8000/ask";
const title = "AgrospAI Chatbot";
const promptSuggestions = [
  "What is AgrospAI?",
  "How can I participate in AgrospAI?",
  "What data sources does AgrospAI use?",
  "How does AgrospAI ensure data privacy?",
];
const placeholder = "Ask me anything about AgrospAI...";

export function App() {
  return (
    <ThemeProvider
      defaultTheme="dark"
      storageKey="vite-ui-theme"
      defaultColorScheme="agrospai"
      colorSchemeStorageKey="vite-color-scheme"
    >
      <div className="flex items-center gap-4 p-4">
        <ThemePicker />
        <ModeToggle />
      </div>
      <div className="max-w-6xl mx-auto flex">
        <RootComponents />
      </div>
      <LocalChatbot
        endpoint={endpoint}
        strings={{
          promptSuggestions,
          title,
          placeholder,
        }}
      />
    </ThemeProvider>
  );
}

export default App;
