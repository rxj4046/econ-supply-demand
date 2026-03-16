import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import os

# ---------------------- 强制配置Linux中文字体（核心修复） ----------------------
# 1. 关闭Matplotlib字体缓存（避免缓存导致的字体不生效）
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False  # 显示负号
plt.rcParams['font.sans-serif'] = [
    'Noto Sans CJK SC',  # Streamlit Cloud默认的思源黑体
    'WenQuanYi Micro Hei',  # 备用Linux中文字体
    'DejaVu Sans'  # 最终兜底英文字体
]
# 2. 强制设置字体（跳过系统字体查找）
try:
    # 直接指定Linux环境中思源黑体的常见路径
    font_path = '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'
    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
except:
    # 容错：如果找不到字体文件，使用Matplotlib内置的中文兼容配置
    fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    plt.rcParams['font.family'] = 'DejaVu Sans'


# ---------------------- 核心函数（无修改） ----------------------
def create_econ_canvas():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 200)
    ax.set_xlabel('数量 (Q)', fontsize=12)  # 简化标签，减少字符数
    ax.set_ylabel('价格 (P)', fontsize=12)
    ax.set_title('供需均衡与价格管制', fontsize=14)
    ax.grid(True, alpha=0.3)
    return fig, ax


def demand_curve(P, a=100, b=0.5):
    return a - b * P


def supply_curve(P, c=10, d=0.8):
    return c + d * P


def find_equilibrium(a=100, b=0.5, c=10, d=0.8):
    equilibrium_price = (a - c) / (b + d)
    equilibrium_quantity = a - b * equilibrium_price
    return equilibrium_price, equilibrium_quantity


# ---------------------- Streamlit布局（数字输入版） ----------------------
st.set_page_config(page_title="供需均衡可视化", layout="wide")
st.title("📊 经济学供需均衡与价格管制交互演示")
st.markdown("### 输入参数后按回车，实时查看供需曲线和均衡点变化")

with st.sidebar:
    st.header("⚙️ 参数设置")
    st.subheader("需求曲线")
    a = st.number_input("截距 (a) - 总需求规模", 50, 150, 100, 5)
    b = st.number_input("斜率 (b) - 价格敏感度", 0.1, 1.0, 0.5, 0.1)

    st.divider()
    st.subheader("供给曲线")
    c = st.number_input("截距 (c) - 基础供给量", 0, 50, 10, 5)
    d = st.number_input("斜率 (d) - 供给敏感度", 0.1, 1.5, 0.8, 0.1)

    st.divider()
    st.subheader("价格管制")
    price_floor = st.number_input("价格下限（支持价格）", 0, 200, 0, 5)
    price_ceiling = st.number_input("价格上限（价格管制）", 0, 200, 200, 5)

# ---------------------- 绘图逻辑 ----------------------
fig, ax = create_econ_canvas()
price_range = np.linspace(0, 200, 200)
Qd = np.where(demand_curve(price_range, a, b) >= 0, demand_curve(price_range, a, b), np.nan)
Qs = np.where(supply_curve(price_range, c, d) >= 0, supply_curve(price_range, c, d), np.nan)

# 绘制曲线（简化标签，确保显示）
ax.plot(Qd, price_range, 'r-', label='需求曲线', linewidth=2)
ax.plot(Qs, price_range, 'b-', label='供给曲线', linewidth=2)

# 均衡点
eq_price, eq_quantity = find_equilibrium(a, b, c, d)
ax.scatter(eq_quantity, eq_price, s=100, color='green', zorder=5)
# 均衡点标注（简化文字，减少显示压力）
ax.annotate(
    f'均衡点\nP={eq_price:.1f}\nQ={eq_quantity:.1f}',
    (eq_quantity, eq_price),
    xytext=(eq_quantity + 5, eq_price + 10),
    arrowprops=dict(arrowstyle='->', color='green'),
    fontsize=10
)

# 价格下限
if price_floor > eq_price and price_floor > 0:
    qd_floor = demand_curve(price_floor, a, b)
    qs_floor = supply_curve(price_floor, c, d)
    ax.axhline(price_floor, color='purple', linestyle='--', alpha=0.7, label='价格下限')
    ax.fill_betweenx([price_floor, eq_price + 20], qd_floor, qs_floor, color='gray', alpha=0.3, label='过剩')

# 价格上限
if price_ceiling < eq_price and price_ceiling > 0:
    qd_ceiling = demand_curve(price_ceiling, a, b)
    qs_ceiling = supply_curve(price_ceiling, c, d)
    ax.axhline(price_ceiling, color='orange', linestyle='--', alpha=0.7, label='价格上限')
    ax.fill_betweenx([price_ceiling, eq_price - 20], qs_ceiling, qd_ceiling, color='red', alpha=0.3, label='短缺')

ax.legend(loc='upper right', fontsize=10)
plt.tight_layout()

# ---------------------- 显示 ----------------------
st.pyplot(fig, use_container_width=True)

st.divider()
st.subheader("📝 核心计算结果")
st.markdown(f"""
- **均衡价格**：{eq_price:.1f} 美元
- **均衡数量**：{eq_quantity:.1f} 单位
- 需求曲线公式：$Q_d = {a} - {b} \\times P$（价格越高，需求量越低）
- 供给曲线公式：$Q_s = {c} + {d} \\times P$（价格越高，供给量越高）
- 价格管制效果：
  - 若价格下限 > {eq_price:.1f} → 市场过剩
  - 若价格上限 < {eq_price:.1f} → 市场短缺
""")