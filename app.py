import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import requests
import re

st.set_page_config(page_title="DD Block Directory v0.1", page_icon="📍", layout="centered")

# --- CONFIGURATION ---
DIRECTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQm-1lqodJfHqPzBnhDSTIxwnc0HqDHVN0gtR4VF78SyyI9R6kbsfaHbAxJR0qkfWXsdIXAsMMDgFm9/pub?output=csv"
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdv4UTrJlLVnxDtsW7rU09bqNG3hWOOhmjMuc6x-nazvtjjjQ/viewform"
VISIT_LOG_CSV = "https://docs.google.com/spreadsheets/d/1Jhe-9MkS_vPmGG_3fMCNuXdKaA5-OECR0h8mVOl4ajw/gviz/tq?tqx=out:csv&sheet=VisitLogs"
VISIT_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzT_H5mES8LI1YEN_inOfC2BAREy48RlTaakfljClvP68O3EBbL5Flhpc6dxLgHRcwUfw/exec"

# Silent background hit logger (ensures every unique session logs 1 visit)
if "logged_visit" not in st.session_state:
    st.session_state.logged_visit = True
    try:
        requests.get(VISIT_WEBHOOK_URL, timeout=2)
    except:
        pass

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

        # --- TRADITIONAL BENGAL-DECORATED INTRODUCTORY CARD ---
        st.markdown("""
            <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding: 18px; border-radius: 12px; border-left: 6px solid #e65100; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <h4 style="color: #bf360c; margin: 0 0 5px 0; font-family: sans-serif;">🪔 এসো মিলি DD ব্লকে 🪔</h4>
                <p style="margin: 0; color: #5d4037; font-size: 14px;">স্বাগত জানাই আমাদের নিউ টাউন DD ব্লকের ডিজিটাল ডিরেক্টরিতে। একসাথে পথ চলার এক নতুন প্রয়াস।</p>
            </div>
        """, unsafe_allow_html=True)

        # --- BIG, BOLD, CAPITALIZED SEARCH SECTION ---
        st.markdown(
            "<h3 style='color: #2c3e50; font-weight: bold; font-size: 18px; margin-bottom: 2px;'>🔍 SEARCH DIRECTORY</h3>", 
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color: #666; font-size: 13px; margin-bottom: 8px;'>Search easily by Name, Plot Number (e.g., DD-142), or Phone digits.</p>", 
            unsafe_allow_html=True
        )
        
        search_query = st.text_input(
            "Search Input", 
            label_visibility="collapsed",
            placeholder="Type name, plot, or phone..."
        )
        
        if search_query:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df

        st.write(f"Showing **{len(filtered_df)}** matching resident cards")
        st.divider()

        # --- INDIVIDUAL RESIDENT CARD DECK ---
        for index, row in filtered_df.iterrows():
            name = row.get(name_col, "N/A")
            address = row.get(address_col, "N/A")
            phone_raw = row.get(phone_col, "N/A")
            
            if pd.isna(name) or str(name).strip() == "" or str(name).lower() == "nan":
                continue
                
            with st.container(border=True):
                st.markdown(f"👤 **{name}**")
                
                if address and str(address).lower() != "nan":
                    addr_text = str(address).strip()
                    map_query = f"{addr_text}, DD Block, New Town, Kolkata, West Bengal 700156"
                    encoded_address = urllib.parse.quote(map_query)
                    map_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
                    directions_url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_address}"
                    st.markdown(f"📍 **Plot:** [{address}]({map_url}) &nbsp;|&nbsp; 🚗 [Directions]({directions_url})")

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
                            
                            st.markdown(f"📞 [{call_phone}]({tel_url}) &nbsp;|&nbsp; 💬 [WhatsApp Chat]({wa_chat_url}) &nbsp;|&nbsp; 📞 [WhatsApp Call]({wa_call_url})")
                        else:
                            if p_item.strip():
                                st.markdown(f"📞 {p_item.strip()}")
                else:
                    st.markdown("📞 N/A")

    except Exception as e:
        st.error(f"Error loading directory data: {e}")

elif tab_choice == "📝 Feedback & New Entries":
    st.subheader("📝 Request New Entry or Modification")
    st.write("Click the button below to open the secure request form in your browser. It takes less than a minute to submit a new entry or update details!")
    
    st.link_button("📋 Open Request & Correction Form", GOOGLE_FORM_URL, use_container_width=True)
    
    st.info("💡 **Tip:** Once you submit the form, administration will review and update your details in the main directory shortly.")

elif tab_choice == "📊 Usage Analytics":
    st.subheader("📊 App Engagement & Hourly Traffic Heatmap")
    st.write("Real-time traffic distribution across DD Block by hour:")
    
    try:
        df_visits = pd.read_csv(VISIT_LOG_CSV)
        df_visits.columns = [str(c).strip() for c in df_visits.columns]
        time_col = df_visits.columns[0]
        
        if not df_visits.empty:
            df_visits[time_col] = pd.to_datetime(df_visits[time_col], errors='coerce')
            df_visits['Hour'] = df_visits[time_col].dt.hour
            
            hourly_counts = df_visits['Hour'].value_counts().reindex(range(24), fill_value=0).sort_index()
            hourly_counts.index = [f"{h:02d}:00" for h in hourly_counts.index]
            
            st.metric(label="Total Global App Visits", value=int(len(df_visits)))
            st.bar_chart(hourly_counts)
            st.success("✅ Live tracking active for all resident visits!")
        else:
            st.metric(label="Total Global App Visits", value=0)
            st.info("🕒 Waiting for the first resident visit to populate hourly metrics...")
    except Exception as e:
        st.metric(label="Total Global App Visits", value="Active")
        st.info("🕒 **Hourly Traffic Heatmap:** Tracking active resident visits throughout the day. Data will render once visits are recorded in your VisitLogs tab.")
