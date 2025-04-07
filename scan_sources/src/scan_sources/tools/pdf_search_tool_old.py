from crewai_tools import BaseTool
import os
# from pypdf import PdfReader # Example: Add PyPDF2 to requirements.txt if using

class PDFSearchTool(BaseTool):
    name: str = "PDF Search Tool"
    description: str = ("Searches for keywords within the text content of a specified PDF file. "
                        "Input must be the path to the PDF file and a list of keywords.")

    def _run(self, file_path: str, keywords: list[str]) -> str:
        """Extracts text from a PDF and searches for keywords."""
        if not os.path.exists(file_path):
            return f"Error: PDF file not found at {file_path}"
        if not file_path.lower().endswith('.pdf'):
            return f"Error: File {file_path} is not a PDF."

        try:
            # --- PDF Parsing Logic --- 
            # This is a placeholder. Replace with actual PDF parsing logic.
            # Example using PyPDF2 (install it and add to requirements.txt):
            # reader = PdfReader(file_path)
            # text_content = ""
            # for page in reader.pages:
            #     text_content += page.extract_text() or ""
            
            # Placeholder text extraction
            print(f"[PDFSearchTool] Simulating text extraction from: {file_path}")
            text_content = "Simulated PDF content mentioning trends and signals. Replace with actual extraction."
            # --------------------------

            findings = []
            text_lower = text_content.lower()
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # In a real implementation, you'd extract relevant snippets around the keyword
                    findings.append(f"Keyword '{keyword}' found in {os.path.basename(file_path)}.")
            
            if not findings:
                return f"No specified keywords found in {os.path.basename(file_path)}."
            
            # Return a summary or concatenated findings
            return "\n".join(findings)

        except Exception as e:
            return f"Error processing PDF file {file_path}: {e}"

# Example Usage (for testing):
if __name__ == '__main__':
    # Create a dummy PDF for testing if needed, or use an existing one
    # For this example, we assume a file exists at 'dummy.pdf'
    # Ensure you have a file named dummy.pdf in the same directory or provide a valid path
    # Create a dummy file if it doesn't exist for the test run
    dummy_path = "dummy.pdf"
    if not os.path.exists(dummy_path):
        with open(dummy_path, "w") as f:
            f.write("This is a dummy PDF file for testing.")
        print(f"Created dummy file: {dummy_path}")

    tool = PDFSearchTool()
    result = tool.run(file_path=dummy_path, keywords=["trends", "dummy"])
    print("\nTool Result:")
    print(result)

    # Clean up dummy file
    # os.remove(dummy_path)
    # print(f"Removed dummy file: {dummy_path}")
