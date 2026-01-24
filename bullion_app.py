import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Private Bullion Calculator (UK)",
    page_icon="🪙",
    layout="centered"
)

# ---------------- PASSWORD PROTECTION ----------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<br><br><br>", unsafe_allow_html=True)  # push down for mobile
        with st.container():
            st.subheader("🔒 Login")
            pwd = st.text_input("Password", type="password")

        if pwd and pwd == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.stop()

check_password()

# ---------------- CONSTANTS ----------------
TROY_OZ_IN_G = 31.1035

# ---------------- SESSION DEFAULTS ----------------
if "spot_gold_oz" not in st.session_state:
    st.session_state.spot_gold_oz = 0.0

if "spot_silver_oz" not in st.session_state:
    st.session_state.spot_silver_oz = 0.0

if "premium_pct" not in st.session_state:
    st.session_state.premium_pct = 5.0

# ---------------- HEADER ----------------
st.title("🪙 Private Bullion Calculator (UK)")
st.caption("Gold & Silver • Bars & Coins • UK VAT rules")

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
            "Weight (kg)",
            [1, 2, 5, 10, 20, 50, 100]
        ) * 1000

    weight_oz = weight_g / TROY_OZ_IN_G
    weight_label = f"{weight_g / 1000:.3f} kg" if weight_g >= 1000 else f"{weight_g} g"

# ---------------- SPOT PRICE ----------------
st.subheader("Spot price")

spot_unit = st.selectbox(
    "Spot unit",
    ["£ / oz", "£ / gram", "£ / kg"]
)

saved_spot_oz = (
    st.session_state.spot_gold_oz
    if metal == "Gold"
    else st.session_state.spot_silver_oz
)

# Convert saved spot to display unit
if spot_unit == "£ / oz":
    spot_display = saved_spot_oz
elif spot_unit == "£ / gram":
    spot_display = saved_spot_oz / TROY_OZ_IN_G
else:
    spot_display = (saved_spot_oz / TROY_OZ_IN_G) * 1000

spot_input = st.number_input(
    "Spot price",
    min_value=0.0,
    step=0.01,
    value=spot_display,
    format="%.2f"
)

# Convert back to £/oz
if spot_unit == "£ / oz":
    spot_per_oz = spot_input
elif spot_unit == "£ / gram":
    spot_per_oz = spot_input * TROY_OZ_IN_G
else:
    spot_per_oz = (spot_input / 1000) * TROY_OZ_IN_G

col1, col2 = st.columns(2)

if col1.button("Save Gold spot"):
    st.session_state.spot_gold_oz = spot_per_oz
    st.success("Gold spot saved")

if col2.button("Save Silver spot"):
    st.session_state.spot_silver_oz = spot_per_oz
    st.success("Silver spot saved")

st.caption("Source: Kitco / LBMA (manual reference)")

# ---------------- PREMIUM ----------------
premium_pct = st.slider(
    "Premium (%)",
    min_value=0.0,
    max_value=25.0,
    value=st.session_state.premium_pct,
    step=0.1
)

st.session_state.premium_pct = premium_pct

# ---------------- CALCULATIONS ----------------
spot_per_oz = (
    st.session_state.spot_gold_oz
    if metal == "Gold"
    else st.session_state.spot_silver_oz
)

spot_total = spot_per_oz * weight_oz
premium_value = spot_total * (premium_pct / 100)
subtotal = spot_total + premium_value

vat_rate = 0.20 if metal == "Silver" else 0.0
vat_value = subtotal * vat_rate
final_price = subtotal + vat_value

# ---------------- OUTPUT ----------------
st.divider()

st.write(f"**Metal:** {metal}")
st.write(f"**Product:** {product_type}")
st.write(f"**Weight:** {weight_label} ({weight_oz:.4f} oz)")

st.metric("Spot value", f"£{spot_total:,.2f}")
st.metric("Premium", f"£{premium_value:,.2f}")

if metal == "Silver":
    st.metric("VAT (20%)", f"£{vat_value:,.2f}")

st.metric("Final Retail Price", f"£{final_price:,.2f}")





