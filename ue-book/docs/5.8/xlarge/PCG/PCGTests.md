# PCG

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG 插件提供了一个完整的程序化内容生成框架，其核心是通过节点图（Graph）定义数据处理和变换流程。它主要用于在编辑器中或运行时，自动化、程序化地创建和填充游戏世界中的几何体、植被、建筑等内容。它通过将复杂的世界生成逻辑封装为可复用、可组合的节点（Settings & Elements），解决了大规模手动摆放内容效率低下、难以维护的问题，特别适用于开放世界、城市生成等需要大量程序化内容的项目。

## 使用场景

-   你需要为一个大型开放世界地形自动生成和分布树木、岩石、草地等植被。
-   你需要根据规则在地面上生成道路、建筑网格和城市设施。
-   你需要创建程序化地牢或室内场景布局。
-   你需要基于玩家行为或游戏状态动态改变场景中的物体分布。

## 蓝图用法

PCG 的蓝图用法主要集中在编辑器中的可视化节点图编辑，但运行时也可以通过蓝图接口控制图表执行。核心操作围绕数据（`UPCGData`）的创建、处理和输出。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Graph` | 在运行时执行指定的 PCG 图表资产。 | `UPCGSubsystem` |
| `Get PCG Data from Pin` | 从 PCG 执行上下文中获取特定输出引脚的数据。 | `FPCGContext` |
| `Create Empty Point Data` | 创建一个空的 PCG 点数据容器。 | `FPCGContext` |
| `Set Points` | 为点数据容器设置一组点（包含位置、旋转、缩放等）。 | `UPCGBasePointData` |
| `Add Attribute` | 为点数据添加一个新的自定义属性（元数据）。 | `UPCGMetadata` |

### 使用示例（蓝图描述）

假设你有一个已配置好的 `PCGGraph` 资产，可以在蓝图中这样使用：
1.  调用 `Get Subsystem` 节点获取 `UPCGSubsystem`。
2.  使用 `Execute Graph` 节点，输入你的 `PCGGraph` 资产引用和一个执行上下文（可以来自场景中的 PCG 组件）。
3.  从 `Execute Graph` 的 `Output Pins` 中，可以按名称查找并获取特定数据（如生成的点集）。

## C++ 用法

在 C++ 中，PCG 框架的核心是操作 `UPCGData` 及其子类（如 `UPCGSpatialData`, `UPCGBasePointData`），并通过继承 `UPCGSettings` 来创建自定义节点。

### 头文件引入

```cpp
#include "PCGComponent.h"
#include "PCGGraph.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"
#include "Metadata/PCGMetadata.h"
```

### 基本用法

创建一个简单的点数据集合并添加一个浮点属性。
*（来源：基于测试用例 `PCGMetadataAttributeTestsCommonHelper` 和通用 PCG 数据操作逻辑推导）*

```cpp
// 在某个上下文（如 FPCGContext）中创建一个点数据对象
UPCGPointData* PointData = NewObject<UPCGPointData>();

// 准备一些点
TArray<FPCGPoint>& Points = PointData->GetMutablePoints();
Points.Emplace(FTransform(FVector(100, 200, 0)), 1.0f /*Density*/, 42 /*Seed*/);
Points.Emplace(FTransform(FVector(300, 400, 0)), 0.5f, 43);

// 获取点数据的元数据容器
UPCGMetadata* Metadata = PointData->Metadata;

// 创建一个名为 “Health” 的浮点属性，默认值为 100.0
FPCGMetadataAttribute<float>* HealthAttr = Metadata->CreateAttribute<float>(
    FName("Health"), 
    100.0f /*DefaultValue*/, 
    EPCGMetadataTypes::Float /*AttributeType*/, 
    /*bAllowsInterpolation=*/ true
);

// 为第一个点设置 Health 值
FPCGPoint& FirstPoint = Points[0];
int32 FirstPointEntryKey = FirstPoint.MetadataEntry;
if (FirstPointEntryKey != -1)
{
    HealthAttr->SetValue(FirstPointEntryKey, 75.5f);
}
```

### 进阶用法

在自定义的 PCG Settings 元素中，处理输入数据并生成输出。
*（来源：基于 `FPCGSingleElementBaseTest` 测试框架的典型执行模式推导）*

```cpp
// 自定义一个 Settings 类
UCLASS()
class UMyPCGSettings : public UPCGSettings
{
    GENERATED_BODY()
public:
    // 实现必要的接口
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
protected:
    virtual FPCGElementPtr CreateElement() const override;
};

// 对应的 Element 实现
class FMyPCGElement : public IPCGElement
{
public:
    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        // 1. 获取输入数据
        const UPCGPointData* InputPoints = Context->GetInput<UPCGPointData>(TEXT("Input"));

        // 2. 准备输出数据
        UPCGPointData* OutputPoints = NewObject<UPCGPointData>();
        Context->Output(OUT_Points, OutputPoints);

        if (InputPoints)
        {
            // 3. 处理逻辑：例如，复制所有点，但偏移位置
            const TArray<FPCGPoint>& InPoints = InputPoints->GetConstPoints();
            TArray<FPCGPoint>& OutPoints = OutputPoints->GetMutablePoints();
            for (const FPCGPoint& P : InPoints)
            {
                FPCGPoint NewPoint = P;
                NewPoint.Transform.AddToTranslation(FVector(100.0f, 0.f, 0.f));
                OutPoints.Add(NewPoint);
            }
        }

        // 4. 返回 true 表示执行完成
        return true;
    }
};
```

## Demo 示例

一个最小的自定义 PCG 节点，将所有输入点的 Z 坐标提升一个固定值。

**MyRaiseZSettings.h**
```cpp
#pragma once
#include "PCGSettings.h"
#include "MyRaiseZSettings.generated.h"

UCLASS()
class UMyRaiseZSettings : public UPCGSettings
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    float RaiseAmount = 100.0f;

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;
};
```

**MyRaiseZSettings.cpp**
```cpp
#include "MyRaiseZSettings.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"

TArray<FPCGPinProperties> UMyRaiseZSettings::InputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace_GetRef(NAME_Default, EPCGDataType::Point).SetRequired();
    return PinProperties;
}

TArray<FPCGPinProperties> UMyRaiseZSettings::OutputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace_GetRef(NAME_Default, EPCGDataType::Point);
    return PinProperties;
}

FPCGElementPtr UMyRaiseZSettings::CreateElement() const
{
    return MakeShared<FMyRaiseZElement>();
}

class FMyRaiseZElement : public IPCGElement
{
public:
    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        const UMyRaiseZSettings* Settings = Context->GetInputSettings<UMyRaiseZSettings>();
        check(Settings);

        const UPCGPointData* InputData = Context->GetInput<UPCGPointData>(NAME_Default);
        UPCGPointData* OutputData = NewObject<UPCGPointData>();
        Context->Output(NAME_Default, OutputData);

        if (InputData)
        {
            const TArray<FPCGPoint>& InputPoints = InputData->GetConstPoints();
            TArray<FPCGPoint>& OutputPoints = OutputData->GetMutablePoints();
            OutputPoints.Reserve(InputPoints.Num());

            const FVector RaiseVec(0.0f, 0.0f, Settings->RaiseAmount);
            for (const FPCGPoint& Point : InputPoints)
            {
                FPCGPoint NewPoint = Point;
                NewPoint.Transform.AddToTranslation(RaiseVec);
                OutputPoints.Add(MoveTemp(NewPoint));
            }
        }
        return true;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 核心运行时框架 |
| `PCGCompute` | PCG 的计算后端，可能用于 GPU 或并行计算 |
| `PCGEditor` | PCG 的编辑器集成（节点图编辑器等） |
| `PCGTests` | PCG 模块的自动化测试 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复了构建地形缓存时，某些条目无法解析可能导致的崩溃。 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化了 PCG 组件的可视化器性能。 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复了在访问器中使用空对象时发生的崩溃。 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存了元数据大小计算，通过标志和 TLS 支持进行门控。 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspectio | 修复了与手动编辑相关的编辑器更新性能问题（包括双重更新和检查）。 |

### 维护评价

PCG 插件在 **2026 年 5 月仍有高频、实质性的功能更新和 Bug 修复**，表明该框架正处于**活跃开发与维护**状态。从 2024 年初正式移出实验性至今约 2 年，已成为 UE5 中程序化内容生成的核心官方解决方案。近期提交集中在**性能优化、稳定性修复和编辑器体验改进**，说明 Epic 对其的持续投入。推荐在任何需要程序化生成内容的 UE5 项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Tests)