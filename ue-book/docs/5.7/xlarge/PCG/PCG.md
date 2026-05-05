# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-13 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG) | |

## 用途

PCG (Procedural Content Generation) 插件是一个强大的可视化脚本框架，用于在编辑器中和运行时程序化地生成和填充世界内容。它解决的核心问题是**大规模、可重复、可控的程序化内容生成**。

传统的内容放置（如手动摆放植被、岩石、建筑）耗时且难以维护。PCG 允许设计师和开发者通过**节点图**定义生成规则，这些规则可以：
1.  **在编辑器中预览和迭代**：快速生成和调整场景布局。
2.  **在运行时动态生成**：根据游戏状态、玩家位置等实时生成内容，适用于开放世界、Roguelike 等游戏类型。
3.  **保持一致性**：通过参数化和随机种子，确保生成结果可预测、可复现。
4.  **高效处理海量数据**：内置空间查询、点云处理、实例化渲染等优化，能处理数百万个对象。

其本质是一个**数据流处理引擎**，数据（如点、线、面、属性）在节点间流动，经过过滤、变换、采样等操作，最终输出到场景中。

## 使用场景

-   **开放世界环境填充**：自动在地形上生成草地、树木、岩石、灌木等自然元素。
-   **城市与建筑生成**：程序化生成街道、建筑群、室内布局。
-   **关卡设计辅助**：快速原型化和迭代关卡布局，如地牢、走廊、房间。
-   **运行时内容生成**：根据玩家进度或世界状态动态生成敌人、物品、地形特征。
-   **数据可视化**：将数据（如热力图、点集）转换为可视化的3D场景。
-   **美术资源管理**：批量处理和放置大量静态网格体、骨骼网格体实例。

## 蓝图用法

PCG 的蓝图用法主要通过 `UPCGComponent` 和各种 `UPCGSettings` 子类来实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Generate` | 触发 PCG 图的执行，生成内容。 | `UPCGComponent` |
| `Cleanup` | 清理由该组件生成的所有内容。 | `UPCGComponent` |
| `SetGraph` | 设置要执行的 PCG 图资产。 | `UPCGComponent` |
| `GetPCGSubsystem` | 获取当前世界的 PCG 子系统，用于全局管理。 | `UPCGSubsystem` (静态) |
| `CreatePCGVolume` | 在指定位置创建一个 PCG 体积 Actor。 | `APCGVolume` (静态) |

### 使用示例（蓝图描述）

1.  **基本生成流程**：
    *   在场景中放置一个 `PCG Volume` Actor。
    *   在其 `Details` 面板中，找到 `PCG Component`。
    *   将 `Graph` 属性设置为一个已创建的 `PCG Graph` 资产。
    *   调用 `PCG Component` 的 `Generate` 节点，即可根据图定义生成内容。

2.  **动态控制**：
    *   通过蓝图获取 `PCG Component` 的引用。
    *   使用 `Set Graph` 节点在运行时切换不同的生成规则。
    *   使用 `Generate` 和 `Cleanup` 节点控制生成的时机。

3.  **与子系统交互**：
    *   使用 `Get PCG Subsystem` 节点获取全局管理器。
    *   可以查询所有活动的 PCG 组件，或监听生成事件。

## C++ 用法

PCG 的 C++ 用法主要涉及创建自定义的 PCG 节点（Settings）和操作 PCG 数据。

### 头文件引入

```cpp
#include "PCGComponent.h"
#include "PCGSubsystem.h"
#include "PCGGraph.h"
#include "PCGSettings.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"
```

### 基本用法：创建自定义 PCG 节点

以下是一个简单的自定义 PCG 节点示例，它接收点数据并为每个点添加一个随机颜色属性。
*(来源：基于 `PCGSettings` 和 `PCGElement` 的通用模式)*

**MyPCGNode.h**
```cpp
#pragma once

#include "PCGSettings.h"
#include "MyPCGNode.generated.h"

UCLASS(BlueprintType, ClassGroup = (Procedural))
class UMyPCGNodeSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UMyPCGNodeSettings();

    //~Begin UPCGSettings interface
#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override;
    virtual FText GetDefaultNodeTitle() const override;
    virtual EPCGSettingsType GetType() const override { return EPCGSettingsType::Filter; }
#endif

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;
    //~End UPCGSettings interface

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings)
    FLinearColor BaseColor = FLinearColor::White;
};

class FMyPCGNodeElement : public IPCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override;
};
```

**MyPCGNode.cpp**
```cpp
#include "MyPCGNode.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"
#include "Metadata/PCGMetadata.h"

UMyPCGNodeSettings::UMyPCGNodeSettings()
{
    bExposeToLibrary = true;
}

#if WITH_EDITOR
FName UMyPCGNodeSettings::GetDefaultNodeName() const
{
    return FName(TEXT("MyCustomNode"));
}

FText UMyPCGNodeSettings::GetDefaultNodeTitle() const
{
    return NSLOCTEXT("PCG", "MyCustomNodeTitle", "My Custom Node");
}
#endif

TArray<FPCGPinProperties> UMyPCGNodeSettings::InputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace(PCGPinConstants::DefaultInputLabel, EPCGDataType::Point);
    return PinProperties;
}

TArray<FPCGPinProperties> UMyPCGNodeSettings::OutputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace(PCGPinConstants::DefaultOutputLabel, EPCGDataType::Point);
    return PinProperties;
}

FPCGElementPtr UMyPCGNodeSettings::CreateElement() const
{
    return MakeShared<FMyPCGNodeElement>();
}

bool FMyPCGNodeElement::ExecuteInternal(FPCGContext* Context) const
{
    // 获取输入数据
    const UPCGPointData* InputData = Context->GetInputData<UPCGPointData>(PCGPinConstants::DefaultInputLabel);
    if (!InputData)
    {
        return true; // 无输入，视为完成
    }

    // 创建输出数据（通常复制输入）
    UPCGPointData* OutputData = Context->NewObject_AnyThread<UPCGPointData>();
    OutputData->InitializeFromData(InputData);
    Context->OutputData(PCGPinConstants::DefaultOutputLabel, OutputData);

    // 获取设置
    const UMyPCGNodeSettings* Settings = Context->GetInputSettings<UMyPCGNodeSettings>();
    check(Settings);

    // 获取输出点数组的可写引用
    TArray<FPCGPoint>& OutputPoints = OutputData->GetMutablePoints();

    // 为每个点添加随机颜色属性
    FPCGMetadataAttribute<FLinearColor>* ColorAttribute = OutputData->Metadata->CreateAttribute<FLinearColor>(
        FName("RandomColor"), Settings->BaseColor, /*bAllowsInterpolation=*/true, /*bOverrideParent=*/true);

    for (FPCGPoint& Point : OutputPoints)
    {
        FLinearColor RandomColor = Settings->BaseColor * FMath::FRandRange(0.8f, 1.2f);
        RandomColor.A = 1.0f;
        ColorAttribute->SetValue(Point.MetadataEntry, RandomColor);
    }

    return true; // 执行完成
}
```

### 进阶用法：操作空间数据与属性

*(来源：测试用例 `PCGAttributeExtractorTest` 和通用元素模式)*

```cpp
// 从点数据中提取特定属性
void ExtractAttributesFromPoints(const UPCGPointData* PointData)
{
    if (!PointData || !PointData->Metadata) return;

    // 查找名为“Density”的属性
    const FPCGMetadataAttribute<float>* DensityAttr = PointData->Metadata->GetConstTypedAttribute<float>(FName("Density"));
    if (DensityAttr)
    {
        for (const FPCGPoint& Point : PointData->GetPoints())
        {
            float Density = DensityAttr->GetValueFromItemKey(Point.MetadataEntry);
            // 使用 Density 值...
        }
    }
}

// 使用空间查询（八叉树）查找附近的点
void QueryNearbyPoints(const UPCGPointData* PointData, const FVector& QueryPosition, float Radius)
{
    // 构建八叉树 (通常在节点初始化时完成)
    PCGPointOctree::FPointOctree PointOctree(FBox(ForceInit));
    for (int32 i = 0; i < PointData->GetNumPoints(); ++i)
    {
        const FPCGPoint& Point = PointData->GetPoint(i);
        PointOctree.AddElement(PCGPointOctree::FPointRef(i, FBoxSphereBounds(Point.Transform.GetLocation(), FVector(Radius), Radius)));
    }

    // 执行球形查询
    TArray<PCGPointOctree::FPointRef> Results;
    PointOctree.FindElementsWithBoundsTest(FBoxSphereBounds(QueryPosition, FVector(Radius), Radius), [&Results](const PCGPointOctree::FPointRef& Ref)
    {
        Results.Add(Ref);
    });

    // 处理结果...
}
```

## Demo 示例

一个最小的自定义 PCG 节点，它将所有输入点沿 Z 轴向上移动一个固定距离。

**PCGMovePointsNode.h**
```cpp
#pragma once

#include "PCGSettings.h"
#include "PCGMovePointsNode.generated.h"

UCLASS(BlueprintType, ClassGroup = (Procedural))
class UPCGMovePointsNodeSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPCGMovePointsNodeSettings();

#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override { return FName(TEXT("MovePoints")); }
    virtual FText GetDefaultNodeTitle() const override { return NSLOCTEXT("PCG", "MovePointsTitle", "Move Points"); }
    virtual EPCGSettingsType GetType() const override { return EPCGSettingsType::Transform; }
#endif

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (ClampMin = "0"))
    float MoveDistance = 100.0f;
};

class FPCGMovePointsNodeElement : public IPCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override;
};
```

**PCGMovePointsNode.cpp**
```cpp
#include "PCGMovePointsNode.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"

UPCGMovePointsNodeSettings::UPCGMovePointsNodeSettings()
{
    bExposeToLibrary = true;
}

TArray<FPCGPinProperties> UPCGMovePointsNodeSettings::InputPinProperties() const
{
    return { FPCGPinProperties(PCGPinConstants::DefaultInputLabel, EPCGDataType::Point) };
}

TArray<FPCGPinProperties> UPCGMovePointsNodeSettings::OutputPinProperties() const
{
    return { FPCGPinProperties(PCGPinConstants::DefaultOutputLabel, EPCGDataType::Point) };
}

FPCGElementPtr UPCGMovePointsNodeSettings::CreateElement() const
{
    return MakeShared<FPCGMovePointsNodeElement>();
}

bool FPCGMovePointsNodeElement::ExecuteInternal(FPCGContext* Context) const
{
    const UPCGPointData* InputData = Context->GetInputData<UPCGPointData>(PCGPinConstants::DefaultInputLabel);
    const UPCGMovePointsNodeSettings* Settings = Context->GetInputSettings<UPCGMovePointsNodeSettings>();

    if (!InputData || !Settings)
    {
        return true;
    }

    // 创建输出数据
    UPCGPointData* OutputData = Context->NewObject_AnyThread<UPCGPointData>();
    OutputData->InitializeFromData(InputData);
    Context->OutputData(PCGPinConstants::DefaultOutputLabel, OutputData);

    // 移动点
    TArray<FPCGPoint>& Points = OutputData->GetMutablePoints();
    for (FPCGPoint& Point : Points)
    {
        FVector NewLocation = Point.Transform.GetLocation() + FVector(0, 0, Settings->MoveDistance);
        Point.Transform.SetLocation(NewLocation);
    }

    return true;
}
```

**Build.cs 依赖**
```csharp
using UnrealBuildTool;

public class MyPCGModule : ModuleRules
{
    public MyPCGModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "PCG" // 依赖 PCG 模块
        });
    }
}
```

## 模块依赖

从 `PCG.Build.cs` 分析，使用 PCG 插件时，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 核心运行时模块，包含所有基础数据类型、元素和组件。 |
| `PCGCompute` | PCG 计算模块，用于 GPU 加速的程序化生成。 |
| `PCGEditor` | PCG 编辑器模块，提供节点图编辑器、自定义资产编辑器等。 |

**注意**：如果你的项目只是**使用** PCG 图和组件，通常只需依赖 `PCG` 模块。如果你需要**扩展编辑器**（如创建自定义节点面板），则需要依赖 `PCGEditor`。

## 维护状态

### 近期更新

1.  **`08d19b999cde`** (2024-07-26): `[PCG] Don't fire world generation process delegates in PIE.`
    *   **解读**：修复了在编辑器内运行（PIE）时错误触发世界生成流程委托的问题，提升了编辑器内的稳定性和可预测性。
2.  **`ac5188e4749b`** (2024-07-26): `[PCG] Convert some lazy/paranoid ensures to proper error messages.`
    *   **解读**：将一些防御性编程中的 `ensure` 断言转换为更友好的错误消息，改善了调试体验。
3.  **`ae59b664dd85`** (2024-07-26): `[PCG] Temporary fix for thread-safety of Polygon 2D Accessors`
    *   **解读**：为 2D 多边形访问器提供了线程安全的临时修复，表明团队正在处理并发相关的问题。

### 维护评价

-   **活跃维护**：PCG 是 Epic Games 重点发展的核心系统之一，用于支持《堡垒之夜》等大型项目。从提交记录看，团队在持续修复 bug、优化性能和添加新功能。
-   **创建时间**：2022 年初创建，相对年轻但已非常成熟。
-   **更新频率**：近期（2024年7月）仍有实质性更新，表明处于**活跃维护**状态。
-   **已知限制**：作为一个庞大且复杂的系统，可能存在一些边缘情况的 bug 或性能瓶颈，但官方在积极解决。
-   **推荐使用**：**强烈推荐**。对于任何需要程序化内容生成的 UE5 项目，PCG 都是官方首选且功能最完整的解决方案。它提供了从编辑器工具到运行时生成的全套工作流。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG)
-   [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG/Source/PCG/Tests)