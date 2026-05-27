# Mesh Terrain Mode

> Mesh Terrain Mode includes a suite of interactive tools for creating and editing Mesh Partitions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 网格分区模式 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、资产、UI组件） |
| 模块 | `MeshTerrainMode` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshTerrainMode) | |

## 用途

Mesh Terrain Mode 是 UE 内置 Modeling Tools Editor Mode 的一个定制化和扩展实现，专门用于 **Mesh Partition** 的工作流。它提供了一个完整的、交互式的编辑器模式，包含了一整套工具，用于在编辑器中创建、编辑、管理和优化“网格分区”（Mesh Partition）资产。

这个插件解决的核心问题是：**如何在大型世界（如开放世界地形）中高效地创建、管理和编辑大型、复杂的网格资产**。它提供了从基础形状创建（立方体、圆柱体）、多边形建模（拉伸、切割、平滑）、雕刻（移动、平滑、膨胀）、网格操作（布尔运算、简化、重新拓扑、UV编辑）到资产转换（合并、拆分、转换为静态网格/体积/动态网格）的完整工具链。它还集成了专门的子模式（Submodes）、自定义的属性面板、预设系统和资产自动生成管理，旨在为网格分区工作流提供一个高度优化和集成的创作环境。

## 使用场景

- **创建和编辑大型地形网格**：使用`BeginAddBoxPrimitiveTool`、`BeginDrawSplineTool`等创建基础地形形状，再用`BeginSculptMeshTool`、`BeginHeightSculptTool`等进行地形雕刻和编辑。
- **管理复杂的网格资产**：使用`BeginCombineMeshesTool`、`BeginSplitMeshesTool`、`BeginConvertMeshesTool`等工具对网格进行合并、拆分和格式转换。
- **优化网格性能**：使用`BeginSimplifyMeshTool`、`BeginRemeshMeshTool`、`BeginLODManagerTool`来简化网格拓扑、重新网格化和管理LOD。
- **快速原型化与布尔操作**：使用`BeginMeshBooleanTool`、`BeginMeshTrimTool`、`BeginCutMeshWithMeshTool`进行复杂的布尔和切割操作。
- **自动生成和管理资产**：插件内置了资产自动生成系统，可以根据设置（`UMeshTerrainModeSettings`）自动创建和保存静态网格、动态网格或体积资产。

## 蓝图用法

该插件主要作为编辑器模式运行，其核心蓝图可调用功能主要通过命令系统暴露。以下是从源码中提取的核心功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginAddBoxPrimitiveTool` | 启动添加立方体图元工具 | `FMeshTerrainModeManagerCommands` |
| `BeginSculptMeshTool` | 启动网格雕刻工具 | `FMeshTerrainModeManagerCommands` |
| `BeginCubeGridTool` | 启动立方体网格工具 | `FMeshTerrainModeManagerCommands` |
| `BeginMeshBooleanTool` | 启动网格布尔运算工具 | `FMeshTerrainModeManagerCommands` |
| `BeginSimplifyMeshTool` | 启动网格简化工具 | `FMeshTerrainModeManagerCommands` |
| `BeginCombineMeshesTool` | 启动合并网格工具 | `FMeshTerrainModeManagerCommands` |
| `BeginSplitMeshesTool` | 启动拆分网格工具 | `FMeshTerrainModeManagerCommands` |
| `BeginConvertMeshesTool` | 启动网格转换工具 | `FMeshTerrainModeManagerCommands` |
| `BeginHeightSculptTool` | 启动高度雕刻工具 | `FMeshTerrainModeManagerCommands` |
| `BeginAddModifierTool` | 启动添加修改器工具 | `FMeshTerrainModeManagerCommands` |
| `EnterSculptSubmode` | 切换到雕刻子模式 | `FMeshTerrainModeManagerCommands` |
| `EnterCreateSubmode` | 切换到创建子模式 | `FMeshTerrainModeManagerCommands` |
| `EnterEditSubmode` | 切换到编辑子模式 | `FMeshTerrainModeManagerCommands` |
| `BeginSelectionAction_Delete` | 删除当前选择 | `FMeshTerrainModeManagerCommands` |
| `BeginSelectionAction_ExpandToConnected` | 选择所有连接元素 | `FMeshTerrainModeManagerCommands` |
| `LaunchUVEditor` | 启动 UV 编辑器 | `FMeshTerrainModeManagerCommands` |

**使用示例（蓝图描述）**
在蓝图中，你通常不会直接调用这些命令来启动工具。更常见的用法是：
1.  **通过编辑器模式面板操作**：用户通过编辑器顶部的模式（Mode）选项卡切换到“Mesh Terrain Mode”，然后通过右侧的子模式面板（如创建、编辑、雕刻）选择具体的工具按钮。
2.  **通过控制台命令**：某些工具可能注册了控制台命令，可以在关卡视口底部的控制台输入。
3.  **通过C++扩展**：开发者可以通过实现 `IMeshTerrainModeToolExtension` 接口来为该模式添加自定义工具和子模式。

## C++ 用法

该插件的 C++ 接口主要用于**扩展**和**自定义**编辑器模式的行为。

### 头文件引入

```cpp
#include "MeshTerrainModeModule.h"
#include "MeshTerrainMode.h"
#include "MeshTerrainModeToolExtensions.h"
```

### 基本用法（注册自定义工具扩展）

（示例来源于 `IMeshTerrainModeToolExtension` 接口定义）

你可以创建一个插件来为 Mesh Terrain Mode 添加自定义工具。这需要实现 `IMeshTerrainModeToolExtension` 接口，并将其作为模块化特性注册。

```cpp
// MyCustomExtension.h
#pragma once
#include "MeshTerrainModeToolExtensions.h"

class FMyCustomToolExtension : public IMeshTerrainModeToolExtension
{
public:
    // 返回要添加到现有子模式的工具
    virtual void GetExtensionSubmodeAddons(TArray<FExtensionSubmodeAddon>& AddonsOut) override;
    
    // 返回要作为新子模式暴露的工具集
    virtual void GetExtensionSubmodes(TArray<FExtensionSubmodeDescription>& SubmodesOut) override;
    
    // 返回自定义工具，可覆盖默认的执行、检查和选中行为
    virtual void GetExtensionCustomTools(const FExtensionToolQueryInfo& QueryInfo, TArray<FExtensionCustomToolDescription>& OutTools) override;
};

// MyCustomExtension.cpp
#include "MyCustomExtension.h"
#include "IModularFeatures.h"

void FMyCustomToolExtension::GetExtensionSubmodeAddons(TArray<FExtensionSubmodeAddon>& AddonsOut)
{
    // 示例：向“创建”子模式添加一个自定义工具
    FSubmodeToolPalette MyPalette(LOCTEXT("MyPalette", "My Tools"), { /* ... 命令列表 ... */ });
    AddonsOut.Emplace(FName("CreateSubmode"), MyPalette);
}

void FMyCustomToolExtension::GetExtensionSubmodes(TArray<FExtensionSubmodeDescription>& SubmodesOut)
{
    // 创建一个全新的子模式
    FExtensionSubmodeDescription Desc;
    Desc.MakeNewSubmode = [this]() -> TSharedPtr<FSubmode> { /* ... 创建并返回你的 FSubmode 子类 ... */ };
    SubmodesOut.Add(Desc);
}

void FMyCustomToolExtension::GetExtensionCustomTools(const FExtensionToolQueryInfo& QueryInfo, TArray<FExtensionCustomToolDescription>& OutTools)
{
    // 定义一个自定义工具
    FExtensionCustomToolDescription ToolDesc;
    ToolDesc.ToolName = TEXT("MyCustomTool");
    ToolDesc.ToolBuilder = /* ... 你的 UInteractiveToolBuilder 实例 ... */;
    // 可选：覆盖默认行为
    ToolDesc.ExecuteAction = [](UInteractiveToolManager* Manager, EToolSide Side) -> bool { /* ... 自定义执行逻辑 ... */ return true; };
    OutTools.Add(ToolDesc);
}

// 在你的模块 StartupModule 中注册
void FMyExtensionModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(
        IMeshTerrainModeToolExtension::GetModularFeatureName(),
        &MyExtensionInstance);
}
```

### 进阶用法（监听模式事件）

你可以通过 `UMeshTerrainMode` 类来监听模式进入、退出以及工具启动等事件。

```cpp
// 假设你有对 UMeshTerrainMode 实例的引用（例如通过 GetMutableDefault<UMeshTerrainMode>()）
UMeshTerrainMode* MeshTerrainMode = /* ... */;
if (MeshTerrainMode)
{
    // 监听工具启动
    MeshTerrainMode->OnToolStarted.AddLambda([](UInteractiveToolManager* Manager, UInteractiveTool* Tool)
    {
        UE_LOG(LogTemp, Log, TEXT("Mesh Terrain Mode tool started: %s"), *Tool->GetClass()->GetName());
    });
}
```

## Demo 示例

一个最小化的、用于向 Mesh Terrain Mode 添加自定义工具扩展的 C++ 模块示例。

```cpp
// CustomMeshTerrainToolExtension.h
#pragma once
#include "MeshTerrainModeToolExtensions.h"
#include "UObject/NoExportTypes.h"

class UCustomToolBuilder;

class FCustomMeshTerrainToolExtension : public IMeshTerrainModeToolExtension
{
public:
    virtual ~FCustomMeshTerrainToolExtension() override;

    virtual void GetExtensionCustomTools(const FExtensionToolQueryInfo& QueryInfo, TArray<FExtensionCustomToolDescription>& OutTools) override;

    static FName GetExtensionName() { return TEXT("CustomMeshTerrainToolExtension"); }

private:
    // 持有工具构建器，确保生命周期
    UPROPERTY()
    TObjectPtr<UCustomToolBuilder> CustomToolBuilder;
};
```

```cpp
// CustomMeshTerrainToolExtension.cpp
#include "CustomMeshTerrainToolExtension.h"
#include "CustomToolBuilder.h" // 假设这是你定义的工具构建器
#include "IModularFeatures.h"

FCustomMeshTerrainToolExtension::~FCustomMeshTerrainToolExtension()
{
    // 反注册
    IModularFeatures::Get().UnregisterModularFeature(IMeshTerrainModeToolExtension::GetModularFeatureName(), this);
}

void FCustomMeshTerrainToolExtension::GetExtensionCustomTools(const FExtensionToolQueryInfo& QueryInfo, TArray<FExtensionCustomToolDescription>& OutTools)
{
    if (!CustomToolBuilder)
    {
        CustomToolBuilder = NewObject<UCustomToolBuilder>();
    }

    FExtensionCustomToolDescription ToolDesc;
    ToolDesc.ToolName = TEXT("MyAwesomeTool");
    ToolDesc.ToolBuilder = CustomToolBuilder;
    // 可以添加到特定的子模式
    // ToolDesc.SubmodeName = FName("EditSubmode");
    OutTools.Add(ToolDesc);
}

// 在某个模块的 StartupModule 中，创建并注册这个扩展实例
static FCustomMeshTerrainToolExtension* CustomExtension = nullptr;

void FMyCustomToolsModule::StartupModule()
{
    CustomExtension = new FCustomMeshTerrainToolExtension();
    IModularFeatures::Get().RegisterModularFeature(IMeshTerrainModeToolExtension::GetModularFeatureName(), CustomExtension);
}

void FMyCustomToolsModule::ShutdownModule()
{
    if (CustomExtension)
    {
        IModularFeatures::Get().UnregisterModularFeature(IMeshTerrainModeToolExtension::GetModularFeatureName(), CustomExtension);
        delete CustomExtension;
        CustomExtension = nullptr;
    }
}
```

## 模块依赖

从源码结构和典型UE编辑器模式插件推断，使用该插件或对其进行扩展时，你的模块可能需要依赖以下模块（除了常见的Core/Engine等）：

| 模块 | 用途 |
|---|---|
| `MeshTerrainMode` | 核心模式模块，包含编辑器模式定义、工具注册、UI等。 |
| `ModelingTools` | 提供基础的建模工具框架（UInteractiveTool等），Mesh Terrain Mode 的工具大量基于此。 |
| `GeometryProcessing` | 提供几何处理算法（网格简化、重新网格化、布尔运算等）。 |
| `InteractiveToolsFramework` | 提供交互工具框架和输入行为系统。 |
| `GeometryFramework` | 提供动态网格（UDynamicMesh）相关支持。 |
| `UnrealEd` | 提供编辑器模式（UEdMode）、工具包（FModeToolkit）等基础支持。 |
| `Slate` / `SlateCore` | 用于构建复杂的编辑器UI，如工具面板、属性自定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `29739ffe` | Mesh Terrain: guard against auto-accepting a tool result during level Reload operation | 防止在关卡重载时工具结果被意外自动接受 |
| 2026-05-20 | `5c588ff7` | MeshPartition: Block editor duplicating the active tool's target actors in mesh terrain mode | 阻止编辑器在网格地形模式中复制活动工具的目标Actor |
| 2026-05-19 | `a261fff3` | Fix editor shutdown crash: Use SP-lambda + weak-capture Slate widgets in MeshTerrainMode OnModified | 修复编辑器关闭崩溃：在OnModified中使用智能指针Lambda并弱捕获Slate控件 |
| 2026-05-15 | `0ddb912e` | [Mesh Partition] Fixed MeshTerrainMode pulling Mesh Partition as plugin dependency only for editor t | 修复了网格地形模式将网格分区作为插件依赖项仅用于编辑器的拉取问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数时产生警告的代码 |

### 维护评价

- **状态**：**活跃维护**
- **年龄**：🆕（创建于2026年3月，非常新的插件）
- **频率**：在创建后的2-3个月内有密集的更新（2026年5月），主要修复了多个编辑器稳定性和功能错误。
- **内容**：更新聚焦于修复使用中的具体问题（崩溃、意外行为），表明插件正在被实际使用和测试。
- **结论**：该插件处于活跃开发和完善阶段，作为实验性功能正在快速迭代。它提供了一套强大且复杂的网格编辑工具集。虽然作为实验性功能可能存在稳定性风险，但对于需要高级网格分区和编辑工作流的项目来说，**值得尝试和关注**。建议在项目中使用，并密切关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshTerrainMode)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain#meshterrainmode)