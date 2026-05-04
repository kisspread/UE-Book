# Motion Design Data Link Integration

> 

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Motion Design 工具箱集成） |
| 模块 | `AvalancheDataLink` (Runtime), `AvalancheDataLinkEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/AvalancheDataLink) | |

## 用途

AvalancheDataLink 是 Motion Design（Avalanche）系统与 DataLink 框架之间的桥梁插件。它解决的核心问题是：**如何将外部数据源（通过 DataLink 管道获取的数据）实时映射到 Motion Design 场景中的 Remote Control 控制器上**。

具体来说，这个插件：
1. 提供 `AAvaDataLinkActor` 作为场景中的数据链接执行器，管理一组 `UAvaDataLinkInstance` 实例
2. 每个 `UAvaDataLinkInstance` 封装了一个 `FDataLinkInstance`（数据链接定义）和一组输出处理器（Output Processors）
3. 核心处理器 `UAvaDataLinkRCProcessor` 将 DataLink 输出的 JSON 或结构体数据，通过字段名映射（Controller Mappings）写入 Remote Control Preset 的控制器值中
4. 支持类型自动提升（Promotion），例如 Bool→Int、Float→Double 等

这个插件最初位于 `Engine/Plugins/Experimental/` 下，于 2025 年 8 月迁移到 `Engine/Plugins/VirtualProduction/`，属于 Motion Design 虚拟制片工具链的一部分。

## 使用场景

- 你在使用 Motion Design 做虚拟制片图形模板，需要从外部数据源（如 JSON API、数据库）实时更新画面元素属性 → 用 AvalancheDataLink
- 你有一个 Remote Control Preset 控制着 Motion Design 场景中的文字、颜色、位置等，想通过数据驱动自动更新这些值 → 用 AvalancheDataLink
- 你需要在 Begin Play 时自动拉取外部数据并应用到场景 → 在 `AAvaDataLinkActor` 上勾选 `bExecuteOnBeginPlay`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecuteDataLinkInstances` | 执行所有关联的 DataLink 实例，拉取数据并应用到控制器 | `AAvaDataLinkActor` |
| `StopDataLinkInstances` | 停止所有正在运行的 DataLink 实例 | `AAvaDataLinkActor` |

### 使用示例（蓝图描述）

1. 在场景中放置一个 **Motion Design Data Link Actor**（通过 Motion Design 工具箱或直接拖入场景）
2. 在 Details 面板中，展开 **Data Link Instances** 数组，添加一个或多个实例
3. 每个实例中配置：
   - **Data Link Instance**：选择数据链接定义（指定数据源和管线）
   - **Output Processors**：添加一个 **Motion Design Data Link Remote Control Processor**
4. 在 Processor 中配置 **Output Field to Controller Mappings**：
   - **Output Field Name**：DataLink 输出中的字段名（如 JSON 路径 `"player.score"`）
   - **Target Controller**：选择要映射到的 Remote Control 控制器
5. 勾选 **Execute On Begin Play** 可在游戏开始时自动执行

## C++ 用法

### 头文件引入

```cpp
#include "AvaDataLinkActor.h"
#include "AvaDataLinkInstance.h"
```

### 基本用法

创建和执行 DataLink 实例：

```cpp
// 在场景中获取或创建 DataLink Actor
AAvaDataLinkActor* DataLinkActor = GetWorld()->SpawnActor<AAvaDataLinkActor>();

// 手动触发所有 DataLink 实例执行
DataLinkActor->ExecuteDataLinkInstances();

// 停止执行
DataLinkActor->StopDataLinkInstances();
```

### 进阶用法

自定义输出处理器。`UAvaDataLinkRCProcessor` 继承自 `UAvaDataLinkProcessor`（抽象类），你可以创建自己的处理器来处理 DataLink 输出：

```cpp
// 自定义处理器需继承 UAvaDataLinkProcessor 并实现 OnProcessOutput
UCLASS()
class UMyCustomProcessor : public UAvaDataLinkProcessor
{
    GENERATED_BODY()

protected:
    virtual void OnProcessOutput(const FDataLinkExecutor& InExecutor, FConstStructView InOutputDataView) override
    {
        // 处理 InOutputDataView 中的数据
        // 可以是 FJsonObjectWrapper（JSON 输出）或自定义 UStruct
    }
};
```

`UAvaDataLinkRCProcessor` 的内部逻辑展示了如何解析输出：
- 如果输出是 `FJsonObjectWrapper`，使用 `FJsonObjectConverter::JsonValueToUProperty` 将 JSON 值映射到控制器属性
- 如果是结构体输出，使用 `UE::DataLink::ResolveConstPropertyView` 按字段名查找，并支持类型提升（Bool→Int、Float→Double 等）

## Demo 示例

最小示例：创建一个自定义 DataLink 处理器

```cpp
// MyProcessor.h
#pragma once

#include "AvaDataLinkProcessor.h"
#include "MyProcessor.generated.h"

UCLASS(DisplayName="My Custom Data Link Processor")
class UMyProcessor : public UAvaDataLinkProcessor
{
    GENERATED_BODY()

protected:
    virtual void OnProcessOutput(const FDataLinkExecutor& InExecutor, FConstStructView InOutputDataView) override
    {
        // 在此处理 DataLink 的输出数据
        // InOutputDataView 包含从数据源拉取的结果
    }
};
```

```cpp
// MyModule.Build.cs - 添加依赖
PublicDependencyModuleNames.AddRange(new string[]
{
    "AvalancheDataLink",
});
```

## 模块依赖

### AvalancheDataLink (Runtime)

| 模块 | 用途 |
|---|---|
| `AvalancheRemoteControl` | Avalanche Remote Control 集成（提供 `FAvaRCControllerId`） |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `DataLink` | DataLink 数据链接框架 |
| `Avalanche` | Motion Design 核心（`UAvaSceneSubsystem`） |
| `DataLinkJson` | DataLink JSON 工具（`FindJsonValue`） |
| `Engine` | 引擎核心 |
| `Json` / `JsonUtilities` | JSON 解析 |
| `PropertyBindingUtils` | 属性兼容性检查和类型提升 |
| `RemoteControl` / `RemoteControlLogic` | Remote Control Preset 和控制器系统 |

### AvalancheDataLinkEditor (Editor)

| 模块 | 用途 |
|---|---|
| `AvalancheDataLink` | 运行时模块 |
| `AvalancheInteractiveTools` | Motion Design 交互工具框架 |
| `PropertyEditor` | Details 面板自定义 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能 |

## 维护状态

### 近期更新

1. `f25e96ca6e25` | 2025-08-27 | Motion Design: set the scene state and data link plugins to beta
   - 将插件从实验性标记为 Beta，表明 Epic 认为其已具备基本可用性
2. `94f961385e8e` | 2025-08-27 | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
   - 从 `Engine/Plugins/Experimental/` 迁移到 `Engine/Plugins/VirtualProduction/`，文件无实质改动（纯移动）
3. `16941e38f207` | 2025-08-12 | MotionDesign: EditorInteractiveTools - Fixed preview actor spawned infinitely
   - 修复编辑器交互工具中的 bug，属于 Motion Design 工具链的通用修复

### 维护评价

- **创建时间**: 2025 年 4 月，非常新的插件（约 1 年）
- **维护状态**: 活跃维护中。2025 年 8 月刚从 Experimental 迁移到 VirtualProduction 并标记为 Beta
- **注意事项**: 插件仍标记为 `IsBetaVersion=true`，API 可能发生变化。5.7 中已废弃 `ControllerMappings` 属性，改为使用通用的 `OutputProcessors` 数组
- **依赖链较重**: 依赖 Remote Control、Avalanche、DataLink 三个插件体系，不适合独立使用
- **推荐**: 如果你在使用 Motion Design 虚拟制片工具链且需要数据驱动，这是官方推荐方案。不建议在非 Motion Design 场景中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/AvalancheDataLink)
- [DataLink 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)（数据链接框架）
- [Avalanche 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)（Motion Design 核心）
- [Remote Control 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlAPI)（远程控制）
