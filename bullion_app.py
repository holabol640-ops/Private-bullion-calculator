import streamlit as st
import requests

@st.cache_data(ttl=300)  # 5-minute cache
def get_live_spot_prices():
    try:
        url = "https://api.metals.live/v1/spot"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        # data format: [["gold", price], ["silver", price]]
        prices = {item[0]: item[1] for item in data}

        gold = prices.get("gold")
        silver = prices.get("silver")

        return gold, silver
    except Exception as e:
        st.error(f"Live spot error: {e}")
        return None, None
        
# -------- PASSWORD PROTECTION (USING SECRETS) --------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        pwd = st.text_input("Password", type="password")

        if pwd and pwd == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.stop()

check_password()

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Private Bullion Calculator (UK)",
    page_icon="🪙",
    layout="centered"
)

st.title("🪙 Private Bullion Calculator (UK)")
st.caption("Gold & Silver • bars & coins • UK VAT rules")

TROY_OZ_IN_G = 31.1035

# ---------------- SESSION DEFAULTS ----------------
if "premium_pct" not in st.session_state:
    st.session_state.premium_pct = 5.0

# ---------------- PRODUCT TYPE ----------------
product_type = st.selectbox(
    "Product type",
    ["Gold Bar", "Gold Sovereign", "Silver Bar", "Silver Coin (1 oz)"]
)

# ---------------- METAL + WEIGHT LOGIC ----------------
if product_type == "Gold Sovereign":
    metal = "Gold"
    weight_g = 7.98805
    weight_oz = 0.2354
    weight_label = "Gold Sovereign"

elif product_type == "Silver Coin (1 oz)":
    metal = "Silver"
    weight_oz = 1.0
    weight_g = TROY_OZ_IN_G
    weight_label = "1 oz Silver Coin"

else:
    metal = "Gold" if "Gold" in product_type else "Silver"

    unit = st.selectbox("Weight unit", ["Grams", "Kilograms"])

    if unit == "Grams":
        weight_g = st.selectbox(
            "Weight",
            [1, 2, 5, 10, 20, 50, 100, 250, 500, 1000]
        )
    else:
        weight_g = st.selectbox(
            "Weight",
            [1, 2, 5, 10, 20, 50, 100]  # kg
        ) * 1000

    weight_oz = weight_g / TROY_OZ_IN_G
    weight_label = f"{weight_g / 1000:.3f} kg" if weight_g >= 1000 else f"{weight_g} g"

# ---------------- INPUTS (SMOOTH) ----------------
# ---------------- SPOT PRICE ----------------

st.subheader("Spot price")

use_live = st.checkbox("Use live spot price", value=True)

gold_spot, silver_spot = get_live_spot_prices()

live_spot = gold_spot if metal == "Gold" else silver_spot

if use_live and live_spot:
    spot_per_oz = float(live_spot)
    st.success(f"Live {metal} spot: £{spot_per_oz:,.2f} per oz")
else:
    spot_per_oz = st.number_input(
        "Spot price (£ per oz)",
        min_value=0.0,
        step=0.01,
        format="%.2f"
    )

premium_pct = st.slider(
    "Premium (%)",
    min_value=0.0,
    max_value=25.0,
    value=st.session_state.premium_pct,
    step=0.1
)

st.session_state.premium_pct = premium_pct

# ---------------- CALCULATIONS ----------------
try:
    spot_per_oz = float(spot_per_oz)
except ValueError:
    spot_per_oz = 0.0

spot_value = spot_per_oz * weight_oz
premium_value = spot_value * (premium_pct / 100)
subtotal = spot_value + premium_value

vat_rate = 0.20 if metal == "Silver" else 0.0
vat_value = subtotal * vat_rate
final_price = subtotal + vat_value

# ---------------- OUTPUT ----------------
st.divider()

st.write(f"**Metal:** {metal}")
st.write(f"**Product:** {product_type}")
st.write(f"**Weight:** {weight_label} ({weight_oz:.4f} oz)")

st.metric("Spot value", f"£{spot_value:,.2f}")
st.metric("Premium", f"£{premium_value:,.2f}")

if metal == "Silver":
    st.metric("VAT (20%)", f"£{vat_value:,.2f}")


st.metric("Final Retail Price", f"£{final_price:,.2f}")




