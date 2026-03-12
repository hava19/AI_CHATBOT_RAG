class PromptBuilder:
    def build_qa_prompt(self, context: str, question: str):
        return f"Context: {context}\n\nQuestion: {question}\nAnswer:"
