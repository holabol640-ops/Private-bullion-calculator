import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Private Bullion Calculator (UK)",
    page_icon="🪙",
    layout="centered"
)

# ---------------- PASSWORD ----------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
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
TOLA_IN_G = 11.6638

# ---------------- SESSION DEFAULTS ----------------
st.session_state.setdefault("spot_gold_oz", 0.0)
st.session_state.setdefault("spot_silver_oz", 0.0)
st.session_state.setdefault("premium_pct", 5.0)
st.session_state.setdefault("calc_pressed", False)

# ---------------- HEADER ----------------
st.title("🪙 Private Bullion Calculator (UK)")
st.caption("Gold & Silver • Bars & Coins • UK VAT rules")

# ---------------- PRODUCT TYPE ----------------
product_type = st.selectbox(
    "Product type",
    ["Gold Bar", "Gold Sovereign", "Silver Bar", "Silver Coin (1 oz)"]
)

# ---------------- METAL & WEIGHT ----------------
if product_type == "Gold Sovereign":
    metal = "Gold"
    weight_g = 7.98805
    weight_oz = 0.2354
    weight_label = "Gold Sovereign"

elif product_type == "Silver Coin (1 oz)":
    metal = "Silver"
    weight_g = TROY_OZ_IN_G
    weight_oz = 1.0
    weight_label = "1 oz Silver Coin"

else:
    metal = "Gold" if "Gold" in product_type else "Silver"

    # Weight input in different units
    weight_unit = st.selectbox(
        "Weight unit",
        ["Grams (g)", "Kilograms (kg)", "Troy Ounces (oz)", "Tola"]
    )
    
    weight_value = st.number_input(
        f"Weight ({weight_unit})",
        min_value=0.0,
        step=0.01
    )
    
    # Convert to grams first
    if weight_unit == "Grams (g)":
        weight_g = weight_value
    elif weight_unit == "Kilograms (kg)":
        weight_g = weight_value * 1000
    elif weight_unit == "Troy Ounces (oz)":
        weight_g = weight_value * TROY_OZ_IN_G
    else:  # Tola
        weight_g = weight_value * TOLA_IN_G
    
    weight_oz = weight_g / TROY_OZ_IN_G
    weight_label = f"{weight_g:.2f} g"

# ---------------- SPOT PRICE ----------------
st.subheader("Spot price")

spot_unit = st.selectbox("Spot unit", ["£ / oz", "£ / gram", "£ / kg"])

saved_spot_oz = (
    st.session_state.spot_gold_oz
    if metal == "Gold"
    else st.session_state.spot_silver_oz
)

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
    key=f"spot_{metal.lower()}"
)

if spot_unit == "£ / oz":
    spot_per_oz = spot_input
elif spot_unit == "£ / gram":
    spot_per_oz = spot_input * TROY_OZ_IN_G
else:
    spot_per_oz = (spot_input / 1000) * TROY_OZ_IN_G

# Automatically save spot price when changed
if metal == "Gold":
    st.session_state.spot_gold_oz = spot_per_oz
else:
    st.session_state.spot_silver_oz = spot_per_oz

# ---------------- PREMIUM ----------------
st.subheader("Premium")

premium_pct = st.number_input(
    "Premium (%)",
    min_value=0.0,
    step=0.1,
    value=st.session_state.premium_pct
)
st.session_state.premium_pct = premium_pct

# ---------------- EQUAL BUTTON ----------------
st.divider()
if st.button("🟰 Calculate / Lock Price"):
    st.session_state.calc_pressed = True

# ---------------- CALCULATIONS ----------------
if st.session_state.calc_pressed:
    spot_oz = (
        st.session_state.spot_gold_oz
        if metal == "Gold"
        else st.session_state.spot_silver_oz
    )

    spot_total = spot_oz * weight_oz
    premium_value = spot_total * (premium_pct / 100)
    subtotal = spot_total + premium_value

    vat_rate = 0.20 if metal == "Silver" else 0.0
    vat_value = subtotal * vat_rate
    final_price = subtotal + vat_value

    st.divider()
    st.write(f"**Metal:** {metal}")
    st.write(f"**Product:** {product_type}")
    st.write(f"**Weight:** {weight_label} ({weight_oz:.4f} oz)")

    st.metric("Spot value", f"£{spot_total:,.2f}")
    st.metric("Premium", f"£{premium_value:,.2f}")

    if metal == "Silver":
        st.metric("VAT (20%)", f"£{vat_value:,.2f}")

    st.metric("Final Retail Price", f"£{final_price:,.2f}")
