from io import BytesIO
from pypdf import PdfReader


class DocumentParser:

    @staticmethod
    def parse_txt(file):
        content = file.read()

        return content.decode(
            "utf-8",
            errors="ignore"
        )

    @staticmethod
    def parse_pdf(file):
        reader = PdfReader(
            BytesIO(file.read())
        )

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n\n".join(pages)

    @staticmethod
    def parse(file, filename):
        extension = filename.lower().rsplit(".", 1)[-1]

        if extension == "txt":
            return DocumentParser.parse_txt(file)

        if extension == "pdf":
            return DocumentParser.parse_pdf(file)

        raise ValueError(
            "Only PDF and TXT files are supported"
        )