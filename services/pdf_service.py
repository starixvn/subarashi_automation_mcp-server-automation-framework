from typing import Dict, Any
from .base_service import BaseService, ServiceResult


class PdfService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def save_as_pdf(
        self, filename: str, full_page: bool = False
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            if not filename.endswith(".pdf"):
                filename += ".pdf"

            output_path = self.context.settings.output_dir / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            await tab.page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
            )

            return ServiceResult(
                success=True,
                message=f"PDF saved to {output_path}",
                data={
                    "filename": filename,
                    "output_path": str(output_path),
                    "full_page": full_page,
                    "format": "A4",
                },
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"Failed to save PDF: {str(e)}", error=str(e)
            )
