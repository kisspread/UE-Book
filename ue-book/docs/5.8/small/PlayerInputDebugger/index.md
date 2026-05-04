# Player Input Debugger

> Plugin for debugging input related things

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlayerInputDebugger` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlayerInputDebugger) | |

## 用途

PlayerInputDebugger 是一个**编辑器内实时输入调试窗口**，用于在 PIE（Play In Editor）运行期间全面诊断玩家输入问题。

它解决的核心问题是：当输入行为不符合预期时，开发者很难判断问题出在哪个环节——是 Slate 层没有收到事件、Enhanced Input 映射配置错误、输入设备断连、还是 PlayerInput 组件栈的优先级冲突。这个插件将所有这些信息汇总到一个可停靠的调试窗口中，提供从硬件设备到最终蓝图响应的完整输入链路可视化。

**主要功能模块：**

- **全局输入信息区**：始终显示当前焦点 Slate 控件、输入模式配置（鼠标捕获、CommonUI 状态）、输入组件栈（含优先级和阻塞状态）
- **Enhanced Input 标签页**：实时展示当前激活的 InputMappingContext、绑定的按键、触发事件状态和输入值，支持按上下文/动作/按键类型过滤
- **输入设备标签页**：按平台用户分组显示所有已知输入硬件设备（包括已断开的设备），支持模拟设备描述符
- **输入事件标签页**：统一记录 Slate 输入事件和 PlayerInput 事件的完整日志，包含帧号、事件类型、处理控件、蓝图调用栈等信息

## 使用场景

- 你在使用 Enhanced Input 但某个按键绑定没有触发预期动作 → 用 Enhanced Input 标签页检查映射上下文是否激活、按键是否正确绑定、触发事件是否匹配
- 你怀疑输入事件被某个 Slate 控件拦截了 → 用输入事件标签页查看事件的处理链和 reply 状态
- 你的游戏支持手柄热插拔，需要确认设备连接状态 → 用输入设备标签页查看所有设备的连接/断开历史
- 你需要排查 CommonUI 的输入模式切换问题 → 用全局信息区查看当前 InputConfig 和 CommonUI 路由器状态
- 你在蓝图中调用了 FlushInput 但不确定是哪里触发的 → 用输入事件标签页查看 flush 时的脚本调用栈

## 蓝图用法

此插件为纯编辑器工具，不暴露蓝图 API。所有功能通过编辑器窗口 UI 交互使用。

### 使用方式

1. 在编辑器中启用插件：**Edit → Plugins → 搜索 "PlayerInputDebugger" → 启用**
2. 进入 PIE 模式
3. 通过菜单 **Window → Player Input Debugger** 打开调试窗口
4. 在窗口顶部的下拉框中选择要调试的 PlayerController

### 窗口布局

```
┌─────────────────────────────────────────────────┐
│  [PlayerController 下拉选择器]                     │
├─────────────────────────────────────────────────┤
│  ▼ 全局输入信息（始终可见，可折叠）                   │
│    • 当前焦点 Slate 控件                            │
│    • 输入配置（模式、鼠标、CommonUI）                 │
│    • 输入组件栈（优先级、阻塞状态）                    │
├──────────┬──────────────┬───────────────────────┤
│ Enhanced │ Input        │ Player Input          │
│ Input    │ Devices      │ Events                │
│          │              │                       │
│ 映射上下文 │ 设备列表      │ 统一事件日志             │
│ 动作绑定  │ 连接状态      │ Slate + Player 事件    │
│ 触发状态  │ 模拟描述符    │ 调用栈追踪              │
└──────────┴──────────────┴───────────────────────┘
```

## C++ 用法

此插件为编辑器工具，不提供可直接在项目代码中调用的 C++ API。以下内容帮助理解其内部实现机制，便于二次开发或扩展。

### 头文件引入

```cpp
#include "PlayerInputDebuggerModule.h"
```

### 内部架构概览

插件采用模块化 Slate Widget 架构：

| Widget 类 | 职责 |
|---|---|
| `SPlayerInputDebugger` | 根容器，管理 PC 选择器和子标签页 |
| `SGlobalInputInfoSection` | 全局输入信息区（焦点控件、输入配置、组件栈） |
| `SEnhancedInputTab` | Enhanced Input 映射上下文和动作显示 |
| `SInputDevicesTab` | 输入硬件设备列表和状态 |
| `SPlayerInputEventsTab` | 统一输入事件日志 |

### 数据流

```
FSlateDebugging::InputEvent ──┐
FSlateDebugging::MouseCaptureEvent ──┤──→ SPlayerInputEventsTab
FPlayerInputDebugging::OnPlayerInputEventExecuted ──┤     (统一日志)
FPlayerInputDebugging::OnPlayerInputFlushed ──┘

IGenericPlatformInputDeviceMapper ──→ SInputDevicesTab
  (ConnectionChanged / HardwareDeviceChanged / PairingChanged)

UCommonUIActionRouterBase::OnActiveInputConfigChanged ──→ SGlobalInputInfoSection
```

### 核心数据结构

**FEnhancedInputDisplayItem** — Enhanced Input 标签页的列表行项：

```cpp
struct FEnhancedInputDisplayItem
{
    bool bIsHeader = false;           // 是否为 IMC 上下文标题行
    bool bIsInputModeInfo = false;    // 是否为输入模式信息行

    // 标题行字段
    FText ContextName;
    int32 Priority = 0;

    // 动作映射行字段
    FText ActionName;
    FKey BoundKey;
    uint8 TriggerEventOrdinal = 0;    // ETriggerEvent
    FText ValueText;

    TWeakObjectPtr<const UObject> WeakAsset;  // 用于超链接导航
};
```

**FUnifiedInputEventRecord** — 统一输入事件日志条目：

```cpp
struct FUnifiedInputEventRecord
{
    uint32 FrameNumber = 0;
    EInputEventSource Source;  // Slate / SlateMouseCapture / Player / PlayerFlush

    // Slate 事件字段
    ESlateDebuggingInputEvent SlateEventType;
    FKey Key;
    FString HandlerWidgetType;
    FString UserWidgetName;
    bool bReplyHandled = false;

    // Player 事件字段
    FString ActionName;
    FString InputComponentName;
    int32 InputComponentPriority = 0;
    FVector InputValue;

    // Flush 字段
    FString ScriptCallstack;  // 蓝图调用栈
};
```

## Demo 示例

此插件为编辑器工具，无需在项目代码中实例化。以下是扩展该插件的最小示例——添加一个自定义标签页：

```cpp
// MyCustomInputTab.h
#pragma once

#include "Widgets/SCompoundWidget.h"

class SMyCustomInputTab : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCustomInputTab) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

    void SetPlayerController(APlayerController* PC) { WeakPC = PC; }

private:
    TWeakObjectPtr<APlayerController> WeakPC;
};
```

```cpp
// MyCustomInputTab.cpp
#include "MyCustomInputTab.h"

void SMyCustomInputTab::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(STextBlock)
        .Text(FText::FromString(TEXT("Custom Input Debug Tab")))
    ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 读取 InputMappingContext 和 InputAction 数据 |
| `CommonUI` | 获取 UCommonUIActionRouterBase 的输入配置状态 |
| `SlateDebugging` | 捕获 FSlateDebugging 输入事件回调 |
| `PlayerInputDebugging` | 捕获 FPlayerInputDebugging 玩家输入事件回调 |

## 维护状态

### 近期更新

```
- 2026-04-22 33dc7559 [Input Debugger] 记录 input flush 时的调用栈，便于追踪触发源
- 2026-03-31 d1d2b706 [Player input debugger] 修复本地化警告
- 2026-03-31 7da916af [Player input debugger] 修复选择状态不断刷新导致选中项丢失的问题
- 2026-03-31 f1227b02 [Player Input Debugger] 设备标签页支持设置模拟设备类型
- 2026-03-27 71c13324 修复本地化警告
```

### 维护评价

- **状态**：🆕 活跃开发中
- **创建时间**：2026-03-27（约 1 个月前）
- **更新频率**：创建后一周内密集提交 5 次，包含功能添加和 bug 修复
- **实验性标记**：IsBetaVersion=true、IsExperimentalVersion=true、EnabledByDefault=false，表明 Epic 将其视为实验性功能
- **已知限制**：
  - 仅在编辑器 PIE 模式下可用，不支持独立进程调试
  - 依赖 EnhancedInput 和 CommonUI 插件，不适用于传统输入系统
  - 作为实验性插件，API 和功能可能在后续版本中发生重大变化

**推荐使用**：如果你在使用 Enhanced Input 系统且遇到输入调试困难，强烈推荐启用此插件。它是 Epic 官方提供的专用调试工具，能显著降低输入问题的排查成本。但请注意其实验性状态，不要在生产构建中依赖它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlayerInputDebugger)
- [Enhanced Input 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput)（依赖项）
- [CommonUI 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/CommonUI)（依赖项）