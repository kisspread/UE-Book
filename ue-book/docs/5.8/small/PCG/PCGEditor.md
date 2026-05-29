# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时框架、编辑器工具、计算模块、测试用例） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG插件是一个全面的框架，用于通过可视化的节点图来定义和执行程序化内容生成规则。它解决了在大型开放世界中手动放置和管理海量内容（如植被、岩石、建筑、NPC等）的效率问题。其核心是构建一个数据驱动的图，该图定义了从输入（如地形、边界、其他数据）到输出（如生成的Actor、点云）的转换过程。

插件的主要价值在于：
1.  **可视化脚本**：艺术家和技术美术可以通过拖拽节点而非编写代码来创建复杂的生成规则。
2.  **执行灵活性**：规则可以在编辑器中预览和缓存，也可以在游戏运行时动态生成。
3.  **性能优化**：支持层级化生成（Hierarchical Generation）和GPU计算，能高效处理世界分区（World Partition）中的海量数据。
4.  **强大调试**：提供丰富的工具来检查、调试和性能分析每个生成步骤。

## 使用场景

- 你需要在一个大型开放世界中程序化地散布数百万棵树、石头和草 → 使用PCG图基于地形坡度、海拔、材质等规则来分布点集，然后使用静态网格体生成器节点来放置物体。
- 你需要根据关卡设计动态生成巡逻路径或敌人波次 → 在运行时触发PCG图，输入玩家位置或任务状态，输出路径点或生成器。
- 你希望非程序员也能创建和修改场景布局 → 使用PCG的节点图编辑器，美术可以直观地调整生成规则，如树木的随机缩放范围、密度分布等。
- 你需要对生成结果进行增量式、非破坏性的局部修改 → 使用PCG的Delta系统或交互式工具（如绘制、样条线）来手动调整程序化生成的内容。
- 你需要优化生成过程的性能 → 使用PCG的性能分析工具查看每个节点的执行时间，利用层级化生成减少不必要的计算。

## 蓝图用法

PCG的核心运行时功能（如执行图）主要通过C++暴露。蓝图主要用于在运行时触发图执行、传递数据以及与生成的组件交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Generate` | 触发PCG组件执行其关联的PCG图。 | `UPCGComponent` |
| `Cleanup` | 清理PCG组件生成的所有内容。 | `UPCGComponent` |
| `SetGraph` | 为PCG组件设置新的PCG图资产。 | `UPCGComponent` |
| `AddToGraphParameters` | 向图参数集合中添加一个标量参数（如浮点数、整数）。 | `UPCGGraphInterface` |
| `GetGeneratedActors` | 获取由PCG组件在上一次执行中生成的所有Actor。 | `UPCGComponent` |

### 使用示例（蓝图描述）

1.  **基本生成**：将`PCG Component`添加到一个Actor上。在`Details`面板中指定`Graph`资产。在游戏开始时，调用该组件的`Generate`函数即可执行图并生成内容。
2.  **运行时参数传递**：在蓝图中，先调用`Add To Graph Parameters`节点，传入一个`Graph Parameter Set`和参数名/值。然后将该参数集通过`Execute`节点的输入引脚传入`PCG Component`的生成函数，图中的`Get Parameter`节点即可读取这个动态值。
3.  **动态切换生成规则**：根据游戏事件（如玩家进入新区域），调用`Set Graph`节点为同一个`PCG Component`更换不同的PCG图资产，然后再次调用`Generate`。

## C++ 用法

PCG的C++ API非常丰富，主要面向开发自定义节点、扩展编辑器功能以及深度集成。

### 头文件引入

```cpp
// 引入PCG核心运行时模块
#include "PCGComponent.h"
#include "PCGGraph.h"
#include "PCGSubsystem.h"
#include "PCGData.h"

// 引入自定义节点基类
#include "PCGSettings.h"
#include "PCGNode.h"
```

### 基本用法：创建自定义PCG设置节点

这是一个创建自定义节点的基础模式。所有节点都继承自`UPCGSettings`。

**来源参考**：`Engine/Plugins/PCG/Source/PCG/Public/Nodes/*Settings.h` 中的模式。

```cpp
// MyCustomPCGSettings.h
#pragma once

#include "PCGSettings.h"
#include "MyCustomPCGSettings.generated.h"

UCLASS(BlueprintType, EditInlineNew, Category = "MyPlugin|PCG")
class MYPLUGIN_API UMyCustomPCGSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UMyCustomPCGSettings();

    // 声明输入输出引脚
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;

protected:
    // 实现核心执行逻辑
    virtual FPCGElementPtr CreateElement() const override;

    // 可选：声明可编辑的属性（会显示在节点细节面板）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings, meta = (ClampMin = 0))
    float Density = 1.0f;
};

// MyCustomPCGSettings.cpp
#include "MyCustomPCGSettings.h"
#include "PCGContext.h"

UMyCustomPCGSettings::UMyCustomPCGSettings()
{
    bUseSeed = true; // 启用种子以支持确定性
}

TArray<FPCGPinProperties> UMyCustomPCGSettings::InputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace(PCGPinConstants::DefaultInputLabel, EPCGDataType::Point);
    return PinProperties;
}

TArray<FPCGPinProperties> UMyCustomPCGSettings::OutputPinProperties() const
{
    TArray<FPCGPinProperties> PinProperties;
    PinProperties.Emplace(PCGPinConstants::DefaultOutputLabel, EPCGDataType::Point);
    return PinProperties;
}

// 创建一个代表此设置执行逻辑的元素
FPCGElementPtr UMyCustomPCGSettings::CreateElement() const
{
    // 使用宏简化元素类的创建
    return MakeShared<FPCGDefaultElement>(GetTransientPackage(), FName(TEXT("MyCustomPCGElement")));
}

// 元素的执行逻辑
class FMyCustomPCGElement : public FPCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        // 1. 获取输入数据
        const UPCGData* InputData = Context->InputData.GetParams();
        
        // 2. 创建输出数据
        UPCGPointData* OutputData = NewObject<UPCGPointData>();
        TArray<FPCGPoint>& OutputPoints = OutputData->GetMutablePoints();
        
        // 3. 应用自定义逻辑，例如根据密度过滤点
        if (const UPCGPointData* InputPoints = Cast<UPCGPointData>(InputData))
        {
            const UMyCustomPCGSettings* Settings = Context->GetInputSettings<UMyCustomPCGSettings>();
            const float DensityThreshold = Settings ? Settings->Density : 1.0f;
            
            for (const FPCGPoint& Point : InputPoints->GetPoints())
            {
                if (Point.Density >= DensityThreshold)
                {
                    OutputPoints.Add(Point);
                }
            }
        }
        
        // 4. 输出结果
        Context->OutputData.TaggedData.Emplace_GetRef().Data = OutputData;
        
        return true;
    }
};
```

### 进阶用法：从运行时代码触发PCG图执行

**来源参考**：`Engine/Plugins/PCG/Tests/PCGTest.cpp` 中的测试用例。

```cpp
// 在某个Actor或组件中
void AMyActor::ExecutePCGGraphAtRuntime()
{
    // 获取世界子系统
    UPCGSubsystem* PCGSubsystem = UPCGSubsystem::GetInstance(GetWorld());
    if (!PCGSubsystem)
    {
        return;
    }

    // 构建执行参数
    FPCGExecuteParams ExecuteParams;
    ExecuteParams.SourceComponent = MyPCGComponent; // 可选：关联一个组件
    ExecuteParams.Seed = 12345; // 设置随机种子以确保可复现性

    // 准备图参数
    FPCGGraphParameters GraphParams;
    GraphParams.AddScalarParameter(TEXT("SpawnCount"), 100.0f);
    GraphParams.AddVectorParameter(TEXT("SpawnAreaSize"), FVector(1000.f, 1000.f, 0.f));

    // 如果需要异步执行，可以获取一个Token
    FPCGGraphExecutionToken Token = PCGSubsystem->ScheduleGraph(MyPCGGraph, ExecuteParams, GraphParams);

    // 你可以轮询Token状态或设置完成回调
    Token->OnExecutionCompleted().AddUObject(this, &AMyActor::OnPCGGraphCompleted);
}

void AMyActor::OnPCGGraphCompleted(UPCGSubsystem* Subsystem, const FPCGGraphExecutionToken& Token, EPCGGenerationStatus Status)
{
    if (Status == EPCGGenerationStatus::Completed)
    {
        // 生成完成，可以处理结果数据
        const UPCGData* OutputData = Token->GetOutputData();
        // ...
    }
}
```

## Demo 示例

一个最小化的自定义PCG节点，它接受一组点作为输入，并输出所有位于特定高度以上的点。

### 高于海拔过滤器节点

**HeightFilterSettings.h**
```cpp
#pragma once

#include "PCGSettings.h"
#include "HeightFilterSettings.generated.h"

UCLASS(BlueprintType, EditInlineNew, Category = "Demo|PCG")
class UHeightFilterSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UHeightFilterSettings();

    // 属性面板
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Filter", meta = (ClampMin = "0.0"))
    float MinHeight = 100.0f;

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;
};
```

**HeightFilterSettings.cpp**
```cpp
#include "HeightFilterSettings.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"

UHeightFilterSettings::UHeightFilterSettings()
{
    bUseSeed = false; // 本节点不依赖随机数
}

TArray<FPCGPinProperties> UHeightFilterSettings::InputPinProperties() const
{
    TArray<FPCGPinProperties> Pins;
    Pins.Emplace(PCGPinConstants::DefaultInputLabel, EPCGDataType::Point);
    return Pins;
}

TArray<FPCGPinProperties> UHeightFilterSettings::OutputPinProperties() const
{
    TArray<FPCGPinProperties> Pins;
    Pins.Emplace(PCGPinConstants::DefaultOutputLabel, EPCGDataType::Point);
    return Pins;
}

FPCGElementPtr UHeightFilterSettings::CreateElement() const
{
    return MakeShared<FPCGDefaultElement>(GetTransientPackage(), FName(TEXT("HeightFilterElement")));
}

// 简化的元素执行逻辑
class FHeightFilterElement : public FPCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        const UHeightFilterSettings* Settings = Context->GetInputSettings<UHeightFilterSettings>();
        check(Settings);

        // 获取输入点集
        const UPCGPointData* InputPointData = Context->InputData.GetFirstPointData();
        if (!InputPointData)
        {
            return true; // 没有输入数据，提前退出
        }

        // 创建输出数据
        UPCGPointData* OutputPointData = NewObject<UPCGPointData>();
        TArray<FPCGPoint>& OutputPoints = OutputPointData->GetMutablePoints();

        // 执行过滤
        for (const FPCGPoint& Point : InputPointData->GetPoints())
        {
            if (Point.Transform.GetLocation().Z >= Settings->MinHeight)
            {
                OutputPoints.Add(Point);
            }
        }

        // 输出结果
        Context->OutputData.TaggedData.Emplace_GetRef().Data = OutputPointData;
        return true;
    }
};
```

## 模块依赖

从源码头文件包含关系推断，使用PCG插件或开发自定义节点通常需要以下模块：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心运行时框架，包含数据、执行、图结构等所有基础类。 |
| `PCGEditor` | 编辑器工具，如节点图编辑器、调试工具、资产定义等。仅在编辑器中使用。 |
| `Core` | 基础类型、容器、数学库。 |
| `Engine` | Actor、组件、世界、子系统等引擎核心。 |
| `CoreUObject` | UObject系统、反射、序列化。 |
| `Slate`, `SlateCore`, `UMG` | 用于构建编辑器界面和小部件。 |
| `InputCore` | 处理输入（如用于交互式工具）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复了构建地形缓存时因部分条目无法解析而导致的潜在崩溃。 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化PCG组件可视化器性能。 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复了访问器遇到空对象时的崩溃问题。 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存了元数据大小计算，通过线程局部存储的标志位进行门控，以确保常规使用不受影响。 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspectio | 修复了与手动编辑相关的编辑器更新性能问题（包括双重更新）和检查功能。 |

### 维护评价

PCG插件目前处于**非常活跃**的维护状态。
- **创建时间**：相对较新，于2024年初从实验性状态转为正式插件。
- **更新频率**：从git历史看，在2026年5月26日一天内就有5次提交，集中在性能优化和崩溃修复上，表明开发团队正在积极打磨该功能。
- **功能完整性**：包含运行时、编辑器、计算和测试四个模块，架构完整。
- **推荐使用**：强烈推荐用于任何需要程序化生成大规模内容的项目。它是Epic Games官方支持的核心工具之一，文档和示例正在不断完善。需要注意，由于功能复杂，初始学习曲线可能较陡峭，但其带来的效率和灵活性提升是值得的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Tests)