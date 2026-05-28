# Procedural Vegetation Editor

> Node Graph based Editor that allows users to create Nanite Foliage ready vegetation directly in the engine. Users can load Procedural Vegetation Presets that contain prebuilt data for a species, and customize/create variations using the node graph.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化植被编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、预设资源、导出功能） |
| 模块 | `ProceduralVegetation` (Runtime), `ProceduralVegetationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ProceduralVegetationEditor) | |

## 用途

这是一个基于节点图的程序化植被创作工具，旨在解决 Nanite Foliage（纳米叶）技术下，高效创建和编辑高质量植被资产的问题。它提供了一个可视化的编辑器环境，允许艺术家和技术美术直接在引擎内工作，而不是依赖外部 DCC 工具。其核心功能是将复杂的植被生成流程抽象为可连接的节点图，用户可以加载包含树木、灌木等物种基础数据的“程序化植被预设”，并通过修改节点参数、连接关系或添加新节点，来创造该物种的无穷变体。

**为什么存在**：为了简化 Nanite Foliage-ready 植被的制作流程。传统方式需要多个软件配合，而此插件将建模、LOD 生成、风动画、物理碰撞等流程整合到一个统一的、基于 PCG 的节点图编辑器中，加速迭代并确保资产符合 Nanite 的要求。

## 使用场景

- **游戏环境美术**：你需要快速为开放世界游戏创建大量不同形态的树木或灌木，同时确保它们都支持 Nanite 和 Foliage 系统。可以使用此插件加载“松树预设”，然后通过调整“生长角度”、“分支密度”等节点参数来生成一片树林，而每棵树都略有不同。
- **技术美术**：你需要为一种植物创建一个带有自定义风力动画和物理碰撞的版本。你可以在此编辑器的节点图中连接“风力模拟”节点和“碰撞体生成”节点，直接预览效果并导出为包含骨架和物理资产的 Skeletal Mesh。
- **快速原型**：在前期预研阶段，你需要快速验证某种植被在游戏场景中的表现。你可以使用内置的预设快速生成基础形态，并通过编辑器实时预览其在场景中的大小、密度以及与其他物体的交互（如通过“物体交互”节点调整碰撞）。
- **资产优化**：你可以利用编辑器内置的统计面板（如点数、三角形数、叶数等）来分析和优化植被资产的复杂度，并通过导出设置控制 Nanite 和 LOD 的具体参数。

## 蓝图用法

此插件主要是一个**编辑器扩展工具**，其核心功能（节点图编辑、资产预览、导出）都运行在编辑器环境中。它不直接提供可在运行时（Runtime）调用的蓝图节点。然而，它生成的最终资产（如 StaticMesh、SkeletalMesh）是标准的引擎资产，可以在蓝图中像其他资产一样使用。

### 核心资产

插件的核心资产类型是 `UProceduralVegetation`，它代表一个完整的植被生成程序或预设。

| 操作 | 说明 | 所在类/资产类型 |
|---|---|---|
| **创建新资产** | 在内容浏览器中右键 -> 创建 -> 其他 -> 程序化植被 | `UProceduralVegetation` |
| **编辑资产** | 双击 `UProceduralVegetation` 资产，将打开程序化植被编辑器窗口。 | `FPVEditor` |
| **导出最终网格体** | 在编辑器工具栏点击“导出”按钮，将根据节点图生成 StaticMesh 或 SkeletalMesh。 | `UPVExportSettings` |

## C++ 用法

此插件主要面向编辑器，其 C++ API 主要用于扩展编辑器功能或自定义节点。以下是基于源码分析的典型用法。

### 头文件引入

```cpp
// 引用运行时数据模块
#include "DataTypes/PVData.h"

// 引用编辑器模块（仅在编辑器模块中使用）
#include "ProceduralVegetationEditorModule.h"
#include "PVEditor.h"
```

### 基本用法：创建自定义可视化节点（概念）

此插件基于 PCG 框架，自定义节点需继承自 `UPCGSettings`。以下为一个假设的“自定义生长”节点头文件示例。

```cpp
// MyCustomGrowthNode.h
#pragma once

#include "PCGSettings.h"
#include "MyCustomGrowthNode.generated.h"

UCLASS(BlueprintType, EditInlineNew, Category = "PV|Growth")
class UMyCustomGrowthSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings)
    float GrowthIntensity = 1.0f;

    // ... 其他属性

protected:
    //~ Begin UPCGSettings interface
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;
    //~ End UPCGSettings interface
};
```

```cpp
// MyCustomGrowthNode.cpp
#include "MyCustomGrowthNode.h"

FPCGElementPtr UMyCustomGrowthSettings::CreateElement() const
{
    return MakeShared<FMyCustomGrowthElement>();
}

// 执行逻辑封装在 FPCGElement 子类中
class FMyCustomGrowthElement : public FSimplePCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        // 从 Context 获取输入的 FManagedArrayCollection (植被数据)
        // 根据 UMyCustomGrowthSettings 的参数修改数据
        // 输出修改后的数据
        return true;
    }
};
```

### 进阶用法：扩展编辑器工具

插件提供工具基类 `UPVBaseInteractiveTool` 用于创建自定义的交互式编辑工具（如拖拽、点击编辑）。你可以继承它来为特定的节点创建专属工具。

```cpp
// 假设的自定义工具头文件
#pragma once

#include "Tools/PVBaseInteractiveTool.h"
#include "InteractiveToolBuilder.h"
#include "MyCustomTool.generated.h"

UCLASS()
class UMyCustomNodeSettings : public UPVBaseSettings
{
    GENERATED_BODY()
    // ... 节点设置
};

UCLASS()
class UMyCustomToolBuilder : public UInteractiveToolBuilder
{
    GENERATED_BODY()
    virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override { return true; }
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override;
};

UCLASS()
class UMyCustomTool : public UPVBaseInteractiveTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;
    virtual void OnTick(float DeltaTime) override;
    // ... 实现鼠标点击、悬停等交互逻辑
};
```

## Demo 示例

以下是一个最小化的、可编译的自定义节点示例，展示了如何创建一个简单的“缩放点云”节点。

**MyScalePointsNode.h**
```cpp
#pragma once
#include "PCGSettings.h"
#include "MyScalePointsNode.generated.h"

UCLASS(BlueprintType, EditInlineNew, Category = "PV|Transform")
class UMyScalePointsNodeSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Parameters", meta = (ClampMin = "0.0"))
    float ScaleFactor = 1.0f;

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;
};
```

**MyScalePointsNode.cpp**
```cpp
#include "MyScalePointsNode.h"
#include "PCGContext.h"
#include "PCGData.h"
#include "DataTypes/PVData.h"

TArray<FPCGPinProperties> UMyScalePointsNodeSettings::InputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace_GetRef(TEXT("Input"), EPCGDataType::Any).SetRequired();
    return PinProperties;
}

TArray<FPCGPinProperties> UMyScalePointsNodeSettings::OutputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace_GetRef(TEXT("Output"), EPCGDataType::Any);
    return PinProperties;
}

FPCGElementPtr UMyScalePointsNodeSettings::CreateElement() const
{
    return MakeShared<FMyScalePointsElement>();
}

class FMyScalePointsElement : public FSimplePCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        const UMyScalePointsNodeSettings* Settings = Context->GetInputSettings<UMyScalePointsNodeSettings>();
        check(Settings);

        TArray<FPCGTaggedData> Inputs = Context->InputData.GetInputs();
        TArray<FPCGTaggedData>& Outputs = Context->OutputData.TaggedData;

        for (const FPCGTaggedData& Input : Inputs)
        {
            const UPCGData* Data = Input.Data;
            if (const UPVData* PVData = Cast<UPVData>(Data))
            {
                // 浅拷贝输入数据
                UPVData* OutputData = Cast<UPVData>(PVData->DuplicateData(Context));
                if (OutputData)
                {
                    FManagedArrayCollection& Collection = OutputData->GetMutableCollection();
                    // 假设存在一个名为 "PointPosition" 的点位置属性
                    TManagedArray<FVector3f>* Positions = Collection.FindAttribute<FVector3f>(TEXT("PointPosition"));
                    if (Positions)
                    {
                        for (FVector3f& Pos : *Positions)
                        {
                            Pos *= Settings->ScaleFactor;
                        }
                    }
                    Outputs.Emplace_GetRef() = { OutputData, Input.Tags };
                }
            }
        }

        return true;
    }
};
```

**如何使用**：
1.  将 `UMyScalePointsNodeSettings` 类编译到你的编辑器模块中。
2.  重启编辑器后，在程序化植被编辑器的节点图中，右键点击并查找“Scale Points”节点，将其添加到图中。
3.  将其输入连接到上游节点（例如一个种子节点），设置“ScaleFactor”，然后运行图表。输出将是缩放后的点云数据。

## 模块依赖

此插件的模块依赖关系较为复杂，主要围绕 PCG 框架和编辑器工具框架。

| 模块 | 用途 |
|---|---|
| `PCG` | 程序化内容生成的核心框架，所有节点、数据和执行逻辑的基础。 |
| `PCGEditor` | PCG 图形编辑器的基础框架，本插件的 `FPVEditor` 继承自 `FPCGEditor`。 |
| `InteractiveToolsFramework` | 编辑器交互工具的框架，用于实现拖拽、点击、Gizmo等操作。 |
| `MeshModelingTools` | 用于动态网格体预览和碰撞体可视化。 |
| `GeometryScriptingCore` | 几何脚本核心库，用于在运行时操作动态网格体（`UDynamicMesh`）。 |
| `NaniteAssembly` | Nanite 组装数据构建，用于生成支持 Nanite 的网格体。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6587e553` | [PVE] Fix for Material look broken in the saved sample content. | 修复了示例内容中材质显示异常的问题。 |
| 2026-05-22 | `ef6788f5` | Fix crash on platforms using HotReload where ProceduralVegetationEditor.plugin attempts to register | 修复了在支持热重载的平台上，插件尝试注册时导致的崩溃。 |
| 2026-05-21 | `5b49f4b9` | [PV] Fixed Incorrect/misleading and missing tooltips for the following nodes | 修正了多个节点的错误、误导性或缺失的工具提示。 |
| 2026-05-21 | `461f91d8` | Re-write PV::Export::Internal::ReplaceAssetInPackage to resolve various crashes in the engine when o | 重写了资产替换逻辑，解决了导出时引擎可能出现的多种崩溃。 |
| 2026-05-20 | `dc74565d` | [PVE] Major fixes | 进行了多项重要修复。 |

### 维护评价

- **活跃维护**：该插件创建于 2025 年 8 月，截至 2026 年 5 月，仍在持续进行**功能性的bug修复和稳定性改进**（如修复材质、崩溃、工具提示等），这表明它仍处于活跃的开发和维护周期。
- **实验性**：插件位于 `Experimental` 目录下，且 `.uplugin` 文件可能标记为实验性，这意味着其API和功能在未来版本中可能会有较大变动。
- **建议**：对于希望使用 Nanite Foliage 工作流程的团队，此插件提供了一个有潜力的内置解决方案。但由于其**实验性状态**，建议在项目关键路径上谨慎使用，并密切关注版本更新日志。适合用于原型开发和内部工具链探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ProceduralVegetationEditor)
- 官方文档：暂无
- 测试用例：插件源码中包含测试场景（`Private/Tests/ScenarioTests/PVTestScenario.h`），可用于验证特定生成流程。