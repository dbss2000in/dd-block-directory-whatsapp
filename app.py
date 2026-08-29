import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="DD Block Directory Pro", page_icon="📍", layout="centered")

st.title("📍 DD Block New Town Directory")
st.write("Kolkata - 700156 (WhatsApp & Maps Enabled)")

@st.cache_data
def load_data():
    excel_file = "DD_Block_New_Town_Kolkata_Directory.xlsx"
    xls = pd.ExcelFile(excel_file)
    sheet_to_use = xls.sheet_names[0]
    for sheet in xls.sheet_names:
        if "Directory" in sheet:
            sheet_to_use = sheet
            break
            
    df = pd.read_excel(excel_file, sheet_name=sheet_to_use)
    return df

try:
    raw_df = load_data()
    
    header_row_idx = 0
    for idx, row in raw_df.iterrows():
        row_str = str(row.values)
        if "Name" in row_str and "Phone" in row_str:
            header_row_idx = idx
            break
            
    excel_file = "DD_Block_New_Town_Kolkata_Directory.xlsx"
    xls = pd.ExcelFile(excel_file)
    sheet_to_use = xls.sheet_names[0]
    for sheet in xls.sheet_names:
        if "Directory" in sheet:
            sheet_to_use = sheet
            break
            
    df = pd.read_excel(excel_file, sheet_name=sheet_to_use, skiprows=header_row_idx)
    df = df.dropna(subset=[df.columns[0]])
    
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
        phone = row.get(phone_col, "N/A")
        
        if pd.isna(name) or str(name).strip() == "" or str(name).lower() == "nan":
            continue
            
        # Clean phone number digits
        digits_only = "".join(filter(str.isdigit, str(phone)))
        
        # Format phone for India (+91) WhatsApp links
        if len(digits_only) == 10:
            wa_number = f"91{digits_only}"
            call_phone = f"+91 {digits_only}"
        elif len(digits_only) > 10:
            wa_number = digits_only
            call_phone = f"+{digits_only}"
        else:
            wa_number = ""
            call_phone = str(phone)

        # Precise Map query using simplified plot number + DD Block
        addr_text = str(address).strip()
        # Clean up any residual words if needed, keeping plot format clean
        map_query = f"{addr_text}, DD Block, New Town, Kolkata, West Bengal 700156"
        encoded_address = urllib.parse.quote(map_query)
        
        map_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
        directions_url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_address}"
        
        # WhatsApp API Links
        wa_chat_url = f"https://wa.me/{wa_number}" if wa_number else "#"
        wa_call_url = f"https://api.whatsapp.com/send?phone={wa_number}&text=Hello%2C%20calling%20via%20WhatsApp" if wa_number else "#"
        tel_url = f"tel:{digits_only}" if digits_only else "#"

        # Render UI Card
        st.markdown(f"👤 **{name}**")
        
        if address and str(address).lower() != "nan":
            st.markdown(f"📍 **Plot:** [{address}]({map_url}) | 🚗 [Directions]({directions_url})")
            
        if wa_number:
            st.markdown(f"📞 [{call_phone}]({tel_url})  |  💬 [WhatsApp Chat]({wa_chat_url})  |  📞 [WhatsApp Call]({wa_call_url})")
        else:
            st.markdown(f"📞 {phone}")
            
        st.markdown("---")

except Exception as e:
    st.error(f"An error occurred while loading data: {e}")
