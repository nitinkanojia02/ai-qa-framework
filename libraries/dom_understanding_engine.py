from typing import Dict, List

from models.page_models import PageElement
from utils.logger import get_logger

logger = get_logger(__name__)

JS_DOM_EXTRACTION = """
() => {
    function isVisible(el) {
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return style &&
               style.visibility !== 'hidden' &&
               style.display !== 'none' &&
               rect.width > 0 &&
               rect.height > 0;
    }

    function getAttributes(el) {
        const attrs = {};
        for (const attr of el.attributes) {
            attrs[attr.name] = attr.value;
        }
        return attrs;
    }

    function buildCssSelector(el) {
        if (!el || !el.tagName) return '';
        if (el.id) return `#${el.id}`;

        let path = [];
        let current = el;

        while (current && current.nodeType === Node.ELEMENT_NODE && current.tagName.toLowerCase() !== 'html') {
            let selector = current.tagName.toLowerCase();

            if (current.className && typeof current.className === 'string') {
                const classes = current.className.trim().split(/\\s+/).filter(Boolean);
                if (classes.length) {
                    selector += '.' + classes.slice(0, 2).join('.');
                }
            }

            const parent = current.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children).filter(child => child.tagName === current.tagName);
                if (siblings.length > 1) {
                    const index = siblings.indexOf(current) + 1;
                    selector += `:nth-of-type(${index})`;
                }
            }

            path.unshift(selector);
            current = current.parentElement;
        }

        return path.join(' > ');
    }

    function buildXPath(el) {
        if (!el || el.nodeType !== 1) return '';
        if (el.id) return `//*[@id="${el.id}"]`;

        const parts = [];
        let current = el;

        while (current && current.nodeType === 1) {
            let ix = 1;
            let sibling = current.previousSibling;
            while (sibling) {
                if (sibling.nodeType === 1 && sibling.nodeName === current.nodeName) {
                    ix++;
                }
                sibling = sibling.previousSibling;
            }

            const tagName = current.nodeName.toLowerCase();
            const part = `${tagName}[${ix}]`;
            parts.unshift(part);
            current = current.parentNode;
            if (current && current.nodeName && current.nodeName.toLowerCase() === 'html') {
                parts.unshift('html[1]');
                break;
            }
        }

        return '/' + parts.join('/');
    }

    function ownText(el) {
        return Array.from(el.childNodes)
            .filter(node => node.nodeType === Node.TEXT_NODE)
            .map(node => node.textContent.trim())
            .filter(Boolean)
            .join(' ');
    }

    function hasInteractiveAttributes(el) {
        return !!(
            el.onclick ||
            el.getAttribute('onclick') ||
            el.getAttribute('routerlink') ||
            el.getAttribute('href') ||
            el.getAttribute('tabindex') ||
            el.getAttribute('aria-label') ||
            el.getAttribute('role') === 'button' ||
            el.getAttribute('role') === 'link'
        );
    }

    function classifyElement(el) {
        const tag = el.tagName.toLowerCase();
        const role = (el.getAttribute('role') || '').toLowerCase();
        const type = (el.getAttribute('type') || '').toLowerCase();
        const className = (el.className || '').toString().toLowerCase();
        const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();

        if (
            tag === 'button' ||
            role === 'button' ||
            type === 'button' ||
            type === 'submit' ||
            type === 'reset' ||
            tag === 'ion-button' ||
            tag === 'ion-fab-button' ||
            tag === 'ion-menu-button' ||
            tag === 'ion-chip' ||
            tag === 'ion-icon' ||
            className.includes('ion-activatable') ||
            hasInteractiveAttributes(el)
        ) {
            return 'button';
        }

        if (
            tag === 'input' ||
            tag === 'textarea' ||
            tag === 'select' ||
            tag === 'ion-input' ||
            tag === 'ion-select'
        ) {
            return 'input';
        }

        if (
            tag === 'a' ||
            role === 'link' ||
            tag === 'ion-item' ||
            tag === 'ion-card'
        ) {
            return 'link';
        }

        if (tag === 'form') {
            return 'form';
        }

        return 'other';
    }

    const all = Array.from(document.querySelectorAll('*'));
    const elements = [];

    for (const el of all) {
        if (!isVisible(el)) continue;

        const classification = classifyElement(el);
        const text = (el.innerText || '').trim();
        const own = ownText(el);
        const attrs = getAttributes(el);

        if (
            classification === 'other' &&
            !text &&
            !attrs['aria-label'] &&
            !attrs['placeholder'] &&
            !attrs['title'] &&
            !attrs['id'] &&
            !attrs['name']
        ) {
            continue;
        }

        elements.push({
            tag: el.tagName.toLowerCase(),
            classification: classification,
            text: text,
            own_text: own,
            id: el.id || '',
            name: el.getAttribute('name') || '',
            type: el.getAttribute('type') || '',
            role: el.getAttribute('role') || '',
            placeholder: el.getAttribute('placeholder') || '',
            title: el.getAttribute('title') || '',
            href: el.getAttribute('href') || '',
            value: el.getAttribute('value') || '',
            aria_label: el.getAttribute('aria-label') || '',
            data_testid: el.getAttribute('data-testid') || '',
            disabled: !!el.disabled,
            css_selector: buildCssSelector(el),
            xpath: buildXPath(el),
            attributes: attrs
        });
    }

    return {
        title: document.title || '',
        url: window.location.href,
        forms_count: document.forms ? document.forms.length : 0,
        element_count: elements.length,
        elements: elements
    };
}
"""

class DOMUnderstandingEngine:
    def __init__(self) -> None:
        logger.info("DOMUnderstandingEngine initialized")

    def extract_dom_intelligence(self, page) -> Dict:
        logger.info("Extracting DOM intelligence from current page")
        dom_data = page.evaluate(JS_DOM_EXTRACTION)
        logger.info(
            "DOM extraction completed | title=%s | url=%s | elements=%s",
            dom_data.get("title", ""),
            dom_data.get("url", ""),
            dom_data.get("element_count", 0),
        )
        return dom_data

    def classify_elements(self, dom_data: Dict) -> Dict[str, List[PageElement]]:
        classified = {
            "buttons": [],
            "inputs": [],
            "links": [],
            "forms": [],
            "others": [],
        }

        for item in dom_data.get("elements", []):
            element = PageElement(
                tag=item.get("tag", ""),
                text=item.get("text", ""),
                element_id=item.get("id", ""),
                name=item.get("name", ""),
                role=item.get("role", ""),
                placeholder=item.get("placeholder", ""),
                locator_candidates=[
                    {"by": "id", "value": item.get("id", "")},
                    {"by": "name", "value": item.get("name", "")},
                    {"by": "css", "value": item.get("css_selector", "")},
                    {"by": "xpath", "value": item.get("xpath", "")},
                    {"by": "aria-label", "value": item.get("aria_label", "")},
                    {"by": "data-testid", "value": item.get("data_testid", "")},
                ],
                attributes=item.get("attributes", {}),
            )

            classification = item.get("classification", "other")
            if classification == "button":
                classified["buttons"].append(element)
            elif classification == "input":
                classified["inputs"].append(element)
            elif classification == "link":
                classified["links"].append(element)
            elif classification == "form":
                classified["forms"].append(item)
            else:
                classified["others"].append(element)

        logger.info(
            "Classification complete | buttons=%s | inputs=%s | links=%s | forms=%s | others=%s",
            len(classified["buttons"]),
            len(classified["inputs"]),
            len(classified["links"]),
            len(classified["forms"]),
            len(classified["others"]),
        )
        return classified