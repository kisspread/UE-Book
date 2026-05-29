# Scriptable Tools Framework

> Blueprint-Scriptable extension to the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 脚本化工具框架 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产，示例） |
| 模块 | `ScriptableToolsFramework` (Runtime), `EditorScriptableToolsFramework` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ScriptableToolsFramework) | |

## 用途
此插件提供了一个框架，旨在让开发者（尤其是蓝图开发者）能够使用 **蓝图** 来快速创建和扩展 Unreal Engine 的**交互式编辑器工具**。它封装了底层的 `InteractiveToolsFramework`，提供了更易于在蓝图中使用的基础类和可绑定的 UI 组件，从而简化了复杂编辑器工具（如自定义变换、测量、放置工具）的开发流程。

## 使用场景
- **编辑器工具开发者**：需要快速原型化或创建自定义编辑器工具，但希望避免编写大量 C++ 代码。
- **技术美术或关卡设计师**：需要在编辑器中制作特定的工作流工具，例如自定义的物体吸附、地形修改或场景测量工具，并希望通过蓝图逻辑进行快速迭代。
- **希望扩展现有工具功能**：基于框架提供的基类，通过蓝图继承来添加自定义逻辑和属性，创建工具变体。

## 模块列表
- **`ScriptableToolsFramework`** (Runtime): 核心运行时模块。定义了蓝图可脚本化工具的基础类（如 `UScriptableTool`）、交互输入处理器和属性系统。
- **`EditorScriptableToolsFramework`** (Editor): 编辑器模块。提供与编辑器深度集成的组件，如可嵌入工具面板的 UI 控件、蓝图图表编辑支持以及工具资产的管理。

## 蓝图用法

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Tool` | 在编辑器中启动一个脚本化工具实例 | `UScriptableTool` |
| `Update Hover` | 工具激活时更新鼠标悬停信息 | `UScriptableTool` |
| `Can Start` | 决定工具是否可以被启动 | `UScriptableTool` |
| `Get Transform Intent` | 获取工具当前的变换意图（移动、旋转、缩放） | `UInteractiveTool` |
| `Set Transform Intent` | 设置工具的变换意图 | `UInteractiveTool` |
| `Register Property Set` | 注册一个包含工具设置的属性集 | `UInteractiveTool` |
| `Set Tool Display Name` | 设置工具在编辑器 UI 中显示的名称 | `UInteractiveTool` |

### 使用示例（蓝图描述）
1.  **创建工具蓝图**：创建一个新蓝图，父类选择 `ScriptableTool` (或其子类)。
2.  **重写核心事件**：在蓝图中重写 `Start Tool`、`On Mouse Down`、`On Mouse Up` 等事件来定义工具逻辑。
3.  **注册属性集**：在 `Start Tool` 事件中，使用 `Register Property Set` 节点将另一个包含工具参数（如尺寸、颜色）的蓝图类注册为工具的属性面板。
4.  **处理输入**：在输入事件节点中，通过 `Get Hit Result`、`Get Input Ray` 等节点获取用户与场景的交互信息，并据此更新工具状态。
5.  **更新可视反馈**：利用提供的可绘制接口（如 `UDrawableToolProperties`）或直接操作组件来显示工具的辅助线、点等。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ScriptableToolsFramework` | 提供核心工具框架和蓝图脚本化支持 |
| `EditorScriptableToolsFramework` | 提供编辑器集成、工具UI和资产管理 |
| `ToolWidgets` | （条件依赖）提供可复用的编辑器工具UI控件 |
| `BlueprintGraph` | 支持蓝图节点和图表的自定义扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `6cab4de5` | ScriptableTools: Refactor SDraggableBoxOverlay usage to isolate ToolWidgets dependency to Scriptable | 重构UI组件依赖，将ToolWidgets依赖限制在脚本化模块内，降低耦合。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`。 |
| 2026-02-06 | `fca152ce` | ScriptableToolsFramework: Only reference ToolWidgets if building developer tools | 优化依赖，仅在构建开发者工具时才引用 ToolWidgets 模块。 |
| 2026-02-06 | `ac856ee6` | Updating tooltips to make Capture Priority values clearer. | 更新工具提示信息，使“捕获优先级”的值更清晰易懂。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了打印格式说明符的错误。 |

### 维护评价
- **状态**：**活跃维护中**。插件创建于 2024 年初，至今（2026年4月）仍有持续的功能性更新和重构。
- **阶段**：**实验性/Beta**。`.uplugin` 标记为 `IsBetaVersion=true` 且默认禁用，表明其 API 和功能可能尚未稳定，仍有变动。
- **趋势**：近期更新主要集中在依赖优化、代码清理和UI改进，说明框架正在趋于成熟和稳定。
- **推荐度**：**推荐早期采用者和工具开发者使用**。适合那些希望利用蓝图快速构建编辑器工具的团队，但需注意其 Beta 状态，未来版本可能会有 API 变更。对于追求稳定性的生产项目，建议密切关注版本更新说明。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ScriptableToolsFramework)
- [模块文档 - ScriptableToolsFramework](ScriptableToolsFramework.md)
- [模块文档 - EditorScriptableToolsFramework](EditorScriptableToolsFramework.md)
- 测试用例：位于 `Engine/Plugins/Runtime/ScriptableToolsFramework/Tests/` 目录下