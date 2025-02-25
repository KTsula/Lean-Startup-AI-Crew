import streamlit as st
import pandas as pd
import json

def bmc_colors():
    """Define colors for BMC sections"""
    return {
        "key_partners": "#F9DFD9",
        "key_activities": "#F8EFBA",
        "key_resources": "#D4F1DD",
        "value_proposition": "#C5EBFE",
        "customer_relationships": "#FEE2D5",
        "channels": "#E8DAF9",
        "customer_segments": "#D3EAFD",
        "cost_structure": "#EFD8D8",
        "revenue_streams": "#DDEBD3"
    }

def display_bmc(bmc_elements):
    """Display Business Model Canvas as a visual grid"""
    st.write("## Business Model Canvas")
    
    # Create a 3x3 grid for BMC elements
    col1, col2, col3 = st.columns([3, 5, 3])
    
    # Row 1
    with col1:
        st.markdown(f"""
        <div style="background-color: {bmc_colors()['key_partners']}; padding: 10px; border-radius: 5px; height: 200px; overflow-y: auto;">
            <h4>Key Partners</h4>
            <p>{bmc_elements.get('key_partners', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        top_col1, top_col2 = st.columns(2)
        with top_col1:
            st.markdown(f"""
            <div style="background-color: {bmc_colors()['key_activities']}; padding: 10px; border-radius: 5px; height: 95px; overflow-y: auto;">
                <h4>Key Activities</h4>
                <p>{bmc_elements.get('key_activities', 'Not specified')}</p>
            </div>
            """, unsafe_allow_html=True)
        with top_col2:
            st.markdown(f"""
            <div style="background-color: {bmc_colors()['key_resources']}; padding: 10px; border-radius: 5px; height: 95px; overflow-y: auto;">
                <h4>Key Resources</h4>
                <p>{bmc_elements.get('key_resources', 'Not specified')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: {bmc_colors()['value_proposition']}; padding: 10px; border-radius: 5px; height: 95px; margin-top: 10px; overflow-y: auto;">
            <h4>Value Proposition</h4>
            <p>{bmc_elements.get('value_proposition', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        top_col1, top_col2 = st.columns(2)
        with top_col1:
            st.markdown(f"""
            <div style="background-color: {bmc_colors()['customer_relationships']}; padding: 10px; border-radius: 5px; height: 95px; overflow-y: auto;">
                <h4>Customer Relationships</h4>
                <p>{bmc_elements.get('customer_relationships', 'Not specified')}</p>
            </div>
            """, unsafe_allow_html=True)
        with top_col2:
            st.markdown(f"""
            <div style="background-color: {bmc_colors()['channels']}; padding: 10px; border-radius: 5px; height: 95px; overflow-y: auto;">
                <h4>Channels</h4>
                <p>{bmc_elements.get('channels', 'Not specified')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: {bmc_colors()['customer_segments']}; padding: 10px; border-radius: 5px; height: 95px; margin-top: 10px; overflow-y: auto;">
            <h4>Customer Segments</h4>
            <p>{bmc_elements.get('customer_segments', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2 - Bottom row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background-color: {bmc_colors()['cost_structure']}; padding: 10px; border-radius: 5px; height: 100px; margin-top: 10px; overflow-y: auto;">
            <h4>Cost Structure</h4>
            <p>{bmc_elements.get('cost_structure', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: {bmc_colors()['revenue_streams']}; padding: 10px; border-radius: 5px; height: 100px; margin-top: 10px; overflow-y: auto;">
            <h4>Revenue Streams</h4>
            <p>{bmc_elements.get('revenue_streams', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
        
def extract_bmc_from_json(json_str):
    """Extract BMC elements from JSON string"""
    try:
        data = json.loads(json_str)
        return data.get("bmc_elements", {})
    except:
        return {}
        
def interactive_bmc_editor(initial_bmc=None):
    """Interactive Business Model Canvas editor"""
    if initial_bmc is None:
        initial_bmc = {
            "key_partners": "",
            "key_activities": "",
            "key_resources": "",
            "value_proposition": "",
            "customer_relationships": "",
            "channels": "",
            "customer_segments": "",
            "cost_structure": "",
            "revenue_streams": ""
        }
    
    st.write("## Edit Business Model Canvas")
    
    # Create a 3x3 grid for BMC elements
    col1, col2, col3 = st.columns([3, 5, 3])
    
    # Row 1
    with col1:
        key_partners = st.text_area(
            "Key Partners", 
            value=initial_bmc.get("key_partners", ""),
            height=150
        )
    
    with col2:
        top_col1, top_col2 = st.columns(2)
        with top_col1:
            key_activities = st.text_area(
                "Key Activities", 
                value=initial_bmc.get("key_activities", ""),
                height=100
            )
        with top_col2:
            key_resources = st.text_area(
                "Key Resources", 
                value=initial_bmc.get("key_resources", ""),
                height=100
            )
        
        value_proposition = st.text_area(
            "Value Proposition", 
            value=initial_bmc.get("value_proposition", ""),
            height=100
        )
    
    with col3:
        top_col1, top_col2 = st.columns(2)
        with top_col1:
            customer_relationships = st.text_area(
                "Customer Relationships", 
                value=initial_bmc.get("customer_relationships", ""),
                height=100
            )
        with top_col2:
            channels = st.text_area(
                "Channels", 
                value=initial_bmc.get("channels", ""),
                height=100
            )
        
        customer_segments = st.text_area(
            "Customer Segments", 
            value=initial_bmc.get("customer_segments", ""),
            height=100
        )
    
    # Row 2 - Bottom row
    col1, col2 = st.columns(2)
    with col1:
        cost_structure = st.text_area(
            "Cost Structure", 
            value=initial_bmc.get("cost_structure", ""),
            height=100
        )
    
    with col2:
        revenue_streams = st.text_area(
            "Revenue Streams", 
            value=initial_bmc.get("revenue_streams", ""),
            height=100
        )
    
    # Update BMC dictionary
    updated_bmc = {
        "key_partners": key_partners,
        "key_activities": key_activities,
        "key_resources": key_resources,
        "value_proposition": value_proposition,
        "customer_relationships": customer_relationships,
        "channels": channels,
        "customer_segments": customer_segments,
        "cost_structure": cost_structure,
        "revenue_streams": revenue_streams
    }
    
    # Save button
    if st.button("Save Business Model Canvas"):
        st.success("Business Model Canvas saved successfully!")
    
    return updated_bmc