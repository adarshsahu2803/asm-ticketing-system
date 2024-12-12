# frontend/app.py
import streamlit as st
from api import APIClient

api = APIClient()

st.set_page_config(page_title="ASM Ticketing", layout="wide")

def display_self_service_guide(classification):
    guide = classification.get('self_service_guide', {})
    
    if guide.get('can_self_resolve', False):
        st.success("✨ This issue can be resolved through self-service!")
        
        st.write("#### Steps to Resolve")
        steps = guide.get('steps', [])
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step}")
        
        resources = guide.get('resources', [])
        if resources:
            st.write("#### Helpful Resources")
            for resource in resources:
                st.write(f"- {resource}")
        
        reason = guide.get('reason', '')
        if reason:
            st.write("#### Why Self-Service?")
            st.info(reason)
        
        if st.button("Still Need Help? Create Support Ticket"):
            return True
    else:
        reason = guide.get('reason', '')
        if reason:
            st.write("#### Why This Requires Support?")
            st.info(reason)
        return True
    
    return False

def create_ticket_form():
    with st.form("ticket_form"):
        title = st.text_input("Ticket Title")
        description = st.text_area("Description")
        priority = st.slider("Priority", 1, 5, 3)
        
        submitted = st.form_submit_button("Submit")
        if submitted and title and description:
            try:
                ticket_data = {
                    "title": title,
                    "description": description,
                    "priority": priority
                }
                response = api.create_ticket(ticket_data)
                
                if isinstance(response, dict):
                    classification = response.get('classification', {})
                    
                    if isinstance(classification, dict):
                        if classification.get('is_generic', False):
                            st.write("### Self-Service Guide Available")
                            proceed_with_ticket = display_self_service_guide(classification)
                            
                            if not proceed_with_ticket:
                                st.success("Please try the self-service steps above first!")
                                return True
                        
                        # Show ticket status
                        if response.get("stored_in_db", False):
                            st.success(f"""
                                Ticket created and stored!
                                Category: {classification.get('category', 'Unknown')}
                                ID: {response.get('ticket_id', 'Unknown')}
                            """)
                        else:
                            st.info(f"""
                                Ticket processed but not stored (non-critical category)
                                Category: {classification.get('category', 'Unknown')}
                            """)
                        
                        with st.expander("Classification Details"):
                            st.json(classification)
                    else:
                        st.error("Invalid classification format received")
                else:
                    st.error("Invalid response format received")
                
                return True
            except Exception as e:
                st.error(f"Error processing ticket: {str(e)}")
                return False
    return False

def display_ticket(ticket):
    if isinstance(ticket, dict):
        classification = ticket.get('classification', {})
        if isinstance(classification, dict):
            with st.expander(f"{ticket.get('title', 'Untitled')} - {classification.get('category', 'Unknown')}"):
                st.write(f"Description: {ticket.get('description', 'No description')}")
                st.write(f"Priority: {ticket.get('priority', 'Unknown')}")
                st.write(f"Created: {ticket.get('created_at', 'Unknown')}")
                st.write("Classification Details:")
                st.json(classification)

def main():
    st.title("ASM Ticketing System")
    
    tab1, tab2 = st.tabs(["Submit Request", "View Stored Tickets"])
    
    with tab1:
        st.write("### Submit Support Request")
        st.write("Describe your issue below. If it's a common issue, we'll provide self-service guidance!")
        create_ticket_form()
    
    with tab2:
        st.write("Stored Tickets (Classified/Prioritized only):")
        try:
            tickets = api.list_tickets()
            if tickets:
                for ticket in tickets:
                    display_ticket(ticket)
            else:
                st.info("No stored tickets found")
        except Exception as e:
            st.error(f"Error loading tickets: {str(e)}")

if __name__ == "__main__":
    main()