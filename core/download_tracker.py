import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from playwright.async_api import Download
    from .tab import Tab

logger = logging.getLogger(__name__)


@dataclass
class DownloadEntry:

    download: "Download"
    tab: "Tab"
    started_at: datetime = field(default_factory=datetime.now)
    finished: bool = False
    output_file: Optional[str] = None
    error: Optional[str] = None

    @property
    def suggested_filename(self) -> str:
        return self.download.suggested_filename

    @property
    def url(self) -> str:
        return self.download.url

    def to_dict(self) -> Dict:
        return {
            "suggested_filename": self.suggested_filename,
            "url": self.url,
            "started_at": self.started_at.isoformat(),
            "finished": self.finished,
            "output_file": self.output_file,
            "error": self.error,
            "tab_id": id(self.tab),
        }


class DownloadTracker:

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self._downloads: List[DownloadEntry] = []
        self._download_tasks: Dict[str, asyncio.Task] = {}

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_downloads(self) -> List[DownloadEntry]:
        return self._downloads.copy()

    def get_active_downloads(self) -> List[DownloadEntry]:
        return [entry for entry in self._downloads if not entry.finished]

    def get_finished_downloads(self) -> List[DownloadEntry]:
        return [entry for entry in self._downloads if entry.finished]

    async def track_download(self, download: "Download", tab: "Tab") -> DownloadEntry:
        entry = DownloadEntry(download=download, tab=tab)
        self._downloads.append(entry)

        task_id = f"download_{id(download)}"
        self._download_tasks[task_id] = asyncio.create_task(
            self._handle_download(entry)
        )

        logger.info(f"Started tracking download: {entry.suggested_filename}")
        return entry

    async def _handle_download(self, entry: DownloadEntry) -> None:
        try:
            filename = self._generate_unique_filename(entry.suggested_filename)
            output_path = self.output_dir / filename

            await entry.download.save_as(str(output_path))

            entry.finished = True
            entry.output_file = str(output_path)

            logger.info(f"Download completed: {filename}")

        except Exception as e:
            entry.finished = True
            entry.error = str(e)
            logger.error(f"Download failed: {entry.suggested_filename} - {e}")

        finally:
            task_id = f"download_{id(entry.download)}"
            self._download_tasks.pop(task_id, None)

    def _generate_unique_filename(self, suggested_filename: str) -> str:
        base_path = self.output_dir / suggested_filename

        if not base_path.exists():
            return suggested_filename

        stem = base_path.stem
        suffix = base_path.suffix
        counter = 1

        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            new_path = self.output_dir / new_filename
            if not new_path.exists():
                return new_filename
            counter += 1

    def get_downloads_markdown(self) -> List[str]:
        if not self._downloads:
            return []

        lines = ["### Downloads"]
        for entry in self._downloads:
            if entry.finished:
                if entry.error:
                    lines.append(
                        f"- Failed to download {entry.suggested_filename}: {entry.error}"
                    )
                else:
                    lines.append(
                        f"- Downloaded file {entry.suggested_filename} to {entry.output_file}"
                    )
            else:
                lines.append(f"- Downloading file {entry.suggested_filename} ...")

        return lines

    async def cleanup(self):
        for task in self._download_tasks.values():
            if not task.done():
                task.cancel()

        if self._download_tasks:
            await asyncio.gather(*self._download_tasks.values(), return_exceptions=True)

        self._download_tasks.clear()
        logger.info("Download tracker cleaned up")
