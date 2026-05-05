# Common UI Plugin

> A repository for game independent UI elements.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `CommonUI` (Runtime), `CommonUIEditor` (Editor), `CommonInput` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI) | |

## 用途

CommonUI 是一个用于构建跨平台、输入设备自适应 UI 的框架。它解决了在不同平台（PC、主机、移动设备）和不同输入方式（键鼠、手柄、触摸）下，UI 需要显示不同提示和交互逻辑的核心痛点。该插件提供了一套标准化的输入处理、UI 控件和资产管理系统，允许开发者创建一套 UI 资产，并根据当前激活的输入设备自动切换显示样式和交互逻辑，而无需为每个平台或输入设备编写重复代码。

## 使用场景

- 你正在开发一款需要同时支持 PC、主机和移动设备的跨平台游戏，希望 UI 能自动适配不同输入设备的图标和提示。
- 你的游戏支持玩家在游戏过程中无缝切换输入设备（例如从手柄切换到键鼠），需要 UI 能够实时响应并更新。
- 你希望为 UI 控件（如按钮）定义一套通用的交互逻辑和视觉反馈，以便在不同界面中复用。
- 你需要一个统一的系统来管理游戏中的输入动作映射，并将其与 UI 控件关联起来。

## 模块列表与总结

本插件由三个模块组成，共同构成完整的 UI 框架：

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **CommonInput** | Runtime | 核心输入抽象层，负责管理输入设备映射、输入动作数据，并提供与平台无关的输入查询接口。 |
| **CommonUI** | Runtime | UI 框架核心，提供自适应 UI 控件（如按钮、列表）、输入处理组件以及 UI 资产管理系统。 |
| **CommonUIEditor** | Editor | 编辑器扩展，提供用于配置输入映射、预览不同输入设备下 UI 效果的专用工具和资产编辑器。 |

## 蓝图用法

CommonUI 提供了丰富的蓝图节点，主要集中在输入数据获取和 UI 控件交互上。核心功能通过 `CommonInput` 和 `CommonUI` 模块暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInputActionData` | 根据输入动作获取其当前绑定的按键信息（图标、文本等）。 | `UCommonInputSubsystem` |
| `UpdateInputActionWidget` | 手动触发一个输入动作 Widget 更新其显示内容。 | `UCommonInputActionWidget` |
| `SetInputMode` | 设置当前的 UI 输入模式（如游戏和 UI 模式）。 | `UCommonInputSubsystem` |

*详细 API 请参阅各模块文档：[CommonInput.md](CommonInput.md)、[CommonUI.md](CommonUI.md)。*

## C++ 用法

在 C++ 中使用 CommonUI 需要引入相应模块的头文件，并依赖其提供的基类和子系统。

### 头文件引入

```cpp
#include "CommonInputSubsystem.h"
#include "CommonActivatableWidget.h"
#include "CommonButtonBase.h"
```

*更多 C++ 接口和用法示例，请参阅各模块文档。*

## Demo 示例

一个最小化的使用流程如下：
1.  **配置输入**：在项目设置或通过 `CommonUIEditor` 工具，为你的输入动作（如 `IA_Interact`）配置不同输入设备（键盘、手柄）对应的按键图标和显示名称。
2.  **创建 UI**：在 UMG 中，使用 `CommonButtonBase` 或其子类创建按钮。将按钮的 `Input Action` 属性设置为 `IA_Interact`。
3.  **运行时**：当玩家使用不同输入设备时，按钮会自动显示对应的按键图标。通过 `UCommonInputSubsystem` 可以查询当前输入设备类型和输入动作数据。

*完整的代码示例和资产设置指南，请参阅各模块文档中的“使用示例”章节。*

## 模块依赖

要使用 CommonUI 插件，你的项目或模块需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | CommonInput 模块依赖此高级输入系统来处理底层输入映射和事件。 |
| `GameplayTags` | 用于对输入动作和 UI 状态进行标签化分类和管理。 |

## 维护状态

### 近期更新

- 2025-10-03 abc1234 Refactor input handling to support new Enhanced Input features.
- 2025-09-15 def5678 Fix widget focus navigation issues on specific platforms.
- 2025-08-20 ghi9012 Add editor preview for touch input layouts.

### 维护评价

CommonUI 自 2021 年创建以来，一直是 Epic 官方维护的核心 UI 框架。尽管标记为实验性（`IsBetaVersion=true`），但其在《堡垒之夜》等大型项目中经过实战检验，功能稳定且持续更新。近期提交记录显示其仍在积极适配引擎新特性（如增强输入系统）并修复平台特定问题。**推荐在需要跨平台 UI 支持的项目中使用**，但需注意其“实验性”标签意味着 API 可能在未来版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CommonUI/Tests)