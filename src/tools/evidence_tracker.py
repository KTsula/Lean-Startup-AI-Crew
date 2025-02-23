from datetime import datetime
from typing import Dict, Any

class EvidenceTracker:
    def __init__(self):
        self.evidence_store: Dict[str, Dict[str, Any]] = {}

    def add_evidence(
        self,
        decision_id: str,
        evidence_type: str,
        source: str,
        content: str,
        agent_name: str
    ) -> None:
        """
        Add a piece of evidence to the store.
        
        Args:
            decision_id: Unique identifier for the decision
            evidence_type: Type of evidence (web, image, document)
            source: Source of the evidence (URL, file path)
            content: The actual evidence content
            agent_name: Name of the agent that provided the evidence
        """
        self.evidence_store[decision_id] = {
            'type': evidence_type,
            'source': source,
            'content': content,
            'agent': agent_name,
            'timestamp': datetime.now().isoformat()
        }

    def get_evidence(self, decision_id: str) -> Dict[str, Any]:
        """Retrieve evidence for a specific decision."""
        return self.evidence_store.get(decision_id, None)

    def get_all_evidence(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all evidence."""
        return self.evidence_store

    def clear_evidence(self) -> None:
        """Clear all evidence from the store."""
        self.evidence_store.clear()