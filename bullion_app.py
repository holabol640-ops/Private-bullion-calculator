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

    # Simplified weight selection
    weight_unit = st.selectbox("Weight unit", ["grams", "kilograms", "oz", "tola"])

    if weight_unit == "grams":
        weight_g = st.number_input("Weight (grams)", min_value=0.0, step=0.01)
    elif weight_unit == "kilograms":
        weight_g = st.number_input("Weight (kg)", min_value=0.0, step=0.01) * 1000
    elif weight_unit == "oz":
        weight_oz = st.number_input("Weight (oz)", min_value=0.0, step=0.0001)
        weight_g = weight_oz * TROY_OZ_IN_G
    else:  # tola
        tolas = st.number_input("Number of tolas", min_value=0.0, step=0.01)
        weight_g = tolas * TOLA_IN_G

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
    value=spot_display
)

if spot_unit == "£ / oz":
    spot_per_oz = spot_input
elif spot_unit == "£ / gram":
    spot_per_oz = spot_input * TROY_OZ_IN_G
else:
    spot_per_oz = (spot_input / 1000) * TROY_OZ_IN_G

# Removed Save Gold/Silver spot buttons
# col1, col2 = st.columns(2)
# if col1.button("Save Gold spot"):
#     st.session_state.spot_gold_oz = spot_per_oz
# if col2.button("Save Silver spot"):
#     st.session_state.spot_silver_oz = spot_per_oz
