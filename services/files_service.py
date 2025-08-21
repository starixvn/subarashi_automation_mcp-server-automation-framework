from typing import List
from .base_service import BaseService, ServiceResult


class FilesService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def upload_files(self, file_paths: List[str]) -> ServiceResult:
        try:
            file_chooser_state = None
            for state in self.context.modal_states():
                if state.type.value == "fileChooser":
                    file_chooser_state = state
                    break

            if not file_chooser_state:
                return ServiceResult(
                    success=False,
                    message="No file chooser visible",
                    error="No file chooser modal state found",
                )

            await file_chooser_state.file_chooser.set_files(file_paths)

            self.context.clear_modal_state(file_chooser_state)

            return ServiceResult(
                success=True,
                message=f"Successfully uploaded files: {file_paths}",
                data={"uploaded_files": file_paths, "file_count": len(file_paths)},
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"Failed to upload files: {str(e)}", error=str(e)
            )
