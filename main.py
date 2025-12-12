import flet as ft
from datetime import datetime


# --- 1. 数据模型 (稍微修改以适应动态添加) ---
class TaskModel:
    def __init__(self, name, task_type, deadline_obj, streak=0):
        self.name = name
        self.task_type = task_type  # 对应下拉菜单的选项值
        # 这里直接接收 datetime 对象，或者字符串
        if isinstance(deadline_obj, str):
            self.deadline = datetime.strptime(deadline_obj, "%Y-%m-%d").date()
        else:
            self.deadline = deadline_obj.date()  # 如果是datetime对象直接转date

        self.streak = streak
        self.last_check_in = None
        self.is_completed = False

    def get_days_left(self):
        today = datetime.now().date()
        delta = self.deadline - today
        return delta.days

    def check_in(self):
        today = datetime.now().date()
        if self.last_check_in != today:
            self.streak += 1
            self.last_check_in = today
            return True
        return False


def main(page: ft.Page):
    page.title = "我的计划通 v2.0"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 380
    page.window_height = 700

    # 初始数据
    tasks = [
        TaskModel("背单词", "daily", "2025-12-31", streak=5),
        TaskModel("妈妈生日", "future", "2025-05-20"),
    ]

    # --- 2. 核心功能：添加任务的弹窗逻辑 ---

    # 临时变量，用来存用户选中的日期
    selected_date_store = {"date": datetime.now()}

    # 2.1 日历选择器 (DatePicker)
    def handle_date_change(e):
        # 用户选好日期后，更新临时变量，并修改界面上显示的文字
        selected_date_store["date"] = e.control.value
        btn_date_select.text = e.control.value.strftime("%Y-%m-%d")
        btn_date_select.update()

    date_picker = ft.DatePicker(
        first_date=datetime(2023, 10, 1),
        last_date=datetime(2030, 10, 1),
        on_change=handle_date_change
    )
    # 必须把 date_picker 加到页面覆盖层里，否则弹不出来
    page.overlay.append(date_picker)

    # 2.2 输入控件
    input_name = ft.TextField(label="任务名称", hint_text="例如：每天跑步")

    # 任务类型下拉框
    input_type = ft.Dropdown(
        label="任务类型",
        options=[
            ft.dropdown.Option("daily", "每日打卡"),
            ft.dropdown.Option("future", "未来大事"),
            ft.dropdown.Option("temp", "临时任务"),
        ],
        value="daily"  # 默认选中第一个
    )

    # 显示日期的按钮
    btn_date_select = ft.ElevatedButton(
        "点击选择截止日期",
        icon=ft.icons.CALENDAR_MONTH,
        on_click=lambda _: date_picker.pick_date()  # 点击触发日历
    )

    # 2.3 确认添加按钮的逻辑
    def confirm_add_task(e):
        if not input_name.value:
            input_name.error_text = "名字不能为空"
            input_name.update()
            return

        # 创建新任务
        new_task = TaskModel(
            name=input_name.value,
            task_type=input_type.value,
            deadline_obj=selected_date_store["date"]
        )

        tasks.append(new_task)  # 加入列表

        # 关闭弹窗
        dlg_add.open = False
        page.update()

        # 刷新页面显示新任务
        refresh_ui()

        # 清空输入框以便下次使用
        input_name.value = ""
        btn_date_select.text = "点击选择截止日期"
        page.show_snack_bar(ft.SnackBar(ft.Text("添加成功！")))

    # 2.4 定义弹窗 (Dialog)
    dlg_add = ft.AlertDialog(
        title=ft.Text("添加新任务"),
        content=ft.Column([
            input_name,
            input_type,
            ft.Text("截止日期:", size=12, color="grey"),
            btn_date_select,
        ], height=200, tight=True),  # tight=True 让高度自适应
        actions=[
            ft.TextButton("取消", on_click=lambda e: page.close(dlg_add)),
            ft.ElevatedButton("确定添加", on_click=confirm_add_task),
        ],
    )

    # 打开弹窗的函数
    def open_add_dialog(e):
        page.open(dlg_add)

    # --- 3. 界面显示逻辑 (和之前类似，稍作优化) ---

    def get_deadline_info(task):
        days = task.get_days_left()
        if days < 0: return f"过期 {-days} 天", ft.colors.RED
        if days == 0: return "就是今天！", ft.colors.ORANGE
        return f"剩余 {days} 天", ft.colors.GREEN

    def build_daily_view():
        items = []
        for t in tasks:
            if t.task_type == "daily":
                txt, col = get_deadline_info(t)

                # 使用闭包或者默认参数来绑定当前的 task 对象
                def check_in_action(e, current_task=t):
                    if current_task.check_in():
                        e.control.icon = ft.icons.CHECK_CIRCLE
                        e.control.icon_color = ft.colors.GREEN
                        e.control.disabled = True
                        refresh_ui()

                card = ft.Card(content=ft.Container(padding=15, content=ft.Row([
                    ft.Column([
                        ft.Text(t.name, size=18, weight="bold"),
                        ft.Text(f"{t.deadline} ({txt})", size=12, color=col)
                    ], expand=True),
                    ft.Column([
                        ft.IconButton(ft.icons.CIRCLE_OUTLINED, on_click=check_in_action),
                        ft.Text(f"坚持 {t.streak} 天", size=10)
                    ])
                ])))
                items.append(card)
        return ft.ListView(items, expand=True)

    def build_future_view():
        items = []
        # 排序
        sorted_tasks = sorted([t for t in tasks if t.task_type == "future"], key=lambda x: x.get_days_left())
        for t in sorted_tasks:
            days = t.get_days_left()
            card = ft.Card(color=ft.colors.BLUE_50, content=ft.Container(padding=20, content=ft.Row([
                ft.Column([ft.Text(f"{days}", size=30, weight="bold", color=ft.colors.BLUE), ft.Text("天后", size=12)]),
                ft.VerticalDivider(width=20),
                ft.Column([ft.Text(t.name, size=18, weight="bold"), ft.Text(f"目标: {t.deadline}", size=12)],
                          alignment="center")
            ])))
            items.append(card)
        return ft.ListView(items, expand=True)

    def build_temp_view():
        items = []
        for t in tasks:
            if t.task_type == "temp" and not t.is_completed:
                txt, col = get_deadline_info(t)

                def finish_action(e, current_task=t):
                    current_task.is_completed = True
                    refresh_ui()

                card = ft.Card(content=ft.Container(padding=10, content=ft.Row([
                    ft.Checkbox(label=t.name, on_change=finish_action),
                    ft.Text(txt, color=col, size=12)
                ], alignment="spaceBetween")))
                items.append(card)
        return ft.ListView(items, expand=True)

    # --- 4. 主布局 ---
    content_area = ft.Container(expand=True)

    def refresh_ui():
        idx = nav_bar.selected_index
        content_area.content = [build_daily_view, build_future_view, build_temp_view][idx]()
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.CALENDAR_TODAY, label="每日"),
            ft.NavigationDestination(icon=ft.icons.ROCKET_LAUNCH, label="未来"),
            ft.NavigationDestination(icon=ft.icons.LIST_ALT, label="临时"),
        ],
        on_change=lambda e: refresh_ui()
    )

    # 绑定加号按钮到打开弹窗函数
    fab = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_dialog)

    page.add(ft.Column([content_area], expand=True), nav_bar)
    page.floating_action_button = fab
    refresh_ui()


ft.app(target=main)