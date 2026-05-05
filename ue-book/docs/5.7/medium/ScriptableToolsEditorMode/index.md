# Scriptable Tools Editor Mode

> Editor Mode for Scriptable Tools

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ScriptableToolsEditorMode` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-12-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ScriptableToolsEditorMode) | |

## 用途

Scriptable Tools Editor Mode 是 UE5 编辑器模式（Editor Mode）的实现，为 **Scriptable Tools Framework** 提供完整的编辑器 UI 容器。它解决的核心问题是：如何让通过蓝图（Blueprint）创建的交互式工具（Interactive Tools）能够像原生建模工具一样，在编辑器中拥有工具面板、工具栏按钮、属性面板、Accept/Cancel 按钮等完整的 UI 体验。

简单来说，ScriptableToolsFramework 让你可以用蓝图创建交互式工具，而 ScriptableToolsEditorMode 则是这些工具在编辑器中的"宿主"——它提供了一个专属的编辑器模式，负责：
- 自动发现并注册所有蓝图创建的 Scriptable Tool
- 在工具面板中按分类展示工具按钮（支持自定义图标）
- 管理工具的激活/停用生命周期
- 提供 Accept、Cancel、Complete 等标准操作按钮
- 支持工具标签过滤（Tag-based filtering）
- 在工具激活时自动启用实时视口（Realtime Viewport）
- 处理蓝图重新编译时的工具热重载

**默认未启用**：此插件需要在编辑器设置中手动启用（`EnabledByDefault: false`），且标记为 Beta 版本。

## 使用场景

- 你用蓝图创建了一系列自定义交互式工具（继承自 `UScriptableInteractiveTool`），需要一个统一的 UI 界面来组织和使用它们 → 用 Scriptable Tools Editor Mode
- 你正在为团队开发一套自定义编辑器工具集，希望工具能像建模模式（Modeling Mode）一样拥有专业的工作流 → 启用此插件并结合 ScriptableToolsFramework
- 你需要在编辑器中快速原型化交互式工具，不想写 C++ 的 Editor Mode 代码 → 此插件提供了现成的编辑器模式容器
- 你需要按标签（Tag）过滤和分组显示工具，让不同项目阶段只展示相关工具 → 利用 `ToolRegistrationFilters` 设置

## 蓝图用法

此插件本身不直接暴露蓝图节点。它是 Scriptable Tools 的 UI 宿主，蓝图交互主要通过 **ScriptableToolsFramework** 插件中的类实现（如 `UScriptableInteractiveTool`、`UScriptableToolBuilder`）。

### 配置选项

通过 **Project Settings → Plugins → Scriptable Tools** 可配置：

| 设置 | 说明 |
|---|---|
| `ToolRegistrationFilters` | 工具注册过滤器，按标签组筛选哪些工具显示在面板中。为空则显示所有工具 |
| `bUseLegacyPalette` | 是否使用旧版工具面板 UI（切换后需重新进入模式） |
| `bAlwaysShowToolButtons` | 工具激活时是否始终显示工具按钮（默认 `true`） |

## C++ 用法

### 头文件引入

```cpp
#include "ScriptableToolsEditorMode.h"
#include "ScriptableToolsEditorModeToolkit.h"
#include "ScriptableToolsEditorModeSettings.h"
```

### 核心类

| 类 | 说明 |
|---|---|
| `UScriptableToolsEditorMode` | 编辑器模式主类，继承自 `UBaseLegacyWidgetEdMode`，管理工具生命周期 |
| `FScriptableToolsEditorModeToolkit` | 工具面板（Toolkit）UI，负责工具按钮、属性面板、Accept/Cancel 按钮的渲染 |
| `UScriptableToolsModeCustomizationSettings` | 开发者设置，控制工具注册过滤和 UI 自定义 |
| `FScriptableToolsEditorModeModule` | 模块入口，注册样式和命令 |

### 编辑器模式的工作流程

进入模式时（`Enter()`），插件执行以下操作：

1. 注册 Tool Target 工厂（StaticMesh、Volume、DynamicMesh）
2. 注册 Transform Gizmo 和 Scene Snapping 上下文对象
3. 启用实时视口覆盖
4. 创建 `UScriptableToolSet` 并扫描所有蓝图 Scriptable Tool
5. 为每个工具注册 UI 命令和图标
6. 初始化视口 Widget API 和 Focus API 等上下文对象

退出模式时（`Exit()`），反向执行清理：取消活跃工具、注销上下文对象、卸载所有工具。

### 蓝图编译热重载

当蓝图 Scriptable Tool 被重新编译时，插件会：
1. 如果该工具正在使用中，自动取消（Cancel）它
2. 在下一帧 Tick 中重建工具集（`RebuildScriptableToolSet`），确保新编译的工具版本被加载

### 工具激活流程

```cpp
// 工具通过 ToolManager 激活
GetToolManager()->SelectActiveToolType(EToolSide::Mouse, ToolIdentifier);
GetToolManager()->ActivateTool(EToolSide::Mouse);
```

工具激活后，Toolkit 会：
- 禁用 Slate 节流（`FSlateThrottleManager`），确保滑块拖拽时后台计算能正常响应
- 隐藏标准变换 Gizmo
- 禁止自动保存
- 禁止删除/剪切操作（对 Accept 类型工具）

### 模块依赖

| 模块 | 用途 |
|---|---|
| `ScriptableToolsFramework` | 蓝图可脚本化的交互式工具基础框架 |
| `EditorScriptableToolsFramework` | 编辑器端的工具框架扩展 |
| `InteractiveToolsFramework` | UE 交互式工具核心框架 |
| `EditorInteractiveToolsFramework` | 编辑器端的交互式工具框架 |
| `ModelingComponents` / `ModelingComponentsEditorOnly` | 建模组件，提供 ToolTarget 等基础设施 |
| `GeometryCore` | 几何核心库 |
| `UnrealEd` | 编辑器基础模块 |
| `PropertyEditor` | 属性面板，用于工具属性展示 |
| `StatusBar` | 状态栏集成 |
| `ToolWidgets` / `EditorWidgets` | 工具和编辑器 UI 控件 |
| `WidgetRegistration` | 控件注册系统 |

## Demo 示例

此插件是纯 Editor Mode 容器，不提供独立的可编译示例。要使用它，你需要结合 **ScriptableToolsFramework** 插件创建蓝图工具。基本步骤：

1. 启用插件：在 Plugins 面板中启用 `ScriptableToolsEditorMode`（会自动启用依赖的 `ScriptableToolsFramework`）
2. 创建蓝图工具：新建继承自 `UScriptableInteractiveTool` 的蓝图类
3. 设置工具属性：配置 `ToolName`、`ToolLongName`、`ToolTooltip`、`ToolIconTexture` 等
4. 进入 Scriptable Tools 编辑器模式：在视口左上角选择 "Scriptable Tools"
5. 工具会自动出现在工具面板中

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "ScriptableToolsFramework",
    "EditorScriptableToolsFramework",
    "InteractiveToolsFramework",
    "EditorInteractiveToolsFramework"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-03 | `89e9961` | FortniteTools: Hide tooltag filter bar at the top of the mode | 为 FortniteTools 项目定制，隐藏模式顶部的标签过滤栏 |
| 2025-10-01 | `db4cba7` | Restore behavior of hiding category toolbar if only a single palette is present | 恢复单面板时自动隐藏分类工具栏的行为 |
| 2025-09-04 | `87637a6` | Added validation checks around pointers | 增加指针验证检查，提升稳定性 |

### 维护评价

- **创建时间**：2022 年 12 月（约 3 年前），最初在 Experimental 目录下，后迁移到 Editor 目录
- **最近更新**：2025 年 10 月有活跃更新，主要是 UI 行为调整和稳定性修复
- **维护状态**：**活跃维护中** — 最近 6 个月内有功能性更新
- **Beta 状态**：插件仍标记为 `IsBetaVersion: true`，API 可能发生变化
- **使用建议**：适合用于原型开发和内部工具。由于仍处于 Beta 阶段，生产环境使用需谨慎，注意升级时的 API 兼容性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ScriptableToolsEditorMode)
- [ScriptableToolsFramework 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ScriptableToolsFramework)（核心依赖插件）
- 官方文档：无（.uplugin 中 DocsURL 为空）
