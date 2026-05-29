# Light Mixer

> Edit any properties of scene lights in a spreadsheet format!

| 属性 | 值 |
|---|---|
| 中文名 | 灯光混合器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LightMixer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ObjectMixer/LightMixer) | |

## 用途

Light Mixer 是一个**基于 ObjectMixer 构建的灯光专用编辑器工具**。它提供了一个电子表格界面，让你能够快速查看和批量编辑场景中所有灯光的属性。

**解决的问题**：
- 在复杂场景中，需要逐个调整数十甚至数百个灯光的参数（强度、颜色、衰减等），效率极低。
- ObjectMixer 是通用对象混合器，但对灯光这类特定类型的属性调整不够专注。

**为什么存在**：
- **专业化的灯光调优**：将灯光编辑从通用的对象混合器中独立出来，提供更符合灯光工作流的默认配置。
- **批量操作效率**：在类似 Excel 的表格视图中，可以同时选择多个灯光，一次性修改它们的共同属性（如统一降低所有灯光的强度）。
- **快速概览**：直观地看到场景中所有灯光的参数分布，便于美术总监或技术美术进行整体把控。

## 使用场景

- 你在进行**大型场景的灯光优化**，需要快速调整几十盏灯光的 `Intensity` 和 `AttenuationRadius`。
- 你负责**统一游戏场景的光照风格**，需要将所有室内灯光的 `LightColor` 从冷色调改为暖色调。
- 你正在**调试动态光照问题**，需要临时禁用某一类灯光（如所有点光源），通过表格的筛选和批量开关功能快速操作。

## 蓝图用法

此插件为**纯编辑器功能插件**，不暴露任何蓝图节点。其全部功能通过编辑器界面和 C++ 代码访问。

## C++ 用法

### 头文件引入

使用 Light Mixer 的模块功能时，需要包含其核心模块头文件。

```cpp
#include "LightMixerModule.h"
```

### 基本用法

**打开 Light Mixer 窗口**

你可以通过 C++ 代码直接打开 Light Mixer 面板，这对于创建自定义编辑器工具栏按钮或快捷键非常有用。

```cpp
// 来源: LightMixerModule.h
// 打开 Light Mixer 的标签页窗口
FLightMixerModule::Get().Initialize();
// 通常，你不需要直接调用 Initialize()，模块启动时会自动初始化。
// 更常用的是激活已存在的标签页。
```

**访问插件设置**

Light Mixer 提供了一个配置页面，可以控制是否隐藏其依赖的“Object Mixer”菜单项。

```cpp
// 来源: LightMixerEditorSettings.h
// 访问 Light Mixer 的编辑器设置
ULightMixerEditorSettings* Settings = GetMutableDefault<ULightMixerEditorSettings>();
if (Settings)
{
    // 例如，检查是否应该隐藏 Object Mixer 菜单项
    bool bShouldHideObjectMixer = Settings->bHideObjectMixerMenuItem;
    UE_LOG(LogTemp, Log, TEXT("Should hide Object Mixer menu item: %s"), 
        bShouldHideObjectMixer ? TEXT("Yes") : TEXT("No"));
}
```

### 进阶用法

**理解过滤器逻辑**

`ULightMixerObjectFilter` 定义了此混合器的核心行为：它过滤出哪些类型的对象，以及在表格中默认显示哪些属性列。

```cpp
// 来源: LightMixerObjectFilter.h
// 创建一个过滤器实例来检查其配置
ULightMixerObjectFilter* Filter = NewObject<ULightMixerObjectFilter>();
TSet<UClass*> FilteredClasses = Filter->GetObjectClassesToFilter();
TSet<FName> DefaultColumns = Filter->GetColumnsToShowByDefault();

// 验证过滤器确实只关注灯光组件
if (FilteredClasses.Contains(ULightComponent::StaticClass()))
{
    UE_LOG(LogTemp, Log, TEXT("Light Mixer is configured to filter ULightComponent."));
}

// 检查默认显示的列
for (const FName& Column : DefaultColumns)
{
    UE_LOG(LogTemp, Log, TEXT("Default visible column: %s"), *Column.ToString());
}
```

## Demo 示例

以下示例展示了如何在你的编辑器工具或菜单扩展中集成“打开 Light Mixer”的功能。

```cpp
// MyEditorTool.h
#pragma once

#include "CoreMinimal.h"
#include "LightMixerModule.h"

class FMyEditorTool
{
public:
    static void OpenLightMixerWindow()
    {
        // 获取 Light Mixer 模块实例并打开它的标签页
        FLightMixerModule& LightMixerModule = FLightMixerModule::Get();
        FGlobalTabmanager::Get()->TryInvokeTab(LightMixerModule.GetTabSpawnerId());
    }
};
```

## 模块依赖

Light Mixer 依赖其父插件 **ObjectMixer**。要使用 Light Mixer，你的项目必须启用 `ObjectMixer` 插件。在模块的 `.Build.cs` 中，通常需要添加对 `ObjectMixer` 模块的依赖。

| 模块 | 用途 |
|---|---|
| `ObjectMixer` | 提供核心的对象混合器框架和表格视图功能，Light Mixer 在此基础上进行灯光专业化定制。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次错误的查找替换后重新提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤销编号为 CL51314860 的变更。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化注册问题，更新了代理接口的调用方式。 |
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 通过工具修复头文件，确保DLL导出宏正确应用于方法和静态变量。 |
| 2023-05-11 | `91c57d39` | Removed redundant module includes. | 移除了冗余的模块包含。 |

### 维护评价

Light Mixer 插件仍在**积极维护**中。
- **创建时间**：2022年，作为 UE5 新一代编辑器工具的一部分。
- **更新频率**：最近在 2026 年 2 月有多次更新，主要修复编译和初始化问题，说明它跟随引擎主线进行维护。
- **内容状态**：标记为 `IsBetaVersion=true`，表明它仍处于 Beta 测试阶段，API 或功能可能在未来版本中有所调整。
- **使用建议**：对于需要高效编辑场景灯光的项目，**推荐使用**。但需注意其 Beta 状态，关键工作流中应考虑备份。作为隐藏插件，需要在“插件”菜单中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ObjectMixer/LightMixer)
- [官方文档]() (暂无)