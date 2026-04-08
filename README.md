# 会议录音转文字 - Android应用

## 使用方法

### 运行脚本：`clean_and_push.bat`

**只需运行这一个脚本！** 它会自动完成所有步骤。

---

## 脚本执行流程（4步）

| 步骤 | 操作 | 说明 |
|------|------|------|
| **Step 1** | 输入Token | 粘贴你的Personal Access Token |
| **Step 2** | 初始化Git | 自动配置账号 |
| **Step 3** | 提交+创建仓库 | 自动在GitHub创建仓库 |
| **Step 4** | 推送代码 | 推送后自动触发APK构建 |

---

## 如何查看构建进度

### 方法1：通过脚本输出
推送成功后，脚本会显示两个重要链接：
- **构建进度链接**
- **APK下载链接**

### 方法2：手动访问

#### 📊 查看构建进度
```
https://github.com/hui461007594-spec/meeting-recorder/actions
```
打开后会看到：
- ⏳ **黄色圆圈** = 正在构建中
- ✅ **绿色勾号** = 构建成功！APK已准备好
- ❌ **红色X号** = 构建失败（点击可看错误日志）

#### ⬇️ 下载APK
```
https://github.com/hui461007594-spec/meeting-recorder/releases
```
打开后：
1. 找到最新版本
2. 点击 `.apk` 文件下载
3. 传到手机安装

---

## 给同事用

**只发这个链接就行：**
```
https://github.com/hui461007594-spec/meeting-recorder/releases
```
同事每次点进去都是最新版APK。

---

## 后续迭代

修改代码后 → 再次运行 `clean_and_push.bat` → 等15分钟 → 下载新版APK

---

## 项目文件

```
音频转文字/
├── clean_and_push.bat   ⭐ 一键推送脚本
├── start_backend.bat    启动后端服务
├── start_web_app.bat    启动Web版
├── app.py               主应用代码
├── mobile_backend.py    后端服务
├── audio_to_text.py     语音转文字模块
├── meeting_processor.py 会议处理模块
├── web_mobile_app.py    Web版界面
├── requirements.txt     Python依赖
├── .env.example         环境变量示例
└── .gitignore           Git忽略规则
```
