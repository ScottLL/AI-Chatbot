from typing import List
import PyPDF2
import docx2txt
import openai

class DocumentEmbedder:
    def __init__(self, openai_key: str):
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def read_pdf(self, file_path: str) -> str:
        pdf_file_obj = open(file_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page_obj = pdf_reader.pages[page_num]
            text += page_obj.extract_text()
        pdf_file_obj.close()
        return text

    def read_docx(self, file_path: str) -> str:
        return docx2txt.process(file_path)

    def read_txt(self, file_path: str) -> str:
        with open(file_path, 'r') as file:
            return file.read()

    def embed_document(self, text: str) -> List[float]:
        response = openai.Embed.create(model='text-davinci-002', texts=[text])
        return response['embeddings'][0]['vectors'][0]['values']

    def embed_documents(self, file_paths: List[str]) -> List[List[float]]:
        document_embeddings = []
        for file_path in file_paths:
            if file_path.endswith('.pdf'):
                text = self.read_pdf(file_path)
            elif file_path.endswith('.docx'):
                text = self.read_docx(file_path)
            elif file_path.endswith('.txt'):
                text = self.read_txt(file_path)
            else:
                raise ValueError('File format not supported.')
            document_embeddings.append(self.embed_document(text))
        return document_embeddings


if __name__ == "__main__":
    embedder = DocumentEmbedder(openai_key='your_openai_key')
    file_paths = ['chat.pdf', 'chat.docx', 'chat.txt']
    embeddings = embedder.embed_documents(file_paths)
