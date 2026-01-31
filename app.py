import streamlit as st
import datetime
import calendar

# ================= 1. 配置与后台数据 =================
st.set_page_config(page_title="Curv 周期监测日历", page_icon="📅", layout="centered")

# 模拟后台数据库 (已移除所有引用标记)
# 历史数据推算的平均周期
USER_DB = {
    "郝欣雅": 31,
    "王如琳": 37,
    "马明曦": 31
}

# LH 监测对照表
# (周期下限, 周期上限, 开始天数, 持续天数)
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
    """
    生成具体的检测日期字典
    Key: Date对象, Value: 检测项目描述
    """
    events = {}
    
    # --- 阶段 1: 基础激素 (FSH + LH) ---
    # 规则: Day 2 - Day 4 (共3天)
    for i in range(1, 4): # D2, D3, D4
        d = start_date + datetime.timedelta(days=i)
        events[d] = {"type": "BASE", "label": "FSH + LH", "desc": "基础值"}

    # --- 阶段 2: 排卵监测 (LH) ---
    # 查表确定开始时间和持续时间
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
        lh_duration = 10 # 兜底策略

    # 生成 LH 日期
    lh_start_date = start_date + datetime.timedelta(days=lh_start_day - 1)
    for i in range(lh_duration):
        d = lh_start_date + datetime.timedelta(days=i)
        # 如果和基础期重叠(极短周期情况)，合并显示，否则添加
        if d in events:
            events[d]["label"] += " & LH排卵"
            events[d]["type"] = "BOTH"
        else:
            events[d] = {"type": "OVULATION", "label": "LH (排卵)", "desc": "排卵监测"}
            
    return events, lh_start_date

# ================= 3. 自定义日历渲染组件 =================

def render_html_calendar(year, month, events):
    """
    生成带有高亮事件的 HTML 日历
    """
    cal = calendar.monthcalendar(year, month)
    month_name = f"{year}年 {month}月"
    
    # CSS 样式
    html = f"""
    <style>
        .calendar-container {{ margin-bottom: 20px; font-family: sans-serif; }}
        .month-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #333; }}
        .cal-table {{ width: 100%; border-collapse: collapse; }}
        .cal-header {{ background-color: #f0f2f6; color: #666; font-size: 0.9em; }}
        .cal-cell {{ 
            width: 14.2%; height: 80px; border: 1px solid #e0e0e0; 
            vertical-align: top; padding: 5px; font-size: 0.9em; position: relative;
        }}
        .day-num {{ font-weight: bold; color: #444; margin-bottom: 4px; display: block; }}
        
        /* 事件样式 */
        .event-tag {{
            display: block; font-size: 0.75em; padding: 2px 4px; border-radius: 4px;
            margin-top: 2px; color: white; text-align: center;
        }}
        .evt-base {{ background-color: #4A90E2; }} /* 蓝色: FSH+LH */
        .evt-ovu {{ background-color: #FF6B6B; }} /* 红色: LH排卵 */
        .evt-both {{ background-color: #9B51E0; }} /* 紫色: 重叠 */
        .empty {{ background-color: #fafafa; }}
    </style>
    <div class="calendar-container">
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
            bg_style = ""
            
            if current_date in events:
                evt = events[current_date]
                css_class = ""
                if evt["type"] == "BASE": css_class = "evt-base"
                elif evt["type"] == "OVULATION": css_class = "evt-ovu"
                else: css_class = "evt-both"
                
                cell_content += f"<span class='event-tag {css_class}'>{evt['label']}</span>"
            
            html += f"<td class='cal-cell' {bg_style}>{cell_content}</td>"
        html += "</tr>"
    
    html += "</table></div>"
    return html

# ================= 4. 前端界面 =================

st.title("Curv 智能检测日历 🗓️")
st.markdown("请输入您的基本信息，生成本周期的 **FSH** 与 **LH** 专属检测日历。")

# --- 输入区 (隐私保护: 填空而非选择) ---
with st.container(border=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 1. 输入姓名
        user_name = st.text_input("请输入姓名", placeholder="例如：张三")
        
        # 2. 自动匹配周期逻辑
        default_cycle = 28
        if user_name:
            user_name = user_name.strip()
            if user_name in USER_DB:
                default_cycle = USER_DB[user_name]
                st.caption(f"✅ 已识别档案，平均周期: {default_cycle}天")
            else:
                st.caption("ℹ️ 新用户或无历史数据，请手动确认周期")
        
        # 3. 周期确认 (允许用户修改)
        cycle_len = st.number_input("平均月经周期 (天)", value=default_cycle, min_value=20, max_value=45)

    with col2:
        start_date = st.date_input("本次月经第一天 (见红日)", datetime.date.today())

# --- 生成区 ---
if st.button("生成我的检测日历", type="primary"):
    if not user_name:
        st.error("请先输入姓名")
    else:
        st.divider()
        
        # 获取事件数据
        events, lh_start_date = get_testing_schedule(cycle_len, start_date)
        
        # 1. 顶部图例
        st.markdown("""
        <div style="display: flex; gap: 15px; margin-bottom: 10px; font-size: 0.9em;">
            <div><span style="display:inline-block;width:12px;height:12px;background:#4A90E2;border-radius:2px;"></span> <b>基础检测 (FSH+LH)</b></div>
            <div><span style="display:inline-block;width:12px;height:12px;background:#FF6B6B;border-radius:2px;"></span> <b>排卵监测 (LH)</b></div>
        </div>
        """, unsafe_allow_html=True)

        # 2. 计算需要渲染的月份
        # 找出事件涉及的所有月份
        event_dates = sorted(events.keys())
        months_to_render = []
        if event_dates:
            first_date = event_dates[0]
            last_date = event_dates[-1]
            
            # 当前月
            months_to_render.append((first_date.year, first_date.month))
            # 如果跨月了，添加下个月
            if (last_date.year > first_date.year) or (last_date.month > first_date.month):
                months_to_render.append((last_date.year, last_date.month))

        # 3. 渲染日历
        for y, m in months_to_render:
            cal_html = render_html_calendar(y, m, events)
            st.markdown(cal_html, unsafe_allow_html=True)
            
        # 4. 文字提示
        st.info(f"""
        **💡 关键提示：**
        1. **FSH+LH 双测**：请在 **{event_dates[0].strftime('%m月%d日')}** (D2) 开始，晨尿监测 3 天。
        2. **LH 排卵监测**：请在 **{lh_start_date.strftime('%m月%d日')}** 左右开始，每天同一时间测试，直到测到强阳。
        """)