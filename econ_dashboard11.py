import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# ---------------------- 适配Linux的Matplotlib中文字体配置 ----------------------
# 方案1：优先使用Linux自带的思源黑体（Noto Sans CJK SC）
def set_chinese_font():
    try:
        # 查找Linux环境的中文字体
        font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        # 优先选择思源黑体
        for path in font_paths:
            if 'Noto Sans CJK' in path or 'WenQuanYi' in path:
                font_prop = fm.FontProperties(fname=path)
                plt.rcParams['font.family'] = font_prop.get_name()
                break
        # 兼容配置：显示负号
        plt.rcParams['axes.unicode_minus'] = False
    except Exception:
        # 容错：若找不到中文字体，使用默认字体+英文标签兜底
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False

# 执行字体配置
set_chinese_font()


# ---------------------- 核心函数定义 ----------------------
def create_econ_canvas():
    """创建基础画布"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 150)  # 数量范围
    ax.set_ylim(0, 200)  # 价格范围
    ax.set_xlabel('Quantity (Q) 数量', fontsize=12)
    ax.set_ylabel('Price (P) 价格', fontsize=12)
    ax.set_title('供需均衡与价格管制', fontsize=14)
    ax.grid(True, alpha=0.3)
    return fig, ax


def demand_curve(P, a=100, b=0.5):
    """需求曲线: Qd = a - b*P"""
    return a - b * P


def supply_curve(P, c=10, d=0.8):
    """供给曲线: Qs = c + d*P"""
    return c + d * P


def find_equilibrium(a=100, b=0.5, c=10, d=0.8):
    """计算均衡价格和数量"""
    equilibrium_price = (a - c) / (b + d)
    equilibrium_quantity = a - b * equilibrium_price
    return equilibrium_price, equilibrium_quantity


# ---------------------- Streamlit UI (Number Input Version) ----------------------
st.set_page_config(page_title="供需均衡可视化", layout="wide")
st.title("📊 微观经济学供需均衡与价格管制交互演示")
st.markdown("### 输入参数后按回车，实时查看供需曲线和均衡点变化")

# Sidebar: Number Inputs
with st.sidebar:
    st.header("⚙️ 参数设置")

    # Demand Curve Parameters
    st.subheader("需求曲线")
    a = st.number_input(
        label="截距 (a) - 总需求规模",
        min_value=50, max_value=150, value=100, step=5,
        help="需求曲线截距，数值越大总需求越高"
    )
    b = st.number_input(
        label="斜率 (b) - 价格敏感度",
        min_value=0.1, max_value=1.0, value=0.5, step=0.1,
        help="需求曲线斜率，数值越大对价格越敏感"
    )

    # Supply Curve Parameters
    st.divider()
    st.subheader("供给曲线")
    c = st.number_input(
        label="截距 (c) - 基础供给量",
        min_value=0, max_value=50, value=10, step=5,
        help="供给曲线截距，数值越大基础供给越高"
    )
    d = st.number_input(
        label="斜率 (d) - 供给敏感度",
        min_value=0.1, max_value=1.5, value=0.8, step=0.1,
        help="供给曲线斜率，数值越大对价格越敏感"
    )

    # Price Control Parameters
    st.divider()
    st.subheader("价格管制")
    price_floor = st.number_input(
        label="价格下限（支持价格）",
        min_value=0, max_value=200, value=0, step=5,
        help="仅当数值大于均衡价格时生效，会导致市场过剩"
    )
    price_ceiling = st.number_input(
        label="价格上限（限制价格）",
        min_value=0, max_value=200, value=200, step=5,
        help="仅当数值小于均衡价格时生效，会导致市场短缺"
    )

# ---------------------- Plotting Logic ----------------------
fig, ax = create_econ_canvas()
price_range = np.linspace(0, 200, 200)

# 计算供需数量（过滤负数）
Qd = np.where(demand_curve(price_range, a, b) >= 0, demand_curve(price_range, a, b), np.nan)
Qs = np.where(supply_curve(price_range, c, d) >= 0, supply_curve(price_range, c, d), np.nan)

# 绘制供需曲线
ax.plot(Qd, price_range, 'r-', label='需求曲线', linewidth=2)
ax.plot(Qs, price_range, 'b-', label='供给曲线', linewidth=2)

# 计算并绘制均衡点
eq_price, eq_quantity = find_equilibrium(a, b, c, d)
ax.scatter(eq_quantity, eq_price, s=100, color='green', zorder=5)
ax.annotate(
    f'均衡点\nP={eq_price:.1f}\nQ={eq_quantity:.1f}',
    (eq_quantity, eq_price),
    xytext=(eq_quantity + 5, eq_price + 10),
    arrowprops=dict(arrowstyle='->', color='green'),
    fontsize=10
)

# 价格下限逻辑
if price_floor > eq_price and price_floor > 0:
    qd_floor = demand_curve(price_floor, a, b)
    qs_floor = supply_curve(price_floor, c, d)
    ax.axhline(price_floor, color='purple', linestyle='--', alpha=0.7, label='价格下限')
    ax.fill_betweenx(
        [price_floor, eq_price + 20],
        qd_floor, qs_floor,
        color='gray', alpha=0.3, label='过剩'
    )

# 价格上限逻辑
if price_ceiling < eq_price and price_ceiling > 0:
    qd_ceiling = demand_curve(price_ceiling, a, b)
    qs_ceiling = supply_curve(price_ceiling, c, d)
    ax.axhline(price_ceiling, color='orange', linestyle='--', alpha=0.7, label='价格上限')
    ax.fill_betweenx(
        [price_ceiling, eq_price - 20],
        qs_ceiling, qd_ceiling,
        color='red', alpha=0.3, label='短缺'
    )

# Legend and layout
ax.legend(loc='upper right', fontsize=10)
plt.tight_layout()

# ---------------------- Display Chart & Explanations ----------------------
# Fix: Replace use_container_width with width='stretch' (remove deprecation warning)
st.pyplot(fig, width='stretch')

# Results Explanation
st.divider()
st.subheader("📝 核心计算结果")
st.markdown(f"""
- **均衡价格**: {eq_price:.1f} 元
- **均衡数量**: {eq_quantity:.1f} 单位
- 需求曲线公式: $Q_d = {a} - {b} \\times P$ (价格越高，需求量越低)
- 供给曲线公式: $Q_s = {c} + {d} \\times P$ (价格越高，供给量越高)
- 价格管制效果:
  - 若价格下限 > {eq_price:.1f} → 市场过剩
  - 若价格上限 < {eq_price:.1f} → 市场短缺
""")
