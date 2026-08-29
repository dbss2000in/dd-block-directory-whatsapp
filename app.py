import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import re

st.set_page_config(page_title="DD Block Directory v0.1", page_icon="📍", layout="centered")

# --- CONFIGURATION ---
DIRECTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQm-1lqodJfHqPzBnhDSTIxwnc0HqDHVN0gtR4VF78SyyI9R6kbsfaHbAxJR0qkfWXsdIXAsMMDgFm9/pub?output=csv"

if "total_hits" not in st.session_state:
    st.session_state.total_hits = 0

st.session_state.total_hits += 1

@st.cache_data(ttl=15)
def load_directory():
    return pd.read_csv(DIRECTORY_CSV_URL)

st.title("📍 DD Block New Town Directory")
st.write("Kolkata - 700156 | **Version 0.1**")

tab_choice = st.radio("Navigation Menu", ["📖 Directory & Maps", "📝 Feedback & New Entries", "📊 Usage Analytics"], horizontal=True)
st.divider()

if tab_choice == "📖 Directory & Maps":
    try:
        df = load_directory()
        df.columns = [str(c).strip() for c in df.columns]
        
        name_col = next((col for col in df.columns if 'name' in col.lower()), df.columns[0])
        address_col = next((col for col in df.columns if 'address' in col.lower() or 'street' in col.lower()), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        phone_col = next((col for col in df.columns if 'phone' in col.lower() or 'number' in col.lower()), df.columns[-1])

        search_query = st.text_input("🔍 Search by Name, Plot Number, or Phone", "")
        
        if search_query:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df

        st.write(f"Showing **{len(filtered_df)}** entries")
        st.divider()

        for index, row in filtered_df.iterrows():
            name = row.get(name_col, "N/A")
            address = row.get(address_col, "N/A")
            phone_raw = row.get(phone_col, "N/A")
            
            if pd.isna(name) or str(name).strip() == "" or str(name).lower() == "nan":
                continue
                
            st.markdown(f"👤 **{name}**")
            
            if address and str(address).lower() != "nan":
                addr_text = str(address).strip()
                map_query = f"{addr_text}, DD Block, New Town, Kolkata, West Bengal 700156"
                encoded_address = urllib.parse.quote(map_query)
                map_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
                directions_url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_address}"
                st.markdown(f"📍 **Plot:** [{address}]({map_url}) | 🚗 [Directions]({directions_url})")

            if pd.notna(phone_raw) and str(phone_raw).lower() != "nan":
                phone_list = re.split(r',|/|\band\b', str(phone_raw))
                
                for p_item in phone_list:
                    digits_only = "".join(filter(str.isdigit, p_item))
                    
                    if len(digits_only) >= 10:
                        clean_10 = digits_only[-10:]
                        wa_number = f"91{clean_10}"
                        call_phone = f"+91 {clean_10}"
                        
                        tel_url = f"tel:{digits_only}"
                        wa_chat_url = f"https://wa.me/{wa_number}"
                        wa_call_url = f"https://api.whatsapp.com/send?phone={wa_number}&text=Hello%2C%20calling%20via%20WhatsApp"
                        
                        st.markdown(f"📞 [{call_phone}]({tel_url})  |  💬 [WhatsApp Chat]({wa_chat_url})  |  📞 [WhatsApp Call]({wa_call_url})")
                    else:
                        if p_item.strip():
                            st.markdown(f"📞 {p_item.strip()}")
            else:
                st.markdown("📞 N/A")
                
            st.markdown("---")

    except Exception as e:
        st.error(f"Error loading directory data: {e}")

elif tab_choice == "📝 Feedback & New Entries":
    st.subheader("📝 Request New Entry or Modification")
    st.write("Click the button below to open the secure request form in your browser. It takes less than a minute to submit a new entry or update details!")
    
    # Direct Clean Link Button (Bypasses cookie blocks entirely on mobile phones)
    form_direct_url = "https://docs.google.com/forms/d/e/1FAIpQLSdv4UTrJlLVnxDtsW7rU09bqNG3hWOOhmjMuc6x-nazvtjjjQ/viewform"
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 30px; margin-bottom: 30px;">
        <a href="{form_direct_url}" target="_blank" style="background-color: #0284c7; color: white; padding: 15px 30px; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); display: inline-block;">
            📋 Open Request & Correction Form
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Tip:** Once you submit the form, administration will review and update your details in the main directory shortly.")

elif tab_choice == "📊 Usage Analytics":
    st.subheader("📊 App Engagement & Hit Counter")
    st.write("Real-time usage metrics for Version 0.1:")
    st.metric(label="Total App Hits / Visits", value=st.session_state.total_hits)
    st.info("Hit counts track the total number of times residents have opened or refreshed the application portal.")
