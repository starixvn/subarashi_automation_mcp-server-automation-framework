from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from playwright.async_api import Dialog, FileChooser
    from .tab import Tab


class ModalStateType(str, Enum):
    DIALOG = "dialog"
    FILE_CHOOSER = "fileChooser"


@dataclass
class ModalState(ABC):
    type: ModalStateType
    description: str

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


@dataclass
class DialogModalState(ModalState):
    dialog: "Dialog"

    def __init__(self, dialog: "Dialog", description: str):
        super().__init__(ModalStateType.DIALOG, description)
        self.dialog = dialog

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "description": self.description,
            "dialog_type": self.dialog.type,
            "message": self.dialog.message,
            "default_value": self.dialog.default_value,
        }


@dataclass
class FileChooserModalState(ModalState):
    file_chooser: "FileChooser"

    def __init__(self, file_chooser: "FileChooser", description: str):
        super().__init__(ModalStateType.FILE_CHOOSER, description)
        self.file_chooser = file_chooser

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "description": self.description,
            "multiple": self.file_chooser.is_multiple(),
        }


@dataclass
class ModalStateWithTab:
    modal_state: ModalState
    tab: "Tab"

    @property
    def type(self) -> ModalStateType:
        return self.modal_state.type

    @property
    def description(self) -> str:
        return self.modal_state.description

    def to_dict(self) -> Dict[str, Any]:
        result = self.modal_state.to_dict()
        result["tab_id"] = id(self.tab)
        return result
