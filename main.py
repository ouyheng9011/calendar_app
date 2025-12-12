import flet as ft
from datetime import datetime
import time

# --- 1. 数据模型 (保持不变) ---
class TaskModel:
    def __init__(self, name, task_type, deadline_obj, streak=0):
        self.name = name
        self.task_type = task_type
        if isinstance(deadline_obj, str):
            self.deadline = datetime.strptime(deadline_obj, "%Y-%m-%d").date()
        else:
            self.deadline = deadline_obj.date()
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

# --- 主应用入口 ---
def main(page: ft.Page):
    # --- 页面基础设置 ---
    print(f"[{time.time()}] main() function started.")
    page.title = "我的计划通 v2.0"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 380
    page.window_height = 700
    print(f"[{time.time()}] Page settings configured.")

    # --- 初始数据和状态 ---
    tasks = [
        TaskModel("背单词", "daily", "2025-12-31", streak=5),
        TaskModel("准备妈妈生日礼物", "future", "2025-05-20"),
        TaskModel("去超市买牛奶", "temp", "2025-12-15"),
    ]
    selected_date_store = {"date": datetime.now()}
    print(f"[{time.time()}] Initial data loaded. Tasks count: {len(tasks)}")

    # --- UI 刷新和视图构建函数 ---
    def get_deadline_info(task):
        days = task.get_days_left()
        if days < 0: return f"已过期 {-days} 天", ft.colors.RED
        if days == 0: return "就是今天！", ft.colors.ORANGE
        return f"剩余 {days} 天", ft.colors.GREEN

    def refresh_ui(e=None):
        print(f"\n[{time.time()}] refresh_ui() triggered.")
        idx = nav_bar.selected_index
        print(f"[{time.time()}] Current navigation index: {idx}")
        views = [build_daily_view, build_future_view, build_temp_view]
        content_area.content = views[idx]()
        print(f"[{time.time()}] Content area updated with view: {views[idx].__name__}")
        page.update()
        print(f"[{time.time()}] page.update() called.")

    def build_daily_view():
        print(f"  -> Building 'daily' view...")
        items = []
        for t in tasks:
            if t.task_type == "daily":
                txt, col = get_deadline_info(t)
                def create_check_in_action(current_task=t):
                    def check_in_action(e):
                        print(f"    -- check_in_action for task '{current_task.name}'")
                        if current_task.check_in():
                            refresh_ui()
                    return check_in_action
                card = ft.Card(...) # 省略卡片内容以保持简洁
                items.append(card)
        print(f"  -> 'daily' view built with {len(items)} items.")
        return ft.ListView(items, expand=True, spacing=10)

    def build_future_view():
        print(f"  -> Building 'future' view...")
        items = []
        sorted_tasks = sorted([t for t in tasks if t.task_type == "future"], key=lambda x: x.get_days_left())
        for t in sorted_tasks:
            if t.get_days_left() >= 0:
                card = ft.Card(...) # 省略卡片内容
                items.append(card)
        print(f"  -> 'future' view built with {len(items)} items.")
        return ft.ListView(items, expand=True, spacing=10)

    def build_temp_view():
        print(f"  -> Building 'temp' view...")
        items = []
        for t in tasks:
            if t.task_type == "temp" and not t.is_completed:
                def create_finish_action(current_task=t):
                    def finish_action(e):
                        print(f"    -- finish_action for task '{current_task.name}'")
                        current_task.is_completed = True
                        refresh_ui()
                    return finish_action
                card = ft.Card(...) # 省略卡片内容
                items.append(card)
        print(f"  -> 'temp' view built with {len(items)} items.")
        return ft.ListView(items, expand=True, spacing=10)

    # --- 添加任务弹窗 (Dialog) ---
    # ... (弹窗相关的代码，和上一版一样，这里省略以保持清爽) ...
    def confirm_add_task(e):
        print(f"[{time.time()}] confirm_add_task() called.")
        # ... (内部逻辑) ...
        tasks.append(new_task)
        print(f"[{time.time()}] New task '{new_task.name}' added.")
        # ... (关闭弹窗等) ...

    def open_add_dialog(e):
        print(f"[{time.time()}] open_add_dialog() called.")
        page.dialog = dlg_add
        dlg_add.open = True
        page.update()

    # --- 主布局和导航 ---
    print(f"[{time.time()}] Setting up main layout components.")
    content_area = ft.Container(expand=True, padding=10)
    nav_bar = ft.NavigationBar(...) # 省略
    fab = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_dialog)

    # --- 页面初始化 ---
    print(f"[{time.time()}] Starting page initialization.")
    page.floating_action_button = fab
    page.navigation_bar = nav_bar
    print(f"[{time.time()}] FAB and NavBar assigned to page.")
    
    page.clean()
    print(f"[{time.time()}] page.clean() called.")
    page.add(content_area)
    print(f"[{time.time()}] Main content area added to page.")
    
    # 手动调用一次以加载初始视图
    print(f"[{time.time()}] Manually calling initial refresh_ui().")
    refresh_ui()
    print(f"[{time.time()}] main() function finished initialization.")

# --- 运行应用 ---
if __name__ == "__main__":
    print("Starting Flet app...")
    ft.app(target=main)
