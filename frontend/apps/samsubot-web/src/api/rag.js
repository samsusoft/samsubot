export async function sendRagQuery(question) {
    const response = await fetch("/api/rag-query", { // proxy to backend
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return data.answer;
}
