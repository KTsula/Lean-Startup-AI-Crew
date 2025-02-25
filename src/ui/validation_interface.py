import streamlit as st
from datetime import datetime
import json
import re

def display_validation_plan(validations):
    """Display validations with guidance for user testing"""
    st.write("## Customer Validation Plan")
    st.write("These are the key assumptions that need validation through customer interviews or testing.")
    
    for i, validation in enumerate(validations, 1):
        # Extract validation details
        validation_item = validation.get("validation", "Validation needed")
        method = validation.get("method", "No method specified")
        
        with st.expander(f"Validation #{i}: {validation_item}"):
            st.write("### What to validate")
            st.write(validation_item)
            
            st.write("### Suggested method")
            st.write(method)
            
            st.write("### Interview questions")
            suggested_questions = generate_suggested_questions(validation_item)
            for q in suggested_questions:
                st.write(f"- {q}")
                
def generate_suggested_questions(validation_item):
    """Generate suggested interview questions based on the validation item"""
    # This is a simple implementation - in a real system, you might use an LLM to generate these
    
    # Default questions that work for most validations
    questions = [
        f"What challenges do you face when it comes to {validation_item.lower()}?",
        f"How do you currently handle or solve {validation_item.lower()}?",
        f"What would an ideal solution look like for you?",
        f"How important is solving this problem for you on a scale of 1-10?",
        f"What would make you try a new solution for this problem?"
    ]
    
    return questions

def human_validation_form(validations):
    """Form for users to input validation results"""
    st.write("## Validation Results Input")
    st.write("After conducting your customer interviews or tests, please input your findings below.")
    
    validation_results = []
    
    for i, validation in enumerate(validations, 1):
        validation_item = validation.get("validation", "Validation needed")
        
        st.write(f"### Validation #{i}: {validation_item}")
        
        # Result dropdown
        result = st.selectbox(
            "Validation result",
            ["Validated", "Partially validated", "Invalidated", "Inconclusive"],
            key=f"result_{i}"
        )
        
        # Confidence level
        confidence = st.slider(
            "Confidence level",
            min_value=1,
            max_value=5,
            value=3,
            key=f"confidence_{i}"
        )
        
        # Evidence collected
        evidence = st.text_area(
            "Evidence collected (What did you learn? Include specific quotes or observations)",
            key=f"evidence_{i}"
        )
        
        # Number of people interviewed
        num_interviewed = st.number_input(
            "Number of people interviewed/tested",
            min_value=0,
            value=0,
            key=f"num_interviewed_{i}"
        )
        
        # Additional notes
        notes = st.text_area(
            "Additional notes or insights",
            key=f"notes_{i}"
        )
        
        validation_results.append({
            "validation_item": validation_item,
            "result": result,
            "confidence": confidence,
            "evidence": evidence,
            "num_interviewed": num_interviewed,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
    
    # File uploader for supporting evidence
    st.write("### Supporting Evidence")
    st.write("Upload any supporting files (interview recordings, survey results, etc.)")
    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
    
    # Submit button
    submit = st.button("Submit Validation Results")
    
    if submit:
        return {
            "validation_results": validation_results,
            "files": [file.name for file in uploaded_files] if uploaded_files else [],
            "submission_time": datetime.now().isoformat()
        }
    
    return None

def generate_recommendations(validation_results):
    """Generate recommendations based on validation results"""
    if not validation_results:
        return []
    
    recommendations = []
    pivot_needed = False
    
    # Check if major pivots are needed
    invalidated_count = sum(1 for r in validation_results 
                           if r.get("result") == "Invalidated" and r.get("confidence", 0) >= 4)
    
    if invalidated_count > len(validation_results) / 2:
        pivot_needed = True
        recommendations.append("⚠️ Major pivot needed: Several key assumptions were invalidated with high confidence.")
    
    # Add specific recommendations for each validation result
    for result in validation_results:
        if result.get("result") == "Invalidated":
            recommendations.append(f"❌ Rethink your approach to: {result.get('validation_item')}")
            
        elif result.get("result") == "Partially validated":
            recommendations.append(f"⚠️ Refine your understanding of: {result.get('validation_item')}")
            
        elif result.get("result") == "Validated" and result.get("confidence", 0) >= 4:
            recommendations.append(f"✅ Continue with your approach to: {result.get('validation_item')}")
            
        elif result.get("result") == "Inconclusive":
            recommendations.append(f"❓ Gather more data about: {result.get('validation_item')}")
    
    # General next steps recommendations
    if pivot_needed:
        recommendations.append("🔄 Consider pivoting your core value proposition based on these findings.")
    else:
        validated_count = sum(1 for r in validation_results if r.get("result") == "Validated")
        if validated_count > len(validation_results) / 2:
            recommendations.append("🚀 You've validated enough assumptions to proceed to the next stage of development.")
        else:
            recommendations.append("🔍 Continue validation with larger sample sizes to confirm initial findings.")
    
    return recommendations