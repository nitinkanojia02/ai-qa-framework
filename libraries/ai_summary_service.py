from pathlib import Path
from typing import Any, Dict

from utils.file_utils import read_text_file
from utils.json_utils import write_json
from utils.logger import get_logger
from utils.time_utils import timestamp_slug

logger = get_logger(__name__)

class AISummaryService:
    def __init__(self, ai_client, artifact_manager) -> None:
        self.ai_client = ai_client
        self.artifact_manager = artifact_manager

    def generate_page_summary(self, page_snapshot) -> Dict[str, Any]:
        logger.info("Generating AI page summary")
        system_prompt = read_text_file("data/prompts/page_summary_prompt.txt")
        user_prompt = self._build_page_summary_prompt(page_snapshot)

        response = self.ai_client.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={
                "type": "page_summary",
                "page_name": page_snapshot.page_analysis.page_name,
            },
        )

        output = {
            "type": "page_summary",
            "page_name": page_snapshot.page_analysis.page_name,
            "title": page_snapshot.page_analysis.title,
            "url": page_snapshot.page_analysis.url,
            "summary": response["response_text"],
            "provider": response["provider"],
            "model": response["model"],
        }

        output_path = self._write_output(
            artifact_type="analytics",
            file_name=f"{page_snapshot.page_analysis.page_name}_{timestamp_slug()}.page_summary.json",
            payload=output,
        )
        output["artifact_path"] = output_path
        return output

    def generate_workflow_summary(self, workflow_graph_dict: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Generating AI workflow summary")
        system_prompt = read_text_file("data/prompts/workflow_summary_prompt.txt")
        user_prompt = self._build_workflow_summary_prompt(workflow_graph_dict)

        response = self.ai_client.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={
                "type": "workflow_summary",
                "application_name": workflow_graph_dict.get("application_name", ""),
            },
        )

        output = {
            "type": "workflow_summary",
            "application_name": workflow_graph_dict.get("application_name", ""),
            "start_url": workflow_graph_dict.get("start_url", ""),
            "summary": response["response_text"],
            "provider": response["provider"],
            "model": response["model"],
        }

        output_path = self._write_output(
            artifact_type="analytics",
            file_name=f"workflow_summary_{timestamp_slug()}.json",
            payload=output,
        )
        output["artifact_path"] = output_path
        return output

    def _build_page_summary_prompt(self, page_snapshot) -> str:
        page_analysis = page_snapshot.page_analysis
        return (
            f"Page Name: {page_analysis.page_name}\n"
            f"Title: {page_analysis.title}\n"
            f"URL: {page_analysis.url}\n"
            f"Buttons Count: {len(page_analysis.buttons)}\n"
            f"Inputs Count: {len(page_analysis.inputs)}\n"
            f"Links Count: {len(page_analysis.links)}\n"
            f"Forms Count: {len(page_analysis.forms)}\n"
            f"Metadata: {page_analysis.metadata}\n"
            f"Sample Buttons: {[button.to_dict() for button in page_analysis.buttons[:5]]}\n"
            f"Sample Inputs: {[item.to_dict() for item in page_analysis.inputs[:5]]}\n"
            f"Sample Links: {[link.to_dict() for link in page_analysis.links[:5]]}\n"
        )

    def _build_workflow_summary_prompt(self, workflow_graph_dict: Dict[str, Any]) -> str:
        steps = workflow_graph_dict.get("steps", [])
        return (
            f"Application Name: {workflow_graph_dict.get('application_name', '')}\n"
            f"Start URL: {workflow_graph_dict.get('start_url', '')}\n"
            f"Workflow Step Count: {len(steps)}\n"
            f"Workflow Steps: {steps[:20]}\n"
        )

    def _write_output(self, artifact_type: str, file_name: str, payload: Dict[str, Any]) -> str:
        output_dir = Path(self.artifact_manager.get_path(artifact_type))
        output_path = output_dir / file_name
        write_json(output_path.as_posix(), payload)
        logger.info("Saved AI summary artifact: %s", output_path)
        return output_path.as_posix()