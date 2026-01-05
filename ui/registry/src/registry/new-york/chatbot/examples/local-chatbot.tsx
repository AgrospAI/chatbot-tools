import LocalChatbot from "@/registry/new-york/chatbot/components/local-chatbot";

const title = "Chatbot Assistant";
const promptSuggestions = [
  "What's the weather like today?",
  "Tell me a joke.",
  "How do I bake a chocolate cake?",
  "Explain quantum computing in simple terms.",
];

export default function Default() {
  return <LocalChatbot strings={{ title, promptSuggestions }} />;
}
