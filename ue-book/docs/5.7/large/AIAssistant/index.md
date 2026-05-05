# AI Assistant

> 

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（SVG 图标、PNG 图标） |
| 模块 | `AIAssistant` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AIAssistant) | |

## 用途

AI Assistant 是 Epic 为 Unreal Editor 打造的内置 AI 聊天助手。它在编辑器中嵌入一个 Web Browser 面板，通过 JavaScript 桥接与 Epic 的 AI 后端服务通信，为开发者提供对话式 AI 辅助。

核心能力：
- **对话式 AI 交互**：在编辑器内直接与 AI 助手聊天，询问引擎使用、蓝图逻辑、代码问题等
- **Slate UI 上下文查询**：快捷键触发，自动捕获鼠标下方的 Slate 控件信息（类型、路径、tooltip、所属窗口等），发送给 AI 让它知道你在看什么
- **Python 代码执行**：AI 可以通过 JavaScript→C++ 桥接调用 Python 脚本，在编辑器中执行自动化操作
- **UEFN 模式**：支持切换 UE / UEFN（Unreal Editor for Fortnite）两种 AI 助手配置，为不同环境提供针对性回答
- **Panel Drawer 集成**：通过状态栏 "Ask AI" 按钮或快捷键，以面板抽屉形式快速召唤 AI 助手

## 使用场景

- 你在编辑器中看到一个不认识的按钮或菜单项 → 用 Slate Query 快捷键让 AI 告诉你它的用途
- 你需要写一段 Python 脚本自动化编辑器操作 → 让 AI 生成并直接执行
- 你在写蓝图卡住了 → 打开 AI Assistant 面板，描述问题获取建议
- 你在用 UEFN 开发 → 切换到 UEFN 模式获取 Fortnite 专属上下文的回答

## 架构概览

```
┌─────────────────────────────────────────────────┐
│                Unreal Editor                     │
│                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ StatusBar │  │ Input        │  │ Slate      │ │
│  │ "Ask AI"  │  │ Processor    │  │ Querier    │ │
│  └─────┬─────┘  └──────┬───────┘  └─────┬──────┘ │
│        │               │                │        │
│  ┌─────▼───────────────▼────────────────▼──────┐ │
│  │         FAIAssistantModule                   │ │
│  │  (Commands, Tab, Style, Menu Registration)   │ │
│  └─────────────────┬───────────────────────────┘ │
│                    │                              │
│  ┌─────────────────▼───────────────────────────┐ │
│  │       UAIAssistantSubsystem                  │ │
│  │  (Blueprint exposed, Python execution)       │ │
│  └─────────────────┬───────────────────────────┘ │
│                    │                              │
│  ┌─────────────────▼───────────────────────────┐ │
│  │     SAIAssistantWebBrowser (Slate Widget)    │ │
│  │  ┌─────────────────────────────────────────┐ │ │
│  │  │  SWebBrowser (Chromium Embedded)        │ │ │
│  │  │  ←→ JavaScript ↔ C++ Bridge            │ │ │
│  │  └─────────────────────────────────────────┘ │ │
│  └─────────────────┬───────────────────────────┘ │
│                    │                              │
│  ┌─────────────────▼───────────────────────────┐ │
│  │     FWebApplication → FWebApi               │ │
│  │  (Conversation management, Agent Environment │ │
│  │   JSON API ↔ JavaScript execution)          │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────┘
                       │ HTTPS
                       ▼
              Epic AI Backend Service
```

### 核心组件

| 组件 | 文件 | 职责 |
|---|---|---|
| `FAIAssistantModule` | AIAssistant.h/.cpp | 模块入口，注册 Tab、菜单、快捷键、输入处理器 |
| `UAIAssistantSubsystem` | AIAssistantSubsystem.h/.cpp | EditorSubsystem，暴露给蓝图和 JavaScript 的接口 |
| `SAIAssistantWebBrowser` | AIAssistantWebBrowser.h/.cpp | Slate 控件，嵌入 Web 浏览器承载 AI 前端 |
| `FWebApplication` | AIAssistantWebApplication.h/.cpp | Web 应用生命周期管理，页面加载状态，Agent Environment 配置 |
| `FWebApi` | AIAssistantWebApi.h/.cpp | 与 AI 后端的 JavaScript API 通信层 |
| `FAIAssistantSlateQuerier` | AIAssistantSlateQuerier.h/.cpp | Slate 控件分析器，构建上下文查询 |
| `FAIAssistantConfig` | AIAssistantConfig.h/.cpp | JSON 配置文件加载（主 URL 等） |
| `FExecuteWhenReady` | AIAssistantExecuteWhenReady.h/.cpp | 通用的延迟执行框架，等待条件就绪后执行队列 |
| `FConversationReadyExecutor` | AIAssistantConversationReadyExecutor.h/.cpp | 对话就绪执行器，排队消息直到对话创建完成 |
| `FAIAssistantInputProcessor` | AIAssistantInputProcessor.h/.cpp | 全局 Slate 输入处理器，确保快捷键始终有效 |
| `FAIAssistantConsole` | AIAssistantConsole.h/.cpp | UEFN 模式 ConsoleVariable 管理 |
| PythonExecutor | AIAssistantPythonExecutor.h/.cpp | Python 脚本执行封装 |
| `FAIAssistantStyle` | AIAssistantStyle.h/.cpp | Slate 样式和图标注册 |
| `FAIAssistantCommands` | AIAssistantCommands.h/.cpp | 编辑器命令定义 |

### JavaScript ↔ C++ 桥接

AI Assistant 的核心交互模式是 **Web 浏览器中的 JavaScript 与 UE C++ 之间的双向通信**：

| 接口 | 文件 | 说明 |
|---|---|---|
| `IWebJavaScriptExecutor` | AIAssistantWebJavaScriptExecutor.h | 执行 JavaScript 代码的接口 |
| `IWebJavaScriptDelegateBinder` | AIAssistantWebJavaScriptDelegateBinder.h | 将 UObject 绑定到 JavaScript（`window.ue.{name}`） |
| `UAIAssistantWebJavaScriptResultDelegate` | AIAssistantWebJavaScriptResultDelegate.h | JavaScript 函数返回结果到 C++ 的回调 |

JavaScript 调用 C++ 的方式：绑定 `UAIAssistantSubsystem` 后，JavaScript 可以调用 `window.ue.aiassistantsubsystem.executepythonscriptviajavascript(code)` 等函数（注意：必须全小写）。

## 蓝图用法

> ⚠️ 注意：此插件为 EditorNoCommandlet 类型，仅在编辑器中可用，不可打包到运行时。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecutePythonScriptViaJavaScript` | 执行 Python 脚本并返回输出字符串 | `UAIAssistantSubsystem` |
| `ShowContextMenuViaJavaScript` | 在指定位置显示右键菜单（Copy 等） | `UAIAssistantSubsystem` |

### 使用示例（蓝图描述）

由于 AI Assistant 主要通过编辑器 UI 和 JavaScript 层交互，蓝图层面的直接使用较少。主要的蓝图交互方式：

1. 获取 Subsystem：`Get Editor Subsystem` → `UAIAssistantSubsystem`
2. 调用 `ExecutePythonScriptViaJavaScript` 传入 Python 代码字符串
3. 返回值为执行输出，可用于日志或进一步处理

## C++ 用法

### 头文件引入

```cpp
#include "AIAssistantSubsystem.h"    // Subsystem 接口
#include "AIAssistantWebApi.h"       // Web API 层
#include "AIAssistantWebBrowser.h"   // Web 浏览器控件
#include "AIAssistantSlateQuerier.h" // Slate 查询
```

### 基本用法 — 通过 Subsystem 执行 Python

```cpp
// 获取 AI Assistant Subsystem
UAIAssistantSubsystem* Subsystem = GEditor->GetEditorSubsystem<UAIAssistantSubsystem>();
if (Subsystem)
{
    // 执行 Python 脚本
    FString Output = Subsystem->ExecutePythonScriptViaJavaScript(TEXT("import unreal; print('Hello')"));
    UE_LOG(LogTemp, Log, TEXT("Python Output: %s"), *Output);
}
```

来源: `AIAssistantSubsystem.cpp`

### 进阶用法 — Web API 对话管理

```cpp
using namespace UE::AIAssistant;

// 创建 WebApi 实例（通常由 FWebApplication 管理）
TSharedPtr<FWebApi> WebApi = FWebApplication::CreateWebApiFactory(
    JavaScriptExecutor, JavaScriptDelegateBinder)();

// 检查 API 是否可用
TFuture<TValueOrError<FWebApiBoolResult, FString>> AvailableFuture = WebApi->IsAvailable();

// 创建新对话
TFuture<TValueOrError<void, FString>> ConversationFuture = WebApi->CreateConversation();

// 发送消息
FAddMessageToConversationOptions Options;
Options.Message.MessageRole = EMessageRole::User;
FMessageContent Content;
Content.ContentType = EMessageContentType::Text;
FTextMessageContent TextContent;
TextContent.Text = TEXT("How do I create a blueprint?");
Content.Content.Set<FTextMessageContent>(TextContent);
Options.Message.MessageContent.Add(Content);
WebApi->AddMessageToConversation(Options);
```

来源: `AIAssistantWebApi.h`

### 进阶用法 — Slate 上下文查询

```cpp
// 获取鼠标下方的控件路径
FWidgetPath WidgetPath = UE::AIAssistant::SlateQuerier::GetWidgetPathUnderCursor();

if (WidgetPath.IsValid())
{
    // 向 AI 助手发送查询，描述该控件
    UE::AIAssistant::SlateQuerier::QueryAIAssistantAboutSlateWidget(WidgetPath);
}
```

来源: `AIAssistantSlateQuerier.h`

### 进阶用法 — 延迟执行框架

```cpp
using namespace UE::AIAssistant;

// 继承 FExecuteWhenReady 来创建需要等待就绪的组件
class FMyComponent : public FExecuteWhenReady
{
public:
    EExecuteWhenReadyState GetExecuteWhenReadyState() override
    {
        return bIsReady ? EExecuteWhenReadyState::Execute : EExecuteWhenReadyState::Wait;
    }

    void OnReady() { bIsReady = true; UpdateExecuteWhenReady(); }

private:
    bool bIsReady = false;
};

// 使用：排队一个 lambda，等就绪后自动执行
FMyComponent Component;
Component.ExecuteWhenReady([]() { /* 在 Component 就绪后执行 */ });
```

来源: `AIAssistantExecuteWhenReady.h`

## Demo 示例

### 最小集成示例 — 注册自定义 AI 命令

```cpp
// MyAIExtension.Build.cs
PublicDependencyModuleNames.AddRange(new string[] { "Core", "AIAssistant" });

// MyAIExtension.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyAIExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyAIExtension.cpp
#include "MyAIExtension.h"
#include "AIAssistantSubsystem.h"

void FMyAIExtensionModule::StartupModule()
{
    // 模块启动时可以访问 AI Assistant Subsystem
    if (GEditor)
    {
        UAIAssistantSubsystem* Subsystem = GEditor->GetEditorSubsystem<UAIAssistantSubsystem>();
        if (Subsystem)
        {
            // Subsystem 可用，可以执行 Python 脚本
            FString Result = Subsystem->ExecutePythonScriptViaJavaScript(
                TEXT("import unreal; unreal.log('MyExtension connected!')"));
        }
    }
}

void FMyAIExtensionModule::ShutdownModule() {}

IMPLEMENT_MODULE(FMyAIExtensionModule, MyAIExtension)
```

## 模块依赖

从 `AIAssistant.Build.cs` 的依赖关系：

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库（Public 依赖） |
| `Projects` | 插件/项目信息查询 |
| `InputCore` | 输入系统核心 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | Unreal Editor 核心 |
| `ToolMenus` | 工具菜单系统（注册菜单项） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `DeveloperSettings` | 开发者设置 |
| `Json` / `JsonUtilities` | JSON 序列化（API 通信） |
| `EditorSubsystem` | EditorSubsystem 基类 |
| `HTTP` | HTTP 通信 |
| `EditorScriptingUtilities` | 编辑器脚本工具 |
| `Kismet` / `KismetCompiler` / `BlueprintGraph` | 蓝图系统集成 |
| `GraphEditor` / `PropertyEditor` | 图形编辑器和属性面板 |
| `UMG` | UMG UI 框架 |
| `ContentBrowser` / `AssetRegistry` | 内容浏览器和资产注册 |
| `LevelEditor` | 关卡编辑器集成 |
| `StatusBar` | 状态栏集成（"Ask AI" 按钮） |
| `PythonScriptPlugin` | Python 脚本执行 |
| `Slate` / `SlateCore` | Slate UI 框架 |
| `ApplicationCore` | 剪贴板等应用核心功能 |
| `WebBrowser` | 内嵌 Web 浏览器 |

插件依赖：
- **PythonScriptPlugin** — 启用 Python 脚本执行
- **EditorScriptingUtilities** — 编辑器脚本工具函数

## 配置

### 启用插件

在 `DefaultEditor.ini` 或编辑器设置中：

```ini
[AIAssistant]
bIsEnabled=true
```

### 自定义主 URL

创建 `AIAssistant.json` 配置文件，放置在以下搜索路径之一（优先级从高到低）：

1. `Engine/Restricted/NotForLicensees/Config/`
2. `Engine/Restricted/NoRedist/Config/`
3. `Engine/Restricted/LimitedAccess/Config/`
4. `Engine/Config/`
5. `Engine/`
6. `%LOCALAPPDATA%/UnrealEngine/Common/`（Windows）

```json
{
    "main_url": "https://your-custom-ai-service.example.com"
}
```

### UEFN 模式

通过 Console Variable 切换 UE / UEFN 模式（`AIAssistantConsole.h` 中定义），UEFN 模式会改变 AI 助手的环境描述符，让后端返回针对 Fortnite 编辑的回答。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-17 | `48e142f` | 修复 Mac 上 WebBrowser PanelDrawer 问题，添加开关事件通知；禁用侧边栏功能（Mac WebBrowser 仍有问题）；强制 Mac WebBrowser 在可见性变化时重新计算大小和位置 |
| 2025-10-15 | `1e6a259` | 使用 `window.eda` 判断助手前端是否加载完成，移除 URL 白名单 |
| 2025-10-08 | `7d92f2f` | AIAssistant 相关更新 |

### 维护评价

- **创建时间**：2025-08-30，非常新的插件（约 1 年）
- **实验性**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **活跃度**：近期有活跃开发（2025 年 10 月连续更新），主要在修复跨平台问题和完善前端检测
- **平台兼容性**：Mac 端仍有一些 WebBrowser 兼容问题（PanelDrawer 崩溃、侧边栏禁用）
- **内部使用**：`NoRedist=true`，`WITH_AIASSISTANT_EPIC_INTERNAL=1`，表明这主要是 Epic 内部使用的插件
- **推荐状态**：⚠️ 实验性内部插件，外部开发者可以参考其架构设计（Web API 桥接、延迟执行框架等），但不建议作为生产依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AIAssistant)
- 官方文档：无（.uplugin 中 DocsURL 为空）
