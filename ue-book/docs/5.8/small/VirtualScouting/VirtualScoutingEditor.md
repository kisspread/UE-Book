# Virtual Scouting

> Virtual Scouting lets filmmakers scout a digital environment in virtual reality.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟勘景 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（VR交互资产） |
| 模块 | `VirtualScouting` (Runtime), `VirtualScoutingEditor` (Runtime), `VirtualScoutingOpenXR` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting) | |

## 用途

Virtual Scouting 插件为电影制作人、建筑可视化师和场景设计师提供了一个在虚拟现实（VR）中实时探索和交互 Unreal Engine 数字环境的工具。它解决了传统实地勘景在远程协作、未建成场景预览、以及创意规划阶段的高成本和不便捷性问题，允许团队在沉浸式的 VR 环境中进行场景评估、镜头设计和协作标记。

## 使用场景

- 电影或剧集的导演、美术指导、摄影指导需要在数字场景中“走位”，规划镜头和演员动线。
- 建筑事务所的客户需要在VR中提前体验尚未建成的建筑空间，提供直观反馈。
- 虚拟制片（Virtual Production）项目在进行LED墙或绿幕拍摄前，需要在VR中预览和调整数字资产场景。
- 远程团队需要跨越地理限制，共同对同一个3D环境进行审阅和讨论。

## 蓝图用法

*（注：提供的源码信息中公共API较少，以下为基于插件典型功能的推断性描述。）*

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartVirtualScoutingSession` | 启动一个VR勘景会话，将用户传送至指定场景。 | `UVirtualScoutingSubsystem` (推测) |
| `PlaceBookmark` | 在当前VR位置放置一个书签或标记点。 | `UVirtualScoutingSubsystem` (推测) |
| `MeasureDistance` | 在VR中通过控制器选择两个点来测量距离。 | `UVirtualScoutingSubsystem` (推测) |
| `TakeSnapshot` | 捕获当前VR视角的截图或全景图。 | `UVirtualScoutingSubsystem` (推测) |

### 使用示例（蓝图描述）

在一个蓝图中，你可能会创建一个UI界面。当用户点击“开始勘景”按钮时，调用`StartVirtualScoutingSession`节点并传入目标场景的地图引用。在VR会话中，通过控制器手柄的特定按键（如侧键）触发`PlaceBookmark`节点，在重要位置留下标记。会话结束后，所有标记可以保存为数据资产供后续分析。

## C++ 用法

### 头文件引入

```cpp
#include "VirtualScoutingEditorModule.h"
```

### 基本用法

基于 `VirtualScoutingEditor` 模块的头部文件，其主要贡献是一个日志类别，用于记录该插件编辑器相关功能的调试信息。

```cpp
// 在你的编辑器工具或扩展代码中使用该插件的日志类别
UE_LOG(LogVirtualScoutingEditor, Log, TEXT("Virtual Scouting editor extension initialized."));
UE_LOG(LogVirtualScoutingEditor, Warning, TEXT("Failed to load VR template asset."));
```

**来源文件**: `Engine/Plugins/VirtualProduction/VirtualScouting/Source/VirtualScoutingEditor/Private/VirtualScoutingEditorModule.h`

### 进阶用法

该插件的功能核心（如VR交互、场景管理）很可能封装在 `VirtualScouting` 和 `VirtualScoutingOpenXR` 模块中。要进行深度集成，通常需要：
1.  引入这些运行时模块的头文件。
2.  通过子系统（Subsystem）或管理器（Manager）类访问核心API。
3.  处理OpenXR交互事件。

## Demo 示例

一个简单的示例，展示如何在编辑器工具中使用Virtual Scouting的日志类别进行信息记录。

```cpp
// MyVirtualScoutingTool.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "VirtualScoutingEditorModule.h" // 引入日志类别
#include "MyVirtualScoutingTool.generated.h"

UCLASS()
class UMyVirtualScoutingTool : public UObject
{
    GENERATED_BODY()

public:
    /** 一个模拟的工具函数，用于记录虚拟勘景相关的事件 */
    UFUNCTION(BlueprintCallable, Category = "Virtual Scouting Tool")
    void LogScoutingEvent(const FString& EventMessage);

    /** 模拟启动一个勘景任务 */
    UFUNCTION(BlueprintCallable, Category = "Virtual Scouting Tool")
    void SimulateStartScouting(const FString& SceneName);
};

// MyVirtualScoutingTool.cpp
#include "MyVirtualScoutingTool.h"

void UMyVirtualScoutingTool::LogScoutingEvent(const FString& EventMessage)
{
    // 使用插件专用的日志类别
    UE_LOG(LogVirtualScoutingEditor, Log, TEXT("Scouting Event: %s"), *EventMessage);
}

void UMyVirtualScoutingTool::SimulateStartScouting(const FString& SceneName)
{
    UE_LOG(LogVirtualScoutingEditor, Log, TEXT("Attempting to start virtual scouting in scene: %s"), *SceneName);
    // 此处将调用 VirtualScouting 模块的核心API，例如：
    // if (UVirtualScoutingSubsystem* Subsystem = GEditor->GetEditorSubsystem<UVirtualScoutingSubsystem>())
    // {
    //     Subsystem->StartSession(SceneName);
    // }
}
```

## 模块依赖

根据 `VirtualScoutingOpenXR` 模块的 Build.cs，存在一个独特的依赖关系。

| 模块 | 用途 |
|---|---|
| `VREditor` | 提供UE编辑器内VR交互的基础框架，用于集成VR控制和界面。 |

*（注：`VirtualScouting` 和 `VirtualScoutingEditor` 模块的详细依赖信息未提供，可能依赖于 `Core`， `Engine`， `HeadMountedDisplay` 等常见模块。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转为浮点的警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正32位与64位格式说明符与参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF。 |
| 2026-03-13 | `b1da5d8f` | [Gizmos] Remove GizmoEdMode from areas not covered by preflight checks | 移除未被预检覆盖的GizmoEdMode区域。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将 Base<Plugin>.ini 重命名为 Default<Plugin>.ini。 |

### 维护评价

- **创建时间**：2024年9月，是一个较新的插件。
- **更新频率**：从Git历史看，在创建后的1-2年内有持续更新，最近一次更新在2026年5月。
- **更新内容**：近期提交主要是代码质量改进（修复编译警告、日志宏迁移、重命名配置文件）和特定功能修复（Gizmos相关），而非重大新功能，表明插件处于稳定维护阶段。
- **状态评估**：**活跃维护**。插件仍在持续接收修复和改进，没有废弃迹象。
- **推荐使用**：**是**。作为Epic官方提供的Virtual Production工具链的一部分，适用于需要VR勘景功能的项目。但由于`EnabledByDefault`为`false`，使用前需在插件管理器中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting)
- [官方文档]()（未提供）