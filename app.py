import streamlit as st
import datetime
import calendar

# ================= 1. 配置与后台数据 =================
st.set_page_config(
    page_title="CURV专属周期日历", 
    page_icon="🌸", 
    layout="centered"
)

# 模拟后台数据库 (静默匹配，界面上完全不可见)
USER_DB = {
    "郝欣雅": 31,
    "王如琳": 37,
    "马明曦": 31
}

# ================= 2. 核心逻辑 (隐形7根策略) =================

def get_testing_schedule(cycle_len, start_date):
    """
    智能分阶算法
    """
    events = {}
    
    # --- 阶段 1: 基础激素 (FSH + LH) ---
    for i in range(1, 4):
        d = start_date + datetime.timedelta(days=i)
        events[d] = {"type": "BASE", "label": "基础检测", "desc": "FSH+LH"}

    # --- 阶段 2: 排卵监测 ---
    estimated_od_day = cycle_len - 14
    
    # 核心期 (每天测): OD-2 到 OD+2
    daily_start_day = estimated_od_day - 2
    daily_count = 5
    
    # 爬升期 (隔天测): 倒推2个点
    eod_days = [daily_start_day - 4, daily_start_day - 2]
    
    # A. 爬升期 (关注期)
    for day_idx in eod_days:
        if day_idx < 1: continue 
        d = start_date + datetime.timedelta(days=day_idx - 1)
        
        if d in events:
            events[d]["label"] += " & 关注期"
            events[d]["type"] = "BOTH"
        else:
            events[d] = {"type": "EOD", "label": "LH 关注期", "desc": "隔天检测"}

    # B. 黄金期 (密集期)
    for i in range(daily_count):
        day_idx = daily_start_day + i
        d = start_date + datetime.timedelta(days=day_idx - 1)
        
        if d in events:
            events[d]["label"] += " & 黄金期"
            events[d]["type"] = "BOTH"
        else:
            events[d] = {"type": "DAILY", "label": "LH 黄金期", "desc": "每天检测"}
            
    return events, (daily_start_day - 4)

# ================= 3. 自定义日历渲染组件 (清新白主题) =================

def render_html_calendar(year, month, events):
    cal = calendar.monthcalendar(year, month)
    month_name = f"{year}年 {month}月"
    
    # CSS 样式: 柔和圆润风格
    html = f"""
    <style>
        .calendar-card {{
            background-color: #ffffff;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.04);
            border: 1px solid #f7f7f7;
        }}
        .month-title {{ 
            font-size: 1.5em; font-weight: 600; margin-bottom: 20px; 
            color: #333; text-align: center; letter-spacing: 1px;
        }}
        .cal-table {{ width: 100%; border-collapse: separate; border-spacing: 6px; }}
        .cal-header td {{ 
            color: #999; font-size: 0.9em; font-weight: 500; text-align: center; padding-bottom: 12px;
        }}
        .cal-cell {{ 
            width: 14.2%; height: 95px; border: 1px solid #f0f0f0; border-radius: 10px;
            vertical-align: top; padding: 8px; font-size: 0.95em; 
            background-color: #fafafa; transition: all 0.2s;
        }}
        .day-num {{ font-weight: 700; color: #555; margin-bottom: 6px; display: block; }}
        
        /* 胶囊标签 */
        .event-tag {{
            display: block; font-size: 0.75em; padding: 4px 2px; border-radius: 6px;
            margin-top: 5px; color: white; text-align: center; font-weight: 500; line-height: 1.4;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* 配色方案 */
        .evt-base {{ background-color: #74b9ff; }}   /* 清新蓝 */
        .evt-eod {{ background-color: #fab1a0; }}    /* 温暖橙 */
        .evt-daily {{ background-color: #ff7675; }}  /* 活力红 */
        .evt-both {{ background-color: #a29bfe; }}   /* 优雅紫 */
        
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
            bg_style = ""
            
            if current_date in events:
                evt = events[current_date]
                css_class = ""
                if evt["type"] == "BASE": css_class = "evt-base"
                elif evt["type"] == "EOD": css_class = "evt-eod"
                elif evt["type"] == "DAILY": css_class = "evt-daily"
                else: css_class = "evt-both"
                
                cell_content += f"<span class='event-tag {css_class}'>{evt['label']}<br><span style='font-size:0.85em;opacity:0.9'>{evt['desc']}</span></span>"
                bg_style = "style='background-color: #fff; border-color: #eee; box-shadow: inset 0 0 10px rgba(0,0,0,0.01);'"
            
            html += f"<td class='cal-cell' {bg_style}>{cell_content}</td>"
        html += "</tr>"
    
    html += "</table></div>"
    return html

# ================= 4. 前端界面 =================

st.title("CURV 专属周期日历 🌸")
st.markdown("👋 您好，请输入您的周期信息，我们将为您规划**最科学轻松**的检测节奏。")

# --- 输入区 (已去敏) ---
with st.container(border=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 修改点：移除了真实姓名示例，改为通用提示
        user_name = st.text_input("您的姓名", placeholder="请输入您的姓名")
        
        # 匹配逻辑保持不变，但在界面上无感知
        default_cycle = 28
        if user_name:
            user_name_stripped = user_name.strip()
            if user_name_stripped in USER_DB:
                default_cycle = USER_DB[user_name_stripped]
        
        cycle_len = st.number_input("平均月经周期 (天)", value=default_cycle, min_value=21, max_value=45, help="通常是两次月经第一天之间的间隔天数")

    with col2:
        start_date = st.date_input("下一次经期第一天 (预计来潮日)", datetime.date.today())

# --- 生成区 ---
if st.button("生成我的专属日历", type="primary"):
    if not user_name:
        st.error("请先填写姓名，以便为您生成专属计划。")
    else:
        st.divider()
        events, lh_start_day_idx = get_testing_schedule(cycle_len, start_date)
        
        # 1. 顶部图例
        st.markdown("""
        <div style="display: flex; gap: 20px; margin-bottom: 20px; font-size: 0.9em; justify-content: center; flex-wrap: wrap; color: #555;">
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="display:block;width:10px;height:10px;background:#74b9ff;border-radius:50%;"></span> 
                <span><b>基础检测</b> (了解卵巢机能)</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="display:block;width:10px;height:10px;background:#fab1a0;border-radius:50%;"></span> 
                <span><b>关注期</b> (隔天测·捕捉变化)</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="display:block;width:10px;height:10px;background:#ff7675;border-radius:50%;"></span> 
                <span><b>黄金期</b> (每天测·锁定排卵)</span>
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
            
        # 3. 贴心监测指南
        st.success(f"""
        **🌟 {user_name}，这是为您定制的本月监测计划：**
        
        1.  **月经期 (基础检测)**：请在 **D2-D4** 进行 FSH+LH 双测。这是了解您卵巢“仓库”储备量的最佳时机。
        2.  **爬升关注期 (LH)**：从 **D{lh_start_day_idx}** 开始，我们建议您**隔天检测**。这能帮您在不焦虑的情况下，敏锐捕捉激素的早期爬升信号。
        3.  **排卵黄金期 (LH)**：这是最关键的时刻！大约在 **D{lh_start_day_idx+4}** 左右，请务必**每天坚持检测**，直到捕捉到强阳峰值，精准锁定排卵日。
        
        ---
        **💧 温馨小贴士：**
        * **最佳时间**：建议在 **上午10:00 至 下午8:00** 之间检测，尽量保持每天同一时间。
        * **饮水建议**：检测前 **2小时** 请尽量少喝水，以免尿液稀释影响结果的精准度哦。
        """)
