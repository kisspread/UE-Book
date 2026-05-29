# Scriptable Tools Editor Mode

> Editor Mode for Scriptable Tools

| 属性 | 值 |
|---|---|
| 中文名 | 脚本化工具编辑器模式 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI 控件资产、样式资产） |
| 模块 | `ScriptableToolsEditorMode` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ScriptableToolsEditorMode) | |

## 用途

此插件为 ScriptableToolsFramework 提供**编辑器模式**（Editor Mode）支持。它在 UE5 编辑器中创建一个专门的"脚本化工具"工作模式，让用户可以在 3D 视口中使用蓝图编写的自定义工具。

插件解决的核心问题是：**如何将蓝图创建的自定义工具整合到编辑器的标准工作流中**。它提供了完整的编辑器模式 UI 框架，包括工具面板（Tool Palette）、工具属性面板、接受/取消按钮、工具分组与标签过滤等功能。

简单来说，ScriptableToolsFramework 定义了"什么是脚本化工具"，而这个插件定义了"如何在编辑器中使用这些工具"。

## 使用场景

- 你用蓝图创建了一套自定义建模工具（如特殊形状生成器）→ 需要此插件在编辑器模式中展示和运行这些工具
- 你需要为关卡设计师提供自定义工具面板 → 用此插件注册蓝图工具并按分组显示
- 你的团队有特定的资产处理流程需要一键化工具 → 将流程封装为脚本化工具并部署到编辑器模式

## 蓝图用法

此插件本身不直接暴露 BlueprintCallable 函数，但它是脚本化工具蓝图的**运行载体**。工具的蓝图接口定义在 ScriptableToolsFramework 中，此插件负责将它们呈现在编辑器 UI 中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActiveScriptableTools` | 获取当前活跃的脚本化工具集 | `UScriptableToolsEditorMode` |
| `FindToolByName` | 按名称查找已注册的工具启动命令 | `FScriptableToolsEditorModeManagerCommands` |

### 使用示例（蓝图描述）

此插件主要通过**编辑器项目设置**配置，而非蓝图节点连接：

1. 打开 **编辑 → 项目设置 → 插件 → ScriptableTools**
2. 配置 `ToolRegistrationFilters`（工具注册过滤器）来选择要激活的工具分组
3. 在编辑器工具栏中切换到 **Scriptable Tools** 编辑器模式
4. 在工具面板中选择并使用已注册的脚本化工具

## C++ 用法

### 头文件引入

```cpp
#include "ScriptableToolsEditorMode.h"
#include "ScriptableToolsEditorModeManagerCommands.h"
#include "ScriptableToolsEditorModeToolkit.h"
```

### 基本用法

自定义编辑器模式的工具注册和命令绑定：

```cpp
// 来源: ScriptableToolsEditorModeManagerCommands.h

// 注册一个自定义工具启动命令
FScriptableToolsEditorModeManagerCommands Commands;
TSharedPtr<FUICommandInfo> MyToolCommand = Commands.RegisterCommand(
    FName("MyCustomTool"),
    NSLOCTEXT("ScriptableTools", "MyTool", "My Custom Tool"),
    NSLOCTEXT("ScriptableTools", "MyToolTip", "Launch the custom tool"),
    FSlateIcon(FScriptableToolsEditorModeStyle::GetStyleSetName(), "MyToolIcon"),
    EUserInterfaceActionType::Button,
    FInputChord()
);

// 通过名称查找已注册的工具命令
bool bFound = false;
TSharedPtr<FUICommandInfo> FoundCommand = Commands.FindToolByName(TEXT("MyCustomTool"), bFound);
if (bFound)
{
    // 使用命令启动工具
}
```

（来源：`ScriptableToolsEditorModeManagerCommands.h`）

### 进阶用法

自定义编辑器模式设置和工具过滤：

```cpp
// 来源: ScriptableToolsEditorModeSettings.h

// 在代码中访问编辑器模式设置
UScriptableToolsModeCustomizationSettings* Settings = GetMutableDefault<UScriptableToolsModeCustomizationSettings>();

// 检查是否注册所有工具
if (Settings->RegisterAllTools())
{
    // 所有工具都会被注册
}
else
{
    // 只有匹配 ToolRegistrationFilters 的工具会被注册
    FScriptableToolGroupSet Filters = Settings->ToolRegistrationFilters;
}

// 切换 UI 模式
Settings->bUseLegacyPalette = false;  // 使用新版 UI
Settings->bAlwaysShowToolButtons = true;  // 始终显示工具按钮
```

（来源：`ScriptableToolsEditorModeSettings.h`）

## Demo 示例

一个最小的自定义脚本化工具编辑器模式扩展：

```cpp
// MyScriptableToolModeExtension.h
#pragma once

#include "CoreMinimal.h"
#include "ScriptableToolsEditorMode.h"

class FMyScriptableToolModeExtension
{
public:
    static void RegisterCustomToolCommands();
    static void OnToolLaunched(UInteractiveTool* Tool);
};
```

```cpp
// MyScriptableToolModeExtension.cpp
#include "MyScriptableToolModeExtension.h"
#include "ScriptableToolsEditorModeManagerCommands.h"
#include "ScriptableToolsEditorModeStyle.h"

void FMyScriptableToolModeExtension::RegisterCustomToolCommands()
{
    // 注册自定义工具图标
    UTexture2D* IconTexture = LoadObject<UTexture2D>(nullptr, TEXT("/Game/UI/MyToolIcon"));
    if (IconTexture)
    {
        FScriptableToolsEditorModeStyle::RegisterIconTexture(
            FName("MyCustomToolIcon"), IconTexture
        );
    }

    // 获取工具管理器命令并查找特定工具
    FScriptableToolsEditorModeManagerCommands& Commands =
        FScriptableToolsEditorModeManagerCommands::Get();
    
    bool bFound = false;
    auto ToolCmd = Commands.FindToolByName(TEXT("MyCustomTool"), bFound);
    
    if (!bFound)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyCustomTool not registered"));
    }
}

void FMyScriptableToolModeExtension::OnToolLaunched(UInteractiveTool* Tool)
{
    if (Tool)
    {
        UE_LOG(LogTemp, Log, TEXT("Scriptable tool launched: %s"), *Tool->GetName());
    }
}
```

## 模块依赖

从 `.uplugin` 的 Plugins 字段提取：

| 模块 | 用途 |
|---|---|
| `ScriptableToolsFramework` | 提供脚本化工具的基础框架（工具类、构建器、上下文对象） |
| `MeshModelingToolset` | 提供网格建模工具集（建模操作基础设施） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `6cab4de5` | ScriptableTools: Refactor SDraggableBoxOverlay usage to isolate ToolWidgets dependency to Scriptable | 重构拖拽框覆盖层，隔离工具控件依赖 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 UE_LOGF |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换后的第二次提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的改动 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托调用方式，解决注册丢失问题 |

### 维护评价

- **状态**: 活跃维护中
- **创建时间**: 2024 年 1 月，从 Experimental 升级为 Beta
- **更新频率**: 2026 年仍有持续更新，包括重构和 API 适配
- **注意**: 插件仍标记为 Beta（`IsBetaVersion=true`）且默认未启用（`EnabledByDefault=false`），API 可能在未来版本中发生变化
- **已知限制**: 依赖 `ScriptableToolsFramework` 和 `MeshModelingToolset`，需要同时启用这两个插件

**推荐**: 如果你需要在编辑器中使用蓝图自定义工具，这是必需的插件。但由于仍处于 Beta 阶段，建议关注 API 变更通知。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ScriptableToolsEditorMode)
- [ScriptableToolsFramework 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ScriptableToolsFramework)
- [MeshModelingToolset 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)