# Modeling Tools Editor Mode

> Modeling Tools Mode includes a suite of interactive tools for creating and editing meshes in the Editor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 建模工具编辑器模式 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelingToolsEditorMode` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-27 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ModelingToolsEditorMode) | |

## 用途

这是一个为 Unreal Engine 5 编辑器提供**交互式网格建模工具**的插件。它并非传统的静态网格编辑器，而是一个完整的**编辑器模式**，包含了一整套用于在编辑器内直接创建、修改和操作 3D 网格资产的工具。

它解决的核心问题是：在传统工作流中，创建或编辑简单的网格资产通常需要离开引擎，使用外部建模软件（如 Blender、Maya）。此插件通过提供类似 Blender 或 Maya 中基础建模工具的 UE 内集成方案，极大地简化了原型设计、关卡快速搭建和资产调整的流程，无需离开编辑器。

## 使用场景

- 你需要快速创建一个简单的几何体（如楼梯、圆柱、箭头）用于关卡原型设计 → 使用 `Add Box Primitive`, `Add Stairs Primitive` 等工具。
- 你需要对现有的静态网格资产进行低层次的编辑，例如修复拓扑、平滑表面、调整 UV → 使用 `Sculpt Mesh`, `PolyEdit`, `UV Layout` 等工具。
- 你需要执行布尔操作（如切割、合并）来组合或修改网格 → 使用 `Mesh Boolean`, `Mesh Trim`, `Plane Cut` 等工具。
- 你需要为网格创建或编辑碰撞体 → 使用 `Set Collision Geometry`, `Edit Collision Geometry` 等工具。
- 你需要对网格顶点进行绘制（如顶点颜色、权重）→ 使用 `Mesh Vertex Paint`, `Skin Weights Paint` 等工具。
- 你需要管理网格的多级细节（LOD）→ 使用 `LOD Manager` 工具。

## 蓝图用法

此插件主要提供编辑器模式和交互式工具，其核心 API 面向 C++ 的交互式工具框架。暴露给蓝图的接口有限，主要集中在**设置和配置**层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAssetGenerationLocation` | 获取当前设置的资产自动生成路径策略 | `UModelingToolsEditorModeSettings` |
| `GetAssetGenerationMode` | 获取当前设置的资产自动生成保存策略 | `UModelingToolsEditorModeSettings` |
| `GetDefaultMeshObjectType` | 获取新建网格对象的默认类型（静态网格、体积、动态网格） | `UModelingToolsEditorModeSettings` |
| `GetMeshSelectionsEnabled` | 获取网格元素选择系统是否启用 | `UModelingToolsEditorModeSettings` |

### 使用示例（蓝图描述）

蓝图中主要通过“项目设置”来配置此模式。要修改设置，你可以：
1.  在蓝图中使用 `Get Class Defaults` 节点，并选择 `ModelingToolsEditorModeSettings` 类来读取当前配置。
2.  要修改配置，需要通过 `Project Settings` -> `Plugins` -> `Modeling Mode` 界面，或者在 C++ 中获取 `UModelingToolsEditorModeSettings` 的单例对象进行修改。蓝图中直接修改这些设置不常见，因为它们是编辑器全局配置。

## C++ 用法

C++ 用法主要围绕**扩展**和**自定义**此编辑器模式。

### 头文件引入

```cpp
#include "ModelingToolsEditorMode.h"
#include "ModelingToolsEditorModeSettings.h"
#include "ModelingModeToolExtensions.h"
```

### 基本用法

**1. 以编程方式进入建模模式**
通常，用户通过编辑器界面手动进入建模模式。在 C++ 中，可以通过激活对应的编辑器模式 ID 来实现。
```cpp
// 获取建模模式的唯一标识符
const FEditorModeID& ModelingModeId = UModelingToolsEditorMode::EM_ModelingToolsEditorModeId;

// 激活该模式
GLevelEditorModeTools().ActivateMode(ModelingModeId);
```

**2. 读取和修改建模模式的项目设置**
(来源：`UModelingToolsEditorModeSettings`)
```cpp
// 获取设置对象（单例）
UModelingToolsEditorModeSettings* Settings = GetMutableDefault<UModelingToolsEditorModeSettings>();

// 读取资产生成位置设置
EModelingModeAssetGenerationLocation Location = Settings->GetAssetGenerationLocation();

// 修改资产生成行为（例如，改为自动保存）
Settings->SetAssetGenerationMode(EModelingModeAssetGenerationBehavior::AutoGenerateAndAutosave);
```

### 进阶用法

**1. 为建模模式添加自定义工具扩展**
这是插件提供的最强大的扩展机制。你可以创建一个新的插件，通过实现 `IModelingModeToolExtension` 接口，将你的自定义工具注册到建模模式中。
(来源：`IModelingModeToolExtension`)

```cpp
// MyModelingExtension.h
#pragma once
#include "ModelingModeToolExtensions.h"

class FMyModelingExtension : public IModelingModeToolExtension
{
public:
    virtual FText GetExtensionName() override;
    virtual FText GetToolSectionName() override;
    virtual void GetExtensionTools(const FExtensionToolQueryInfo& QueryInfo, TArray<FExtensionToolDescription>& ToolsOut) override;
};

// MyModelingExtension.cpp
#include "MyModelingExtension.h"
#include "MyToolBuilder.h" // 你自己的工具构建器类

FText FMyModelingExtension::GetExtensionName()
{
    return NSLOCTEXT("MyExtension", "Name", "My Custom Tools");
}

FText FMyModelingExtension::GetToolSectionName()
{
    // 你的工具将出现在建模工具面板中的哪个分页（分类）
    return NSLOCTEXT("MyExtension", "Section", "Custom Tools");
}

void FMyModelingExtension::GetExtensionTools(const FExtensionToolQueryInfo& QueryInfo, TArray<FExtensionToolDescription>& ToolsOut)
{
    if (!QueryInfo.bIsInfoQueryOnly)
    {
        FExtensionToolDescription ToolDesc;
        ToolDesc.ToolName = NSLOCTEXT("MyExtension", "ToolName", "My Awesome Tool");
        ToolDesc.ToolCommand = ...; // 创建一个 FUICommandInfo
        ToolDesc.ToolBuilder = NewObject<UMyToolBuilder>(); // 你的工具构建器实例
        ToolsOut.Add(ToolDesc);
    }
}

// 在你的插件模块启动时注册扩展
void FMyPluginModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(
        IModelingModeToolExtension::GetModularFeatureName(),
        new FMyModelingExtension()
    );
}
```

## Demo 示例

一个展示如何通过 C++ 获取建模模式设置的最小示例。

**MyModelingModeHelper.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ModelingToolsEditorModeSettings.h" // 引入设置头文件
#include "MyModelingModeHelper.generated.h"

UCLASS()
class UMyModelingModeHelper : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    /** 获取建模模式下一次创建网格对象的默认类型 */
    UFUNCTION(BlueprintPure, Category = "Modeling|Settings")
    static EModelingModeDefaultMeshObjectType GetDefaultMeshObjectType();

    /** 设置建模模式下一次创建网格对象的默认类型 */
    UFUNCTION(BlueprintCallable, Category = "Modeling|Settings")
    static void SetDefaultMeshObjectType(EModelingModeDefaultMeshObjectType NewType);
};
```

**MyModelingModeHelper.cpp**
```cpp
#include "MyModelingModeHelper.h"
#include "ModelingToolsEditorModeSettings.h"

EModelingModeDefaultMeshObjectType UMyModelingModeHelper::GetDefaultMeshObjectType()
{
    UModelingToolsEditorModeSettings* Settings = GetMutableDefault<UModelingToolsEditorModeSettings>();
    if (Settings)
    {
        return Settings->DefaultMeshObjectType;
    }
    return EModelingModeDefaultMeshObjectType::StaticMeshAsset; // 默认值
}

void UMyModelingModeHelper::SetDefaultMeshObjectType(EModelingModeDefaultMeshObjectType NewType)
{
    UModelingToolsEditorModeSettings* Settings = GetMutableDefault<UModelingToolsEditorModeSettings>();
    if (Settings)
    {
        Settings->DefaultMeshObjectType = NewType;
        // 可选：通知设置已更改，以便UI刷新
        Settings->PostEditChange();
    }
}
```

## 模块依赖

从 `Build.cs` 和 `.uplugin` 依赖分析，使用者需要添加以下模块依赖：

| 模块 | 用途 |
|---|---|
| `MeshModelingToolset` | 提供核心的网格建模工具实现 |
| `MeshModelingToolsetExp` | 提供实验性的网格建模工具 |
| `MeshLODToolset` | 提供网格LOD生成和管理工具 |
| `ToolPresets` | 提供工具预设（Preset）管理功能 |
| `StylusInput` | 提供手绘板/压感笔输入支持（用于雕刻等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 为顶点属性绘制和蒙皮权重绘制工具新增了跨模式同步笔刷半径的选项 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点属性绘制工具的笔画累加器以支持松弛笔刷，并修复相关问题 |
| 2026-05-14 | `351412fd` | [Backout] - CL53956416 | 撤销（Backout）了一个提交（CL53956416） |
| 2026-05-14 | `7bd975ac` | [ModelingTools] Add Polygroup color mode to SkinWeights and VertexAttribute paint tools | 为蒙皮权重和顶点属性绘制工具添加了基于多边形组的颜色显示模式 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下可能导致双精度常量截断为浮点数的警告 |

### 维护评价

- **创建时间**：约 5 年（2021年），属于较新的插件。
- **活跃度**：**非常活跃**。最近一次提交（2026-05-27）距今很短，且近期更新频繁，内容涉及新功能、重构和错误修复，表明 Epic Games 持续投入开发。
- **状态**：虽然 `.uplugin` 中标记为 `IsBetaVersion: true`，但从更新频率和深度看，它已是**功能成熟且仍在积极迭代**的核心编辑器功能。建议在非关键生产环境中使用，或做好版本更新可能带来工作流变化的准备。
- **推荐**：**强烈推荐**给任何需要在编辑器内进行快速原型制作、关卡设计或网格资产调整的团队。它是 UE5 标准建模工作流的基石。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ModelingToolsEditorMode)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/modeling-mode-in-unreal-engine/) (无 .uplugin 中 DocsURL，提供引擎文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ModelingToolsEditorMode/Tests) (如果存在)