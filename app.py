import streamlit as st
import datetime
import calendar

# ================= 1. 配置与后台数据 =================
st.set_page_config(
    page_title="激素检测日历", 
    page_icon="🌸", 
    layout="centered"
)

# 模拟后台数据库 (静默匹配)
USER_DB = {
    "郝欣雅": 31,
    "王如琳": 37,
    "马明曦": 31
}

# ================= 2. 核心逻辑 (学术化/极简) =================

def get_testing_schedule(cycle_len, start_date):
    """
    分阶算法：基于生理周期倒推
    """
    events = {}
    
    # --- 阶段 1: 卵巢储备评估 (FSH + LH) ---
    # D2-D4
    for i in range(1, 4):
        d = start_date + datetime.timedelta(days=i)
        # 标签极简：只保留激素名
        events[d] = {"type": "BASE", "label": "FSH+LH"}

    # --- 阶段 2: 排卵节律监测 (LH) ---
    estimated_od_day = cycle_len - 14
    
    # 密集期 (Daily): OD-2 到 OD+2
    daily_start_day = estimated_od_day - 2
    daily_count = 5
    
    # 间隔期 (Interval): 倒推2个点
    eod_days = [daily_start_day - 4, daily_start_day - 2]
    
    # A. 间隔监测点
    for day_idx in eod_days:
        if day_idx < 1: continue 
        d = start_date + datetime.timedelta(days=day_idx - 1)
        
        if d in events:
            # 极简合并
            events[d]["label"] = "FSH+LH" 
            events[d]["type"] = "BOTH"
        else:
            events[d] = {"type": "EOD", "label": "LH"}

    # B. 密集监测点
    for i in range(daily_count):
        day_idx = daily_start_day + i
        d = start_date + datetime.timedelta(days=day_idx - 1)
        
        if d in events:
            events[d]["label"] = "FSH+LH"
            events[d]["type"] = "BOTH"
        else:
            events[d] = {"type": "DAILY", "label": "LH"}
            
    return events, (daily_start_day - 4)

# ================= 3. 自定义日历渲染组件 (极简风格) =================

def render_html_calendar(year, month, events):
    cal = calendar.monthcalendar(year, month)
    month_name = f"{year}年 {month}月"
    
    # CSS: 去除装饰，保持严谨、干净
    html = f"""
    <style>
        .calendar-card {{
            background-color: #ffffff;
            border-radius: 8px; /* 减小圆角幅度，更硬朗 */
            padding: 20px;
            margin-bottom: 25px;
            border: 1px solid #e0e0e0;
        }}
        .month-title {{ 
            font-size: 1.2em; font-weight: 600; margin-bottom: 15px; 
            color: #2c3e50; text-align: center; font-family: sans-serif;
        }}
        .cal-table {{ width: 100%; border-collapse: collapse; }}
        .cal-header td {{ 
            color: #666; font-size: 0.85em; font-weight: 600; text-align: center; 
            padding-bottom: 8px; border-bottom: 1px solid #eee;
        }}
        .cal-cell {{ 
            width: 14.2%; height: 85px; border-bottom: 1px solid #f0f0f0; 
            vertical-align: top; padding: 6px; font-size: 0.9em; 
            color: #333;
        }}
        .day-num {{ 
            font-weight: normal; color: #333; margin-bottom: 4px; display: block; 
            font-size: 0.9em;
        }}
        
        /* 极简标签: 只显示激素名，无多余文字 */
        .event-tag {{
            display: block; font-size: 0.7em; padding: 4px 0; border-radius: 4px;
            margin-top: 4px; color: #fff; text-align: center; font-weight: 500;
            width: 100%;
        }}
        
        /* 学术化配色: 降低饱和度，区分频率 */
        .evt-base {{ background-color: #5b8db8; }}   /* 沉稳蓝: FSH+LH */
        .evt-eod {{ background-color: #e0ac69; }}    /* 赭石色: 间隔LH */
        .evt-daily {{ background-color: #cd5c5c; }}  /* 印度红: 密集LH */
        .evt-both {{ background-color: #7b68ee; }}   /* 蓝紫色 */
        
        .empty {{ background-color: transparent; }}
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
                elif evt["type"] == "EOD": css_class = "evt-eod"
                elif evt["type"] == "DAILY": css_class = "evt-daily"
                else: css_class = "evt-both"
                
                # 修改：仅显示label(激素名)，不显示desc
                cell_content += f"<span class='event-tag {css_class}'>{evt['label']}</span>"
            
            html += f"<td class='cal-cell'>{cell_content}</td>"
        html += "</tr>"
    
    html += "</table></div>"
    return html

# ================= 4. 前端界面 =================

st.title("激素检测日历 🌸")

# --- 输入区 ---
with st.container(border=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        user_name = st.text_input("受测人姓名", placeholder="请输入姓名")
        default_cycle = 28
        if user_name:
            user_name_stripped = user_name.strip()
            if user_name_stripped in USER_DB:
                default_cycle = USER_DB[user_name_stripped]
        
        cycle_len = st.number_input("平均周期长度 (天)", value=default_cycle, min_value=21, max_value=45)

    with col2:
        # 修改：文案更为客观
        start_date = st.date_input("周期日第一天", datetime.date.today())

# --- 生成区 ---
if st.button("生成监测方案", type="primary"):
    if not user_name:
        st.error("请完善受测人信息")
    else:
        st.divider()
        events, lh_start_day_idx = get_testing_schedule(cycle_len, start_date)
        
        # 1. 顶部图例 (学术化表达)
        st.markdown("""
        <div style="display: flex; gap: 25px; margin-bottom: 20px; font-size: 0.85em; justify-content: center; color: #444;">
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="display:block;width:12px;height:12px;background:#5b8db8;border-radius:2px;"></span> 
                <span><b>基础值</b> (FSH+LH)</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="display:block;width:12px;height:12px;background:#e0ac69;border-radius:2px;"></span> 
                <span><b>LH 间隔监测</b> (每48h)</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="display:block;width:12px;height:12px;background:#cd5c5c;border-radius:2px;"></span> 
                <span><b>LH 密集监测</b> (每24h)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. 渲染日历
        event_dates = sorted(events.keys())
        months_to_render = []
        if event_dates:
            first_date = event_dates[0]
            last_date = event_dates[-1]
            months_to_render.append((first_date.year, first_date.month))
            if (last_date.year > first_date.year) or (last_date.month > first_date.month):
                months_to_render.append((last_date.year, last_date.month))

        for y, m in months_to_render:
            cal_html = render_html_calendar(y, m, events)
            st.markdown(cal_html, unsafe_allow_html=True)
            
        # 3. 规范化操作说明
        st.info("""
        **监测规范与意义说明**
        
        **1. 采样标准控制**
        为确保尿液激素浓度（Hormone Concentration）的可比性，请严格遵守以下采样要求：
        * **方案 A (推荐)：** 使用**晨尿**（First Morning Urine）进行检测，每日采样时间点应尽量一致。
        * **方案 B：** 若无法采集晨尿，请确保检测前 **2小时内限制饮水**，避免尿液稀释导致假阴性结果。
        
        **2. 阶段性监测目的**
        * **基础值监测 (FSH+LH)：** 评估卵巢储备功能及周期起始状态。
        * **间隔监测 (LH)：** 监测激素爬升趋势，建立个体基线。
        * **密集监测 (LH)：** 捕捉 LH 峰值（Surge），以验证排卵规律性及黄体生成机制的完整性。
        """)
