"use client";
import { ComponentExample } from "@/components/component-example";
import LocalChatbot from "@/components/chatbot/local-chatbot";

export default function Page() {
    return (
        <>
            <LocalChatbot />
            <ComponentExample />;
        </>
    );
}
