from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os
import streamlit as st

class EvidenceTracker:
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the evidence tracker.
        
        Args:
            storage_path: Optional path to store evidence data. If None, stores in memory only.
        """
        self.evidence_store: Dict[str, Dict[str, Any]] = {}
        self.storage_path = storage_path
        
        # Create storage directory if it doesn't exist
        if self.storage_path:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            if os.path.exists(self.storage_path):
                self._load_evidence()
                
    def _load_evidence(self) -> None:
        """Load evidence from storage file."""
        try:
            with open(self.storage_path, 'r') as f:
                self.evidence_store = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.evidence_store = {}

    def _save_evidence(self) -> None:
        """Save evidence to storage file."""
        if self.storage_path:
            with open(self.storage_path, 'w') as f:
                json.dump(self.evidence_store, f, indent=2)

    def add_evidence(
        self,
        decision_id: str,
        evidence_type: str,
        source: str,
        content: str,
        agent_name: str,
        confidence: int = 3  # 1-5 confidence level
    ) -> None:
        """
        Add a piece of evidence to the store.
        
        Args:
            decision_id: Unique identifier for the decision
            evidence_type: Type of evidence (web, image, document, market_research, customer_interview)
            source: Source of the evidence (URL, file path, interview name)
            content: The actual evidence content
            agent_name: Name of the agent that provided the evidence
            confidence: Confidence level (1-5) in the evidence
        """
        self.evidence_store[decision_id] = {
            'type': evidence_type,
            'source': source,
            'content': content,
            'agent': agent_name,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_evidence()

    def get_evidence(self, decision_id: str) -> Dict[str, Any]:
        """Retrieve evidence for a specific decision."""
        return self.evidence_store.get(decision_id, None)

    def get_all_evidence(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all evidence."""
        return self.evidence_store

    def get_evidence_by_type(self, evidence_type: str) -> List[Dict[str, Any]]:
        """Retrieve all evidence of a specific type."""
        return [
            {"id": decision_id, **evidence}
            for decision_id, evidence in self.evidence_store.items()
            if evidence.get("type") == evidence_type
        ]

    def clear_evidence(self) -> None:
        """Clear all evidence from the store."""
        self.evidence_store.clear()
        self._save_evidence()

def display_evidence(evidence_tracker, filter_type=None):
    """Display evidence in a Streamlit interface."""
    if filter_type:
        evidence = evidence_tracker.get_evidence_by_type(filter_type)
        st.write(f"### Evidence ({filter_type})")
    else:
        evidence = [{"id": k, **v} for k, v in evidence_tracker.get_all_evidence().items()]
        st.write("### All Evidence")
    
    if not evidence:
        st.write("No evidence available.")
        return
    
    for item in evidence:
        with st.expander(f"{item.get('source')} ({item.get('type')})"):
            st.write(f"**Decision ID:** {item.get('id')}")
            st.write(f"**Source:** {item.get('source')}")
            st.write(f"**Type:** {item.get('type')}")
            st.write(f"**Agent:** {item.get('agent')}")
            st.write(f"**Confidence:** {'⭐' * item.get('confidence', 0)}")
            st.write(f"**Timestamp:** {item.get('timestamp')}")
            st.write("**Content:**")
            st.write(item.get('content'))