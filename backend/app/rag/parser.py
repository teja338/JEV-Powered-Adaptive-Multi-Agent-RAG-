import os
import pypdf
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DocumentParser:
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extracts text from PDF file using PyMuPDF / pypdf."""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
            if text.strip():
                return text.strip()
        except Exception as e:
            logger.warning(f"PyMuPDF failed on {file_path}, trying pypdf: {e}")

        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except Exception as e:
            logger.error(f"pypdf failed on {file_path}: {e}")

        return text.strip()

class TextChunker:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Splits text into chunks of character length chunk_size with overlap."""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        current_chunk = []
        current_len = 0

        for word in words:
            current_chunk.append(word)
            current_len += len(word) + 1
            if current_len >= chunk_size:
                chunks.append(" ".join(current_chunk))
                # retain overlap words
                overlap_words = []
                o_len = 0
                for w in reversed(current_chunk):
                    if o_len + len(w) + 1 <= overlap:
                        overlap_words.insert(0, w)
                        o_len += len(w) + 1
                    else:
                        break
                current_chunk = overlap_words
                current_len = sum(len(w) + 1 for w in current_chunk)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
