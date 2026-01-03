import LocalChatbot from "@/registry/new-york/chatbot/components/local-chatbot"
import SvgFastragIcon from "../components/icons/FastragIcon"

const title = "Chatbot Assistant"
const promptSuggestions = [
  "What's the weather like today?",
  "Tell me a joke.",
  "How do I bake a chocolate cake?",
  "Explain quantum computing in simple terms.",
]

const icon = <SvgFastragIcon className="size-12" />


export default function Default() {
  return <LocalChatbot strings={{ title, promptSuggestions }} icon={icon} />
}
