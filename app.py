import streamlit as st
import datetime
import calendar

# ================= 1. 配置与后台数据 =================
st.set_page_config(
    page_title="CURV 周期监测日历", 
    page_icon="💍", 
    layout="centered"
)

# 模拟后台数据库
USER_DB = {
    "郝欣雅": 31,
    "王如琳": 37,
    "马明曦": 31
}

# LH 监测对照表
LH_TABLE = [
    (21, 23, 5, 9),
    (24, 25, 7, 10),
    (26, 27, 8, 10),
    (28, 28, 9, 8),
    (29, 30, 11, 9),
    (31, 35, 12, 10)
]

# ================= 2. 核心逻辑 =================

def get_testing_schedule(cycle_len, start_date):
    """生成具体的检测日期字典"""
    events = {}
    
    # --- 阶段 1: 基础激素 (FSH + LH) ---
    # 规则: D2 - D4
    for i in range(1, 4):
        d = start_date + datetime.timedelta(days=i)
        events[d] = {"type": "BASE", "label": "FSH + LH", "desc": "基础值"}

    # --- 阶段 2: 排卵监测 (LH) ---
    # 查表
    lh_start_day = 12
    lh_duration = 10
    
    matched = False
    for (min_c, max_c, start_d, dur) in LH_TABLE:
        if min_c <= cycle_len <= max_c:
            lh_start_day = start_d
            lh_duration = dur
            matched = True
            break
            
    if not matched and cycle_len > 35:
        lh_start_day = 13 
        lh_duration = 10

    # 生成 LH 日期
    lh_start_date = start_date + datetime.timedelta(days=lh_start_day - 1)
    for i in range(lh_duration):
        d = lh_start_date + datetime.timedelta(days=i)
        if d in events:
            events[d]["label"] += " & LH"
            events[d]["type"] = "BOTH"
        else:
            events[d] = {"type": "OVULATION", "label": "LH (排卵)", "desc": "排卵监测"}
            
    return events, lh_start_date

# ================= 3. 自定义日历渲染组件 (白色主题优化版) =================

def render_html_calendar(year, month, events):
    """
    生成 HTML 日历，增加了白色卡片样式和阴影
    """
    cal = calendar.monthcalendar(year, month)
    month_name = f"{year}年 {month}月"
    
    # CSS 样式 (优化了在纯白背景下的显示效果)
    html = f"""
    <style>
        .calendar-card {{
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* 轻微阴影 */
            border: 1px solid #f0f0f0;
        }}
        .month-title {{ 
            font-size: 1.4em; 
            font-weight: bold; 
            margin-bottom: 15px; 
            color: #2c3e50; 
            text-align: center;
        }}
        .cal-table {{ width: 100%; border-collapse: separate; border-spacing: 4px; }}
        .cal-header td {{ 
            color: #888; 
            font-weight: 500; 
            text-align: center; 
            padding-bottom: 10px;
        }}
        .cal-cell {{ 
            width: 14.2%; 
            height: 85px; 
            border: 1px solid #f2f2f2; 
            border-radius: 8px;
            vertical-align: top; 
            padding: 6px; 
            font-size: 0.9em; 
            background-color: #fafafa; /* 默认格子的淡淡灰背景 */
        }}
        .day-num {{ font-weight: bold; color: #444; margin-bottom: 4px; display: block; }}
        
        /* 事件胶囊样式 */
        .event-tag {{
            display: block; font-size: 0.75em; padding: 3px 2px; border-radius: 4px;
            margin-top: 4px; color: white; text-align: center; font-weight: 500;
        }}
        .evt-base {{ background-color: #5D9CEC; }} /* 柔和蓝 */
        .evt-ovu {{ background-color: #FF7E79; }} /* 柔和红 */
        .evt-both {{ background-color: #AC92EC; }} /* 柔和紫 */
        
        .empty {{ background-color: transparent; border: none; }}
    </style>
    
    <div class="calendar-card">
        <div class="month-title">{month_name}</div>
        <table class="cal-table">
            <tr class="cal-header">
                <td>一</td><td>二</td><td>三</td><td>四</td><td>五</td><td>六</td><td>日</td>
            </tr>
    """

    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td class='cal-cell empty'></td>"
                continue
            
            current_date = datetime.date(year, month, day)
            cell_content = f"<span class='day-num'>{day}</span>"
            
            if current_date in events:
                evt = events[current_date]
                css_class = ""
                if evt["type"] == "BASE": css_class = "evt-base"
                elif evt["type"] == "OVULATION": css_class = "evt-ovu"
                else: css_class = "evt-both"
                
                cell_content += f"<span class='event-tag {css_class}'>{evt['label']}</span>"
            
            # 如果有事件，格子背景改为白色以突显
            bg_style = "style='background-color: white; border-color: #e0e0e0;'" if current_date in events else ""
            
            html += f"<td class='cal-cell' {bg_style}>{cell_content}</td>"
        html += "</tr>"
    
    html += "</table></div>"
    return html

# ================= 4. 前端界面 =================

st.title("CURV 周期检测日历 🗓️")
st.markdown("请输入您的基本信息，生成本周期的 **FSH** 与 **LH** 专属检测日历。")

# --- 输入区 (静默匹配) ---
with st.container(border=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        user_name = st.text_input("请输入姓名", placeholder="填写姓名")
        
        # 静默匹配逻辑
        default_cycle = 28
        if user_name:
            user_name = user_name.strip()
            if user_name in USER_DB:
                default_cycle = USER_DB[user_name]
        
        cycle_len = st.number_input("平均月经周期 (天)", value=default_cycle, min_value=20, max_value=45)

    with col2:
        start_date = st.date_input("本次月经第一天 (见红日)", datetime.date.today())

# --- 生成区 ---
if st.button("生成我的检测日历", type="primary"):
    if not user_name:
        st.error("请先输入姓名")
    else:
        st.divider()
        events, lh_start_date = get_testing_schedule(cycle_len, start_date)
        
        # 1. 顶部图例
        st.markdown("""
        <div style="display: flex; gap: 15px; margin-bottom: 15px; font-size: 0.9em; justify-content: center;">
            <div style="display:flex; align-items:center; gap:5px;">
                <span style="display:block;width:12px;height:12px;background:#5D9CEC;border-radius:2px;"></span> 
                <span>基础检测 (FSH+LH)</span>
            </div>
            <div style="display:flex; align-items:center; gap:5px;">
                <span style="display:block;width:12px;height:12px;background:#FF7E79;border-radius:2px;"></span> 
                <span>排卵监测 (LH)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. 计算需要渲染的月份
        event_dates = sorted(events.keys())
        months_to_render = []
        if event_dates:
            first_date = event_dates[0]
            last_date = event_dates[-1]
            months_to_render.append((first_date.year, first_date.month))
            if (last_date.year > first_date.year) or (last_date.month > first_date.month):
                months_to_render.append((last_date.year, last_date.month))

        # 3. 渲染日历
        for y, m in months_to_render:
            cal_html = render_html_calendar(y, m, events)
            st.markdown(cal_html, unsafe_allow_html=True)
            
        # 4. 文字提示
        st.info(f"""
        **💡 检测指南：**
        1. **FSH+LH 双测**：**{event_dates[0].strftime('%m月%d日')}** (D2) 开始，晨尿监测 3 天。
        2. **LH 排卵监测**：**{lh_start_date.strftime('%m月%d日')}** 左右开始，直到测到强阳。
        """)