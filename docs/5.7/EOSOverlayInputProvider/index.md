# EOS Overlay Input Provider

> Responsible for providing input forwarding to the EOSSDK Overlay.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否（`EnabledByDefault: false`） |
| 包含内容 | 否 |
| 模块 | `EOSOverlayInputProvider` (ClientOnlyNoCommandlet, LoadingPhase: PostConfigInit) |
| 平台限制 | 空白（`PlatformAllowList: []`，需自行配置） |
| 创建时间 | 2024-01-16 |
| 年龄标签 | 🆕（~2年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/EOSOverlayInputProvider) | |

## 用途

此 plugin 的核心职责是**将 UE 的输入事件转发给 Epic Online Services (EOS) SDK 的 Overlay（叠加层）**。

当游戏启用了 EOS Overlay（例如好友列表、成就面板、商城等 UI 叠加层）时，用户需要在游戏画面上与这些 UI 交互。但 Overlay 不是 UE 的 Slate Widget，它运行在 EOS SDK 层面，因此需要一个桥接机制把键盘、鼠标、手柄等原始输入事件捕获并转发给 EOS SDK。

这就是 `EOSOverlayInputProvider` 的作用——它通过 Slate 的 `IInputProcessor` 接口拦截所有输入事件，调用 `EOS_UI_ReportInputState()` 把状态同步给 EOS UI 系统。当 Overlay 处于排他输入模式（`bIsExclusiveInput`）时，处理器会拦截（吃掉）输入事件，阻止它们传递到游戏；否则事件正常透传到游戏，同时 EOS Overlay 也能收到副本。

## 为什么需要这个 plugin？

- EOS SDK 的 Overlay 是独立于 UE 渲染管线的系统 UI，不共享输入
- UE 的输入系统（Enhanced Input / Legacy Input）只面向游戏逻辑，不通知 EOS
- 没有这个 plugin，EOS Overlay 无法接收鼠标点击或手柄操作，用户无法与之交互
- `EnabledByDefault: false` 是因为不是所有项目都使用 EOS Overlay，这是一个选择性功能

## 使用场景

- 你使用 Epic Online Services 作为在线子系统，并且启用了 EOS Overlay（好友邀请、商城、成就等）
- 你的游戏需要在运行时弹出 EOS 社交界面，用户需要在其中操作
- 你希望手柄用户也能在 EOS Overlay 中导航（而不仅仅是鼠标）

**不需要此 plugin 的情况：**
- 你没有使用 EOS，或只用了 EOS 的其他子模块（如 Stats/Leaderboards）但不使用 Overlay
- 你使用了 EOS Overlay 但平台不支持（如某些主机），不需要输入转发

## 蓝图用法

此 plugin **没有暴露任何蓝图接口**。它完全是运行时自动工作的底层系统——一旦启用并正确配置，输入转发会自动发生，不需要在蓝图中调用任何函数。

### 启用方式

由于 `EnabledByDefault: false`，你需要手动启用：

1. **Project Settings → Plugins** 中搜索 "EOS Overlay Input Provider" 并启用
2. 或在 `.uproject` 文件中添加：
   ```json
   "Plugins": [
       {
           "Name": "EOSOverlayInputProvider",
           "Enabled": true
       }
   ]
   ```
3. 或在 Target.cs 中通过代码启用

> **注意**：此 plugin 的模块类型为 `ClientOnlyNoCommandlet`，不会在 Dedicated Server 或 Commandlet 中加载。`PlatformAllowList` 为空，你可能需要根据项目需求在 `.uplugin` 中配置目标平台。

## C++ 用法

此 plugin 是纯自运行模块，不需要使用者编写代码。但了解其内部工作原理有助于调试问题。

### 架构概览

```
StartupModule()
    └─ StartupTicker()  // 注册 Tick 回调
        └─ Tick() → IsRenderReady()  // 等待 Slate 渲染器就绪
            └─ 创建 FEOSOverlayInputProviderPreProcessor
            └─ FSlateApplication::RegisterInputPreProcessor(...)
                └─ Initialize()  // 监听 EOS 平台创建事件
                    └─ OnPlatformCreated() → 注册 DisplaySettingsUpdated 回调

输入事件流：
  用户按键/点击 → Slate → FEOSOverlayInputProviderPreProcessor::HandleXxxEvent()
      ├─ 更新内部输入状态（CurrentInputStates）
      ├─ 调用 EOS_UI_ReportInputState() 通知 EOS SDK
      └─ 返回 bIsExclusiveInput（true = 吃掉事件，false = 透传）
```

### 关键类

#### `FEOSOverlayInputProviderModule`
模块入口类。核心职责是**等待渲染器就绪后注册输入预处理器**。它使用 `FTSTicker` 每帧检测 `FSlateApplication::GetRenderer()` 是否可用，避免在编辑器启动列表等非游戏窗口中过早注册。

#### `FEOSOverlayInputProviderPreProcessor`
实现了 `IInputProcessor` 接口，是实际的输入转发器。支持的输入类型：

| 输入类型 | 处理方式 |
|---|---|
| 键盘 KeyDown/KeyUp | 映射为 EOS 按钮标志位，调用 `ReportInputState` |
| 鼠标按钮 Down/Up | 设置 `bMouseButtonDown` + 坐标，调用 `ReportInputState` |
| 鼠标移动 | 仅在排他模式下拦截，不转发给 EOS |
| 鼠标滚轮/双击 | 仅在排他模式下拦截 |
| 模拟输入（Analog） | 仅在排他模式下拦截 |
| 运动检测（Motion） | 仅在排他模式下拦截 |

#### `FEOSInputState`
继承自 `EOS_UI_ReportInputStateOptions` 的辅助结构体，使用 Builder 模式封装输入状态构造。包含：
- 按钮标志位（DPad、Face Buttons、Shoulders、Triggers 等）
- 鼠标位置和按键状态
- 手柄摇杆值（Left/Right Stick X/Y）
- 扳机值（Left/Right Trigger）
- `bAcceptIsFaceButtonRight`：根据平台自动检测确认键是否是右脸键

### 手柄按键映射

Plugin 内置了 UE Key → EOS Button 的映射表：

| UE Key | EOS Button Flag |
|---|---|
| `Gamepad_DPad_Down` | `EOS_UISBF_DPad_Down` |
| `Gamepad_DPad_Up` | `EOS_UISBF_DPad_Up` |
| `Gamepad_DPad_Left` | `EOS_UISBF_DPad_Left` |
| `Gamepad_DPad_Right` | `EOS_UISBF_DPad_Right` |
| `Gamepad_FaceButton_Bottom` | `EOS_UISBF_FaceButton_Bottom` |
| `Gamepad_FaceButton_Top` | `EOS_UISBF_FaceButton_Top` |
| `Gamepad_FaceButton_Left` | `EOS_UISBF_FaceButton_Left` |
| `Gamepad_FaceButton_Right` | `EOS_UISBF_FaceButton_Right` |
| `Gamepad_LeftShoulder` | `EOS_UISBF_LeftShoulder` |
| `Gamepad_RightShoulder` | `EOS_UISBF_RightShoulder` |
| `Gamepad_LeftTrigger` | `EOS_UISBF_LeftTrigger` |
| `Gamepad_RightTrigger` | `EOS_UISBF_RightTrigger` |
| `Gamepad_LeftThumbstick` | `EOS_UISBF_LeftThumbstick` |
| `Gamepad_RightThumbstick` | `EOS_UISBF_RightThumbstick` |
| `Gamepad_Special_Left` | `EOS_UISBF_Special_Left` |
| `Gamepad_Special_Right` | `EOS_UISBF_Special_Right` |

### 排他输入模式

当 EOS Overlay 处于排他输入模式时（例如弹出了全屏模态对话框），所有输入事件都会被拦截，游戏不会收到任何输入。这是通过 `EOS_UI_AddNotifyDisplaySettingsUpdated` 回调中的 `bIsExclusiveInput` 字段来控制的。

### 如果需要扩展或自定义

如果你需要修改输入转发行为，需要 fork 此 plugin 并修改 `FEOSOverlayInputProviderPreProcessor`：

```cpp
// 在 HandleKeyDownEvent 中，当前逻辑是：
// 1. 将 UE Key 映射为 EOS Button Flag
// 2. 更新内部状态
// 3. 调用 EOS_UI_ReportInputState
// 4. 返回 bIsExclusiveInput 决定是否拦截事件

// 要修改行为，重写对应的 Handle* 方法即可
```

## Demo 示例

此 plugin 无需编写代码。最小启用示例：

### 1. `.uproject` 配置

```json
{
    "Plugins": [
        {
            "Name": "OnlineSubsystemEOS",
            "Enabled": true
        },
        {
            "Name": "EOSOverlayInputProvider",
            "Enabled": true
        }
    ]
}
```

### 2. 验证工作

启用后，运行游戏并按 Shift+F3（EOS Overlay 默认快捷键）打开 Overlay。如果鼠标可以正常点击 Overlay 内的按钮，说明输入转发工作正常。

> **前提**：必须先正确配置 EOS SDK（Project ID、Sandbox ID、Deployment ID 等），否则 Overlay 本身不会启动。

## 模块依赖

此 plugin 的所有依赖都是 **PrivateDependencyModuleNames**（仅内部使用），不会传递到你的模块。但你需要间接依赖以下模块才能让 plugin 正常工作：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心框架 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `EOSSDK` | Epic Online Services SDK，提供 Overlay API |
| `EOSShared` | EOS 共享工具和类型（plugin 显式依赖） |
| `InputCore` | UE 输入核心（按键定义 `EKeys`） |
| `SlateCore` | Slate UI 核心 |
| `Slate` | Slate 框架（`FSlateApplication::RegisterInputPreProcessor`） |

**你的项目需要确保：**
- `EOSSDK` 模块可用（通常通过 `OnlineSubsystemEOS` plugin 引入）
- `EOSShared` plugin 已启用（plugin 依赖声明中已自动要求）

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-12 | `ce6ff39` | 修复 `[[nodiscard]]` 警告 | `FTSTicker::RemoveTicker` 返回值被忽略，改用赋值接收返回值。纯编译器警告修复。 |
| 2024-11-06 | `bc63a88` | 重定向编译器警告设置 | `CppCompileWarningProperties` → `CppCompileWarningSettings`，构建系统重构的配套修改。 |
| 2024-09-04 | `7abeaeb` | 重构为响应 EOS 通知 | **最有实质意义的更新**：原先依赖 `FSlateApplication` 来检测 Overlay 显示状态，现在改为直接订阅 `EOS_UI_AddNotifyDisplaySettingsUpdated` 通知，更可靠且解耦。 |

### 维护评价

- **创建时间**：2024-01-16，约 2 年前，🆕 级别
- **最近更新**：2025-09-12（最近一次实质性功能更新在 2024-09-04）
- **更新频率**：低（约每年 1-2 次），但每次更新都有意义
- **维护状态**：**维护中**——代码稳定，功能完整，更新频率与 EOS SDK 变动同步
- **风险评估**：低风险。代码量小（~220 行核心代码），逻辑清晰，依赖的 EOS API 稳定
- **推荐**：如果你使用 EOS Overlay，这是必备 plugin，无替代方案

> ⚠️ 此 plugin 的 `PlatformAllowList` 为空数组。这意味着默认没有任何平台被允许加载此模块。在实际使用中，EOS Online Subsystem 或其他依赖方可能通过编译配置覆盖此限制，但如果你在非常规平台（如 Linux Dedicated Server）遇到问题，请检查此配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/EOSOverlayInputProvider)
- [EOS Overlay 官方文档](https://dev.epicgames.com/docs/epic-online-services/services/en-US/players/overlay-overview/index.html)
- 测试用例：无（此 plugin 没有配套自动化测试）
