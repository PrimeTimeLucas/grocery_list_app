import streamlit as st
import requests
from datetime import datetime

BASE_URL = "http://localhost:5000"
SESSION_KEY = "jwt_token"

def main():
    st.title("🛒 Smart Grocery Lister")
    
    # Initialize session state
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'current_list' not in st.session_state:
        st.session_state.current_list = None
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Authentication sidebar
    with st.sidebar:
        st.header("Account")
        if not st.session_state.token:
            auth_tab = st.tabs(["Login", "Register"])
            
            with auth_tab[0]:
                with st.form("Login"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Login"):
                        response = requests.post(
                            f"{BASE_URL}/login",
                            json={"username": username, "password": password}
                        )
                        if response.status_code == 200:
                            st.session_state.token = response.json()["access_token"]
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                            
            with auth_tab[1]:
                with st.form("Register"):
                    new_user = st.text_input("New Username")
                    new_pass = st.text_input("New Password", type="password")
                    if st.form_submit_button("Register"):
                        response = requests.post(
                            f"{BASE_URL}/register",
                            json={"username": new_user, "password": new_pass}
                        )
                        if response.status_code == 201:
                            st.success("Account created! Please login")
                        else:
                            st.error(response.json().get("message", "Registration failed"))
        else:
            st.success(f"Logged in")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

    # Main app functionality
    if st.session_state.token:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        # Create new list
        with st.expander("➕ Create New Grocery List", expanded=not st.session_state.current_list):
            with st.form("new_list"):
                store = st.text_input("Store Name (optional)")
                items = st.text_area("Items (one per line)")
                if st.form_submit_button("Create List"):
                    item_list = [{"name": item.strip()} for item in items.split("\n") if item.strip()]
                    response = requests.post(
                        f"{BASE_URL}/lists",
                        json={"store_name": store, "items": item_list},
                        headers=headers
                    )
                    if response.status_code == 201:
                        st.session_state.current_list = response.json()["id"]
                        st.rerun()
                    else:
                        st.error("Failed to create list")

        # Existing lists
        st.subheader("Your Grocery Lists")
        lists_response = requests.get(f"{BASE_URL}/lists", headers=headers)
        
        if lists_response.status_code == 200:
            lists = lists_response.json()
            
            # List selection
            cols = st.columns([3,1,1])
            selected_list = cols[0].selectbox(
                "Select a list",
                options=lists,
                format_func=lambda x: f"{x['store']} ({x['created_at'][:10]})" if x['store'] else x['created_at'][:10]
            )
            
            # List actions
            if cols[1].button("Open for Shopping"):
                st.session_state.current_list = selected_list["id"]
                st.rerun()
                
            if cols[2].button("Delete", type="secondary"):
                requests.delete(f"{BASE_URL}/lists/{selected_list['id']}", headers=headers)
                st.rerun()

        # Shopping mode
        if st.session_state.current_list:
            st.divider()
            st.subheader("🛍️ Shopping Mode")
            
            # Get list details
            details = requests.get(
                f"{BASE_URL}/lists/{st.session_state.current_list}",
                headers=headers
            ).json()
            
            total = 0
            with st.form("shopping_list"):
                st.markdown(f"**Store:** {details['store'] or 'No store specified'}")
                
                # Item list
                for idx, item in enumerate(details["items"]):
                    cols = st.columns([1,2,1,1])
                    checked = cols[0].checkbox("", key=f"checked_{idx}", value=False)
                    name = cols[1].text_input("Item", value=item["name"], key=f"name_{idx}", disabled=True)
                    price = cols[2].number_input(
                        "Price", 
                        value=float(item["price"]) if item["price"] else 0.0,
                        key=f"price_{idx}",
                        min_value=0.0,
                        step=0.1,
                        format="%.2f"
                    )
                    store = cols[3].text_input("Store", value=item["store"], key=f"store_{idx}")
                    
                    if price > 0 and checked:
                        total += price

                # Total and actions
                st.markdown(f"## Total: €{total:.2f}")
                if st.form_submit_button("💾 Save Changes"):
                    # Update items
                    updated_items = []
                    for idx in range(len(details["items"])):
                        updated_items.append({
                            "name": st.session_state[f"name_{idx}"],
                            "price": st.session_state[f"price_{idx}"],
                            "store": st.session_state[f"store_{idx}"]
                        })
                    
                    response = requests.put(
                        f"{BASE_URL}/lists/{st.session_state.current_list}",
                        json={"items": updated_items},
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.success("List updated!")
                    else:
                        st.error("Failed to save changes")

            if st.button("← Back to Lists"):
                st.session_state.current_list = None
                st.rerun()

if __name__ == "__main__":
    main()
