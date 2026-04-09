"""
会议录音转文字 - 主应用
版本: 1.0.0
支持功能扩展和升级
"""

import flet as ft
import requests
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

APP_VERSION = "1.0.0"
APP_NAME = "会议录音转文字"


class ConfigManager:
    """配置管理器 - 支持保存和加载用户配置"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "api_url": "http://192.168.1.100:5000",
            "model": "base",
            "language": "zh",
            "theme": "light",
            "history": []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def update(self, key: str, value: Any):
        """更新配置"""
        self.config[key] = value
        self.save_config()


class APIClient:
    """API客户端 - 处理与服务器的通信"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def transcribe(self, audio_path: str, model: str = "base", language: str = "zh") -> Dict[str, Any]:
        """上传音频并获取转录结果"""
        url = f"{self.base_url}/api/transcribe"
        
        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            data = {
                'model': model,
                'language': language
            }
            response = requests.post(url, files=files, data=data, timeout=600)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API错误: {response.status_code} - {response.text}")
    
    def health_check(self) -> bool:
        """检查服务器连接"""
        try:
            url = f"{self.base_url}/api/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


class MeetingRecorderApp:
    """会议录音转文字应用主类"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.config_manager = ConfigManager()
        self.api_client = None
        
        self.setup_page()
        self.create_ui()
    
    def setup_page(self):
        """设置页面基本属性"""
        self.page.title = f"{APP_NAME} v{APP_VERSION}"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.spacing = 10
        self.page.scroll = ft.ScrollMode.AUTO
        
        # 设置窗口大小（桌面端）
        if self.page.platform in [ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS, ft.PagePlatform.LINUX]:
            self.page.window.width = 500
            self.page.window.height = 800
    
    def create_ui(self):
        """创建用户界面"""
        # 标题
        title = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.MIC, size=40, color=ft.colors.INDIGO),
                    ft.Text(APP_NAME, size=24, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_700),
                    ft.Text(f"版本 {APP_VERSION}", size=12, color=ft.colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=10),
        )
        
        # API设置
        self.api_url_field = ft.TextField(
            label="API服务器地址",
            value=self.config_manager.config.get("api_url", ""),
            hint_text="例如: http://192.168.1.100:5000",
            prefix_icon=ft.icons.DNS,
            on_change=self.on_api_url_change,
        )
        
        self.connection_status = ft.Text(
            "未连接",
            size=12,
            color=ft.colors.RED_400,
        )
        
        test_btn = ft.TextButton(
            "测试连接",
            icon=ft.icons.WIFI_FIND,
            on_click=self.test_connection,
        )
        
        api_section = ft.Container(
            content=ft.Column(
                [
                    ft.Row([ft.Text("服务器设置", size=14, weight=ft.FontWeight.BOLD)]),
                    self.api_url_field,
                    ft.Row([self.connection_status, test_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ],
                spacing=10,
            ),
            padding=10,
            bgcolor=ft.colors.GREY_50,
            border_radius=10,
        )
        
        # 模型设置
        self.model_dropdown = ft.Dropdown(
            label="Whisper模型",
            value=self.config_manager.config.get("model", "base"),
            options=[
                ft.dropdown.Option("tiny", "tiny - 最快"),
                ft.dropdown.Option("base", "base - 推荐"),
                ft.dropdown.Option("small", "small - 较准"),
                ft.dropdown.Option("medium", "medium - 准确"),
            ],
            on_change=self.on_model_change,
        )
        
        self.language_dropdown = ft.Dropdown(
            label="识别语言",
            value=self.config_manager.config.get("language", "zh"),
            options=[
                ft.dropdown.Option("zh", "中文"),
                ft.dropdown.Option("en", "英文"),
                ft.dropdown.Option("auto", "自动检测"),
            ],
            on_change=self.on_language_change,
        )
        
        settings_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text("识别设置", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([self.model_dropdown, self.language_dropdown]),
                ],
                spacing=10,
            ),
            padding=10,
        )
        
        # 文件选择
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)
        
        self.selected_file_text = ft.Text("未选择文件", size=13, color=ft.colors.GREY)
        self.selected_file_path: Optional[str] = None
        
        file_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text("音频文件", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "选择录音文件",
                                icon=ft.icons.AUDIO_FILE,
                                on_click=lambda _: self.file_picker.pick_files(
                                    allowed_extensions=["mp3", "wav", "m4a", "flac", "ogg", "3gp", "amr", "aac"],
                                    file_type=ft.FilePickerFileType.CUSTOM,
                                ),
                            ),
                            self.selected_file_text,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=10,
            ),
            padding=10,
        )
        
        # 处理按钮
        self.process_btn = ft.ElevatedButton(
            "开始处理",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.process_audio,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.INDIGO_600,
                color=ft.colors.WHITE,
            ),
            width=float("inf"),
            height=50,
        )
        
        # 状态显示
        self.status_text = ft.Text(
            "准备就绪",
            size=14,
            color=ft.colors.GREY_600,
        )
        
        # 结果显示
        self.transcript_field = ft.TextField(
            label="转录文本",
            multiline=True,
            min_lines=6,
            max_lines=15,
            read_only=True,
            expand=True,
        )
        
        self.minutes_field = ft.TextField(
            label="会议记录",
            multiline=True,
            min_lines=6,
            max_lines=15,
            read_only=True,
            expand=True,
        )
        
        self.todos_field = ft.TextField(
            label="待办事项",
            multiline=True,
            min_lines=6,
            max_lines=15,
            read_only=True,
            expand=True,
        )
        
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="转录文本", content=ft.Container(content=self.transcript_field, padding=5)),
                ft.Tab(text="会议记录", content=ft.Container(content=self.minutes_field, padding=5)),
                ft.Tab(text="待办事项", content=ft.Container(content=self.todos_field, padding=5)),
            ],
            expand=True,
        )
        
        # 操作按钮
        save_btn = ft.OutlinedButton(
            "保存结果",
            icon=ft.icons.SAVE,
            on_click=self.save_results,
            width=float("inf"),
        )
        
        copy_btn = ft.OutlinedButton(
            "复制全部",
            icon=ft.icons.COPY,
            on_click=self.copy_results,
            width=float("inf"),
        )
        
        # 组装界面
        self.page.add(
            title,
            api_section,
            settings_section,
            file_section,
            self.process_btn,
            ft.Container(content=self.status_text, padding=ft.padding.only(left=10)),
            ft.Container(content=self.tabs, padding=5, height=350),
            ft.Row([save_btn, copy_btn]),
            self.create_about_section(),
        )
    
    def create_about_section(self) -> ft.Container:
        """创建关于部分"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Divider(),
                    ft.Text("使用说明", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text("1. 在电脑上运行后端服务", size=11, color=ft.colors.GREY_600),
                    ft.Text("2. 输入电脑IP地址并测试连接", size=11, color=ft.colors.GREY_600),
                    ft.Text("3. 选择手机中的录音文件", size=11, color=ft.colors.GREY_600),
                    ft.Text("4. 点击开始处理，等待结果", size=11, color=ft.colors.GREY_600),
                    ft.Divider(),
                    ft.Text(f"© 2024 {APP_NAME} v{APP_VERSION}", size=10, color=ft.colors.GREY_400),
                ],
            ),
            padding=10,
        )
    
    def on_api_url_change(self, e):
        """API地址改变时"""
        self.config_manager.update("api_url", e.control.value)
        self.api_client = APIClient(e.control.value)
    
    def on_model_change(self, e):
        """模型改变时"""
        self.config_manager.update("model", e.control.value)
    
    def on_language_change(self, e):
        """语言改变时"""
        self.config_manager.update("language", e.control.value)
    
    def test_connection(self, e):
        """测试服务器连接"""
        url = self.api_url_field.value.strip()
        if not url:
            self.connection_status.value = "请输入地址"
            self.connection_status.color = ft.colors.RED_400
            self.page.update()
            return
        
        self.connection_status.value = "测试中..."
        self.connection_status.color = ft.colors.BLUE_400
        self.page.update()
        
        self.api_client = APIClient(url)
        if self.api_client.health_check():
            self.connection_status.value = "连接成功 ✓"
            self.connection_status.color = ft.colors.GREEN_600
        else:
            self.connection_status.value = "连接失败 ✗"
            self.connection_status.color = ft.colors.RED_600
        
        self.page.update()
    
    def on_file_selected(self, e: ft.FilePickerResultEvent):
        """文件选择后"""
        if e.files and len(e.files) > 0:
            self.selected_file_path = e.files[0].path
            self.selected_file_text.value = f"已选择: {e.files[0].name}"
            self.selected_file_text.color = ft.colors.GREEN_700
            self.status_text.value = "文件已就绪，点击开始处理"
        else:
            self.selected_file_path = None
            self.selected_file_text.value = "未选择文件"
            self.selected_file_text.color = ft.colors.GREY
        self.page.update()
    
    def process_audio(self, e):
        """处理音频"""
        if not self.selected_file_path:
            self.show_error("请先选择音频文件")
            return
        
        url = self.api_url_field.value.strip()
        if not url:
            self.show_error("请输入API服务器地址")
            return
        
        self.process_btn.disabled = True
        self.status_text.value = "正在处理中，请稍候..."
        self.status_text.color = ft.colors.BLUE_700
        self.page.update()
        
        try:
            if not self.api_client:
                self.api_client = APIClient(url)
            
            result = self.api_client.transcribe(
                self.selected_file_path,
                self.model_dropdown.value,
                self.language_dropdown.value
            )
            
            if result.get("success"):
                self.transcript_field.value = result.get("transcript", "")
                self.minutes_field.value = result.get("minutes", "")
                self.todos_field.value = result.get("todos", "")
                self.status_text.value = "处理完成！"
                self.status_text.color = ft.colors.GREEN_700
            else:
                self.show_error(f"处理失败: {result.get('error', '未知错误')}")
        
        except Exception as ex:
            self.show_error(f"错误: {str(ex)}")
        
        finally:
            self.process_btn.disabled = False
            self.page.update()
    
    def save_results(self, e):
        """保存结果"""
        content = f"""会议录音转文字 - 结果报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

【转录文本】
{self.transcript_field.value}

{'='*50}

【会议记录】
{self.minutes_field.value}

{'='*50}

【待办事项】
{self.todos_field.value}
"""
        
        if not self.transcript_field.value and not self.minutes_field.value and not self.todos_field.value:
            self.show_error("没有可保存的内容")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_result_{timestamp}.txt"
        
        try:
            # 移动端保存到Documents目录
            if self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
                save_path = os.path.join("/storage/emulated/0/Documents", filename)
            else:
                save_path = os.path.join(os.path.expanduser("~"), "Documents", filename)
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.status_text.value = f"已保存: {filename}"
            self.status_text.color = ft.colors.GREEN_700
        except Exception as ex:
            self.show_error(f"保存失败: {str(ex)}")
        
        self.page.update()
    
    def copy_results(self, e):
        """复制结果到剪贴板"""
        content = f"""【转录文本】
{self.transcript_field.value}

【会议记录】
{self.minutes_field.value}

【待办事项】
{self.todos_field.value}"""
        
        self.page.set_clipboard(content)
        self.status_text.value = "已复制到剪贴板"
        self.status_text.color = ft.colors.GREEN_700
        self.page.update()
    
    def show_error(self, message: str):
        """显示错误信息"""
        self.status_text.value = message
        self.status_text.color = ft.colors.RED_700
        self.page.update()


def main(page: ft.Page):
    """应用入口"""
    app = MeetingRecorderApp(page)


if __name__ == "__main__":
    ft.run(target=main)
