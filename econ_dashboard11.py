# 导入依赖
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import urllib.request
import os
import tempfile

# ---------------------- 配置Matplotlib中文字体（增强版）---------------------
def setup_chinese_font():
    """
    尝试设置中文字体，若系统无中文字体则从网络下载 SimHei.ttf 并加载。
    返回是否成功设置中文字体。
    """
    # 常见中文字体名称列表（按优先级排序）
    chinese_fonts = [
        'SimHei',                     # 黑体
        'Microsoft YaHei',             # 微软雅黑
        'WenQuanYi Zen Hei',           # 文泉驿正黑（Linux常用）
        'Noto Sans CJK SC',            # 思源黑体
        'Droid Sans Fallback',         # Android回退字体
        'PingFang SC',                 # 苹方（macOS）
        'Hiragino Sans GB'             # 冬青黑体
    ]

    # 1. 尝试系统已有中文字体
    for font_name in chinese_fonts:
        try:
            # 检查字体是否存在（findfont返回路径，若不存在则返回默认字体路径）
            font_path = fm.findfont(font_name, fallback_to_default=False)
            # 如果找到的字体不是默认字体，则认为有效
            default_font = fm.findfont('DejaVu Sans', fallback_to_default=True)
            if font_path != default_font:
                plt.rcParams['font.sans-serif'] = [font_name]
                plt.rcParams['axes.unicode_minus'] = False
                print(f"使用系统字体: {font_name}")
                return True
        except:
            continue

    # 2. 系统无中文字体，尝试下载 SimHei.ttf 到临时目录
    print("未找到系统中文字体，尝试下载 SimHei.ttf...")
    font_url = "https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimHei.ttf"
    temp_dir = tempfile.gettempdir()
    font_path = os.path.join(temp_dir, "SimHei.ttf")

    # 如果字体文件不存在则下载
    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(font_url, font_path)
            print("SimHei.ttf 下载完成")
        except Exception as e:
            print(f"下载字体失败: {e}")
            # 回退：尝试使用默认字体（可能显示方框）
            plt.rcParams['axes.unicode_minus'] = False
            return False

    # 3. 加载下载的字体文件
    try:
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.sans-serif'] = [fm.FontProperties(fname=font_path).get_name()]
        plt.rcParams['axes.unicode_minus'] = False
        print("已加载下载的 SimHei.ttf")
        return True
    except Exception as e:
        print(f"加载下载字体失败: {e}")
        plt.rcParams['axes.unicode_minus'] = False
        return False

# 初始化字体设置
font_ok = setup_chinese_font()
if not font_ok:
    st.warning("⚠️ 未找到中文字体，图表中的中文可能无法正常显示，建议使用英文标签。")

# ---------------------- 核心函数定义（保持不变）---------------------
def create_econ_canvas():
    """创建基础画布"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 150)  # 数量范围
    ax.set_ylim(0, 200)  # 价格范围
    ax.set_xlabel('Quantity (Q) 数量', fontsize=12)
    ax.set_ylabel('Price ($P$) 价格', fontsize=12)
    ax.set_title('供需均衡与价格管制', fontsize=14)
    ax.grid(True, alpha=0.3)
    return fig, ax


def demand_curve(P, a=100, b=0.5):
    """需求曲线：Qd = a - b*P"""
    return a - b * P


def supply_curve(P, c=10, d=0.8):
    """供给曲线：Qs = c + d*P"""
    return c + d * P


def find_equilibrium(a=100, b=0.5, c=10, d=0.8):
    """计算均衡价格和数量"""
    equilibrium_price = (a - c) / (b + d)
    equilibrium_quantity = a - b * equilibrium_price
    return equilibrium_price, equilibrium_quantity


# ---------------------- Streamlit 网页布局（数字输入版）---------------------
st.set_page_config(page_title="供需均衡可视化", layout="wide")
st.title("📊 经济学供需均衡与价格管制交互演示")
st.markdown("### 输入参数后按回车，实时查看供需曲线和均衡点变化")

with st.sidebar:
    st.header("⚙️ 参数设置")
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

# ---------------------- 核心绘图逻辑 ----------------------
fig, ax = create_econ_canvas()
price_range = np.linspace(0, 200, 200)

Qd = demand_curve(price_range, a, b)
Qs = supply_curve(price_range, c, d)
Qd = np.where(Qd >= 0, Qd, np.nan)
Qs = np.where(Qs >= 0, Qs, np.nan)

ax.plot(Qd, price_range, 'r-', label='需求曲线', linewidth=2)
ax.plot(Qs, price_range, 'b-', label='供给曲线', linewidth=2)

eq_price, eq_quantity = find_equilibrium(a, b, c, d)
ax.scatter(eq_quantity, eq_price, s=100, color='green', zorder=5)
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
    ax.axhline(price_floor, color='purple', linestyle='--', alpha=0.7, label='Price Floor (价格下限)')
    ax.fill_betweenx(
        [price_floor, eq_price + 20],
        qd_floor, qs_floor,
        color='gray', alpha=0.3, label='Surplus (过剩)'
    )

# 价格上限
if price_ceiling < eq_price and price_ceiling > 0:
    qd_ceiling = demand_curve(price_ceiling, a, b)
    qs_ceiling = supply_curve(price_ceiling, c, d)
    ax.axhline(price_ceiling, color='orange', linestyle='--', alpha=0.7, label='Price Ceiling (价格上限)')
    ax.fill_betweenx(
        [price_ceiling, eq_price - 20],
        qs_ceiling, qd_ceiling,
        color='red', alpha=0.3, label='Shortage (短缺)'
    )

ax.legend(loc='upper right', fontsize=10)
plt.tight_layout()

st.pyplot(fig)

st.divider()
st.subheader("📝 核心计算结果")
st.markdown(f"""
- **均衡价格**：{eq_price:.1f} 元
- **均衡数量**：{eq_quantity:.1f} 单位
- 需求曲线公式：$Q_d = {a} - {b} \\times P$（价格越高，需求量越低）
- 供给曲线公式：$Q_s = {c} + {d} \\times P$（价格越高，供给量越高）
- 价格管制效果：
  - 若价格下限 > {eq_price:.1f} → 市场过剩
  - 若价格上限 < {eq_price:.1f} → 市场短缺
""")
