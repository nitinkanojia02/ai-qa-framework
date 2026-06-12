from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

@dataclass
class PageElement:
    tag: str
    text: str = ""
    element_id: str = ""
    name: str = ""
    role: str = ""
    placeholder: str = ""
    locator_candidates: List[Dict[str, str]] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PageAnalysis:
    url: str
    title: str = ""
    page_name: str = ""
    buttons: List[PageElement] = field(default_factory=list)
    inputs: List[PageElement] = field(default_factory=list)
    links: List[PageElement] = field(default_factory=list)
    forms: List[Dict] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "title": self.title,
            "page_name": self.page_name,
            "buttons": [button.to_dict() for button in self.buttons],
            "inputs": [item.to_dict() for item in self.inputs],
            "links": [link.to_dict() for link in self.links],
            "forms": self.forms,
            "metadata": self.metadata,
        }

@dataclass
class PageSnapshot:
    page_analysis: PageAnalysis
    screenshot_path: Optional[str] = None
    dom_path: Optional[str] = None
    captured_at: str = ""

    def to_dict(self) -> Dict:
        return {
            "page_analysis": self.page_analysis.to_dict(),
            "screenshot_path": self.screenshot_path,
            "dom_path": self.dom_path,
            "captured_at": self.captured_at,
        }