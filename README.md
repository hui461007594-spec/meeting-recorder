# 会议录音转文字 - Android应用

一个Android应用，支持会议录音转文字、生成会议记录和提取待办事项。

---

## 使用方法

### 双击运行：`push_to_github.bat`

**首次运行时需要输入一次Token**（之后自动保存）：

1. 脚本会提示输入：
   - **Username**: `hui461007594-spec`
   - **Password**: 粘贴你的Personal Access Token

2. 输入后Git会安全保存凭据
3. 后续运行无需再次输入

---

## 获取APK

推送成功后等 **15-20分钟**：

```
https://github.com/hui461007594-spec/meeting-recorder/releases
```

**把这个链接发给同事！**

---

## 后续迭代

修改代码后 → 双击 `push_to_github.bat` → 等15分钟 → 下载新版APK

---

## 项目文件

| 文件 | 用途 |
|------|------|
| **push_to_github.bat** | ⭐ 一键推送（只需运行这个） |
| start_backend.bat | 启动后端服务 |
| start_web_app.bat | 启动Web版 |
| app.py | 主应用代码 |

---

## 常见问题

**Q: 为什么不能把Token写在脚本里？**
A: GitHub会检测代码中的secrets并阻止推送。这是安全保护。

**Q: Token只需要输入一次？**
A: 是的！Git会把凭据保存在本地（`~/.git-credentials`），后续自动使用。

**Q: 推送失败怎么办？**
A: 检查Token是否正确，重新运行脚本即可。
