import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ---------------------- 核心计算函数 ----------------------
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

# ---------------------- 绘图函数（Plotly 前端渲染，支持中文） ----------------------
def plot_supply_demand(a, b, c, d, price_floor, price_ceiling):
    # 生成价格范围
    price_range = np.linspace(0, 200, 200)
    # 计算供需数量（过滤负数）
    Qd = np.where(demand_curve(price_range, a, b) >= 0, demand_curve(price_range, a, b), np.nan)
    Qs = np.where(supply_curve(price_range, c, d) >= 0, supply_curve(price_range, c, d), np.nan)
    # 计算均衡点
    eq_price, eq_quantity = find_equilibrium(a, b, c, d)

    # 创建 Plotly 图表
    fig = go.Figure()

    # 绘制需求曲线
    fig.add_trace(go.Scatter(
        x=Qd, y=price_range,
        mode='lines', name='需求曲线',
        line=dict(color='red', width=2),
        hovertemplate='价格: %{y:.1f}<br>需求量: %{x:.1f}<extra></extra>'
    ))

    # 绘制供给曲线
    fig.add_trace(go.Scatter(
        x=Qs, y=price_range,
        mode='lines', name='供给曲线',
        line=dict(color='blue', width=2),
        hovertemplate='价格: %{y:.1f}<br>供给量: %{x:.1f}<extra></extra>'
    ))

    # 绘制均衡点
    fig.add_trace(go.Scatter(
        x=[eq_quantity], y=[eq_price],
        mode='markers+text', name='均衡点',
        marker=dict(color='green', size=10),
        text=[f'均衡点<br>P={eq_price:.1f}<br>Q={eq_quantity:.1f}'],
        textposition='top right',
        hovertemplate='均衡价格: %{y:.1f}<br>均衡数量: %{x:.1f}<extra></extra>'
    ))

    # 绘制价格下限
    if price_floor > eq_price and price_floor > 0:
        qd_floor = demand_curve(price_floor, a, b)
        qs_floor = supply_curve(price_floor, c, d)
        # 价格下限线
        fig.add_trace(go.Scatter(
            x=[0, 150], y=[price_floor, price_floor],
            mode='lines', name='价格下限',
            line=dict(color='purple', width=2, dash='dash'),
            hovertemplate='价格下限: %{y:.1f}<extra></extra>'
        ))
        # 过剩区域
        fig.add_trace(go.Scatter(
            x=np.linspace(qd_floor, qs_floor, 100),
            y=[price_floor]*100,
            fill='tozerox', fillcolor='gray', opacity=0.3,
            mode='none', name='过剩'
        ))

    # 绘制价格上限
    if price_ceiling < eq_price and price_ceiling > 0:
        qd_ceiling = demand_curve(price_ceiling, a, b)
        qs_ceiling = supply_curve(price_ceiling, c, d)
        # 价格上限线
        fig.add_trace(go.Scatter(
            x=[0, 150], y=[price_ceiling, price_ceiling],
            mode='lines', name='价格上限',
            line=dict(color='orange', width=2, dash='dash'),
            hovertemplate='价格上限: %{y:.1f}<extra></extra>'
        ))
        # 短缺区域
        fig.add_trace(go.Scatter(
            x=np.linspace(qs_ceiling, qd_ceiling, 100),
            y=[price_ceiling]*100,
            fill='tozerox', fillcolor='red', opacity=0.3,
            mode='none', name='短缺'
        ))

    # 设置图表样式（中文标签）
    fig.update_layout(
        title='供需均衡与价格管制',
        xaxis_title='数量 (Q)',
        yaxis_title='价格 (P)',
        xaxis=dict(range=[0, 150], gridcolor='lightgray'),
        yaxis=dict(range=[0, 200], gridcolor='lightgray'),
        legend=dict(x=0.85, y=0.95),
        width=800, height=500,
        font=dict(family='SimHei, Microsoft YaHei, sans-serif')  # 浏览器中文字体
    )

    return fig, eq_price, eq_quantity

# ---------------------- Streamlit 网页布局（全中文交互） ----------------------
st.set_page_config(page_title="供需均衡可视化", layout="wide")
st.title("📊 经济学供需均衡与价格管制交互演示")
st.markdown("### 输入参数后按回车，实时查看供需曲线和均衡点变化")

# 侧边栏：参数输入
with st.sidebar:
    st.header("⚙️ 参数设置")
    
    # 需求曲线参数
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
    
    # 供给曲线参数
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
    
    # 价格管制参数
    st.divider()
    st.subheader("价格管制")
    price_floor = st.number_input(
        label="价格下限（支持价格）",
        min_value=0, max_value=200, value=0, step=5,
        help="仅当数值大于均衡价格时生效，会导致市场过剩"
    )
    price_ceiling = st.number_input(
        label="价格上限（价格管制）",
        min_value=0, max_value=200, value=200, step=5,
        help="仅当数值小于均衡价格时生效，会导致市场短缺"
    )

# 生成图表
fig, eq_price, eq_quantity = plot_supply_demand(a, b, c, d, price_floor, price_ceiling)
# 显示图表
st.plotly_chart(fig, use_container_width=True)

# 核心计算结果展示
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
