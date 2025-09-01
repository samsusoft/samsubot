import { useState } from "react";
import { sendRagQuery } from "../api/rag";

export default function ChatBox() {
    const [input, setInput] = useState("");
    const [answer, setAnswer] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await sendRagQuery(input);
            setAnswer(res);
        } catch (err) {
            console.error("RAG query failed:", err);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask me something..."
                />
                <button type="submit">Ask</button>
            </form>
            {answer && <p>Answer: {answer}</p>}
        </div>
    );
}
