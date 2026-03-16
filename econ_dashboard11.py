import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ---------------------- 极简字体配置（仅确保负号显示） ----------------------
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display
plt.rcParams['font.family'] = 'DejaVu Sans'  # Default font in Streamlit Cloud


# ---------------------- Core Functions ----------------------
def create_econ_canvas():
    """Create basic plot canvas"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 150)  # Quantity range
    ax.set_ylim(0, 200)  # Price range
    ax.set_xlabel('Quantity (Q)', fontsize=12)
    ax.set_ylabel('Price (P)', fontsize=12)
    ax.set_title('Supply & Demand Equilibrium with Price Controls', fontsize=14)
    ax.grid(True, alpha=0.3)
    return fig, ax


def demand_curve(P, a=100, b=0.5):
    """Demand curve formula: Qd = a - b*P"""
    return a - b * P


def supply_curve(P, c=10, d=0.8):
    """Supply curve formula: Qs = c + d*P"""
    return c + d * P


def find_equilibrium(a=100, b=0.5, c=10, d=0.8):
    """Calculate equilibrium price and quantity"""
    equilibrium_price = (a - c) / (b + d)
    equilibrium_quantity = a - b * equilibrium_price
    return equilibrium_price, equilibrium_quantity


# ---------------------- Streamlit UI (Number Input Version) ----------------------
st.set_page_config(page_title="Supply-Demand Equilibrium", layout="wide")
st.title("📊 Economics: Supply & Demand Equilibrium Interactive Tool")
st.markdown("### Enter values and press Enter to update the chart in real-time")

# Sidebar: Number Inputs
with st.sidebar:
    st.header("⚙️ Parameter Settings")

    # Demand Curve Parameters
    st.subheader("Demand Curve")
    a = st.number_input(
        label="Intercept (a) - Total Demand Scale",
        min_value=50, max_value=150, value=100, step=5,
        help="Higher value = greater total demand"
    )
    b = st.number_input(
        label="Slope (b) - Price Sensitivity",
        min_value=0.1, max_value=1.0, value=0.5, step=0.1,
        help="Higher value = more sensitive to price changes"
    )

    # Supply Curve Parameters
    st.divider()
    st.subheader("Supply Curve")
    c = st.number_input(
        label="Intercept (c) - Base Supply Volume",
        min_value=0, max_value=50, value=10, step=5,
        help="Higher value = greater base supply"
    )
    d = st.number_input(
        label="Slope (d) - Price Sensitivity",
        min_value=0.1, max_value=1.5, value=0.8, step=0.1,
        help="Higher value = more sensitive to price changes"
    )

    # Price Control Parameters
    st.divider()
    st.subheader("Price Controls")
    price_floor = st.number_input(
        label="Price Floor (Support Price)",
        min_value=0, max_value=200, value=0, step=5,
        help="Takes effect only if > equilibrium price (causes surplus)"
    )
    price_ceiling = st.number_input(
        label="Price Ceiling (Price Control)",
        min_value=0, max_value=200, value=200, step=5,
        help="Takes effect only if < equilibrium price (causes shortage)"
    )

# ---------------------- Plotting Logic ----------------------
fig, ax = create_econ_canvas()
price_range = np.linspace(0, 200, 200)

# Calculate demand/supply quantities (filter negative values)
Qd = np.where(demand_curve(price_range, a, b) >= 0, demand_curve(price_range, a, b), np.nan)
Qs = np.where(supply_curve(price_range, c, d) >= 0, supply_curve(price_range, c, d), np.nan)

# Plot curves
ax.plot(Qd, price_range, 'r-', label='Demand Curve', linewidth=2)
ax.plot(Qs, price_range, 'b-', label='Supply Curve', linewidth=2)

# Calculate and plot equilibrium point
eq_price, eq_quantity = find_equilibrium(a, b, c, d)
ax.scatter(eq_quantity, eq_price, s=100, color='green', zorder=5)
ax.annotate(
    f'Equilibrium\nP={eq_price:.1f}\nQ={eq_quantity:.1f}',
    (eq_quantity, eq_price),
    xytext=(eq_quantity + 5, eq_price + 10),
    arrowprops=dict(arrowstyle='->', color='green'),
    fontsize=10
)

# Price Floor Logic
if price_floor > eq_price and price_floor > 0:
    qd_floor = demand_curve(price_floor, a, b)
    qs_floor = supply_curve(price_floor, c, d)
    ax.axhline(price_floor, color='purple', linestyle='--', alpha=0.7, label='Price Floor')
    ax.fill_betweenx(
        [price_floor, eq_price + 20],
        qd_floor, qs_floor,
        color='gray', alpha=0.3, label='Surplus'
    )

# Price Ceiling Logic
if price_ceiling < eq_price and price_ceiling > 0:
    qd_ceiling = demand_curve(price_ceiling, a, b)
    qs_ceiling = supply_curve(price_ceiling, c, d)
    ax.axhline(price_ceiling, color='orange', linestyle='--', alpha=0.7, label='Price Ceiling')
    ax.fill_betweenx(
        [price_ceiling, eq_price - 20],
        qs_ceiling, qd_ceiling,
        color='red', alpha=0.3, label='Shortage'
    )

# Legend and layout
ax.legend(loc='upper right', fontsize=10)
plt.tight_layout()

# ---------------------- Display Chart & Explanations ----------------------
# Fix: Replace use_container_width with width='stretch' (remove deprecation warning)
st.pyplot(fig, width='stretch')

# Results Explanation
st.divider()
st.subheader("📝 Key Calculation Results")
st.markdown(f"""
- **Equilibrium Price**: {eq_price:.1f} USD
- **Equilibrium Quantity**: {eq_quantity:.1f} units
- Demand Curve Formula: $Q_d = {a} - {b} \\times P$ (Higher price = lower quantity demanded)
- Supply Curve Formula: $Q_s = {c} + {d} \\times P$ (Higher price = higher quantity supplied)
- Price Control Effects:
  - If Price Floor > {eq_price:.1f} → Market Surplus
  - If Price Ceiling < {eq_price:.1f} → Market Shortage
""")