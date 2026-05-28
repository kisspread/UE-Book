# Procedural Content Generation Framework (PCG) Water Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Water system.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG水体交互 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PCGWaterInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGWaterInterop) | |

## 用途

该插件是 PCG 框架与 Water 插件之间的桥梁。它扩展了 PCG 的功能，使其能够**读取和处理来自 `UWaterSplineComponent` 的数据**，并将这些水体样条线的特性（如深度、宽度、水流速度、音频强度）作为元数据注入到 PCG 点中。

核心价值在于：当你的程序化内容生成流程需要依赖世界中的水体形状时（例如，在河流沿岸生成植被、在水面放置漂浮物、或让生成的道路避开水域），该插件提供了标准的数据转换通道。它解决了 PCG 无法直接理解和使用 Water 系统特有数据的难题。

## 使用场景

- **开放世界地形生成**：你正在使用 PCG 来程序化生成一片大陆，并且使用了 Water 插件来创建河流。现在，你需要沿河流两岸自动生成不同的植物群落。你需要用到这个插件来获取河流样条线，并根据 `Depth` 或 `RiverWidth` 属性来放置不同的植被。
- **动态障碍物放置**：你需要在 PCG 生成的场景中放置一些动态物体（如浮标、小船），这些物体的位置和属性需要基于水流的方向 (`WaterVelocityScalar`) 和宽度 (`RiverWidth`) 来计算。
- **音景程序化生成**：你希望根据水体的 `AudioIntensity` 属性，在 PCG 生成的区域中动态放置环境音效源。

## 蓝图用法

该插件主要通过 PCG 图表 (PCG Graph) 的节点来使用，而非传统的蓝图函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Water Spline Data` | 从场景中的 Actor 上提取 `UWaterSplineComponent`，并将其转换为 PCG 可用的 `UPCGWaterSplineData`。 | `UPCGGetWaterSplineSettings` |

### 使用示例（蓝图描述）

1.  **在 PCG 图表中**：从节点面板搜索并添加 **“Get Water Spline Data”** 节点。
2.  **配置输入**：在该节点的细节面板中，指定要从中获取水体样条线的 **Actor**。通常你会将一个包含 `UWaterSplineComponent` 的 Actor 拖入图表，并连接到此节点的 `Actor` 输入引脚。
3.  **连接输出**：将 “Get Water Spline Data” 节点的输出（一条 `Spline` 数据）连接到下游的节点，例如 “Sample Spline Points” 或 “Transform Points” 节点。
4.  **使用元数据**：在下游节点中处理 `FPCGPoint` 时，你可以访问写入点的元数据字段（如 `WaterDepth`, `WaterRiverWidth` 等），这些字段值来源于原始水体样条线顶点数据。

## C++ 用法

该插件的核心在于提供 PCG 数据类型与 Water 系统数据的转换。以下示例展示了如何以编程方式使用其核心数据类。

### 头文件引入

```cpp
#include "Data/PCGWaterSplineData.h"
#include "Elements/PCGGetWaterSpline.h"
```

### 基本用法：解析水体样条线数据

这个示例展示了如何从一个 `UWaterSplineComponent` 初始化一个 `UPCGWaterSplineData` 对象，从而在 C++ 的 PCG 流程中使用它。

```cpp
// 来源：基于 PCGWaterSplineData.h 的 `Initialize` 方法设计
// 假设你已经获取到了一个指向 UWaterSplineComponent 的指针
UWaterSplineComponent* WaterSplineComp = GetWaterSplineComponentFromSomeActor();

if (WaterSplineComp)
{
    // 1. 创建 PCG 水体样条线数据对象
    UPCGWaterSplineData* PCGWaterSpline = NewObject<UPCGWaterSplineData>();

    // 2. 使用 WaterSplineComponent 对其进行初始化
    //    此步骤会将 WaterSplineComp 上的元数据（深度、宽度等）复制到内部结构体中
    PCGWaterSpline->Initialize(WaterSplineComp);

    // 3. 现在，PCGWaterSpline 可以作为一个标准的 UPCGSplineData 使用
    //    例如，将其传递给 PCG 图表执行器，或在其上调用 SamplePoint 方法
    //    SamplePoint 内部会将 WaterSplineMetadataStruct 中的信息写入 FPCGPoint 的元数据。
}
```

### 进阶用法：自定义 PCG 元素处理水体数据

你可以基于 `FPCGGetWaterSplineElement` 创建自定义的 PCG 元素，以扩展或修改获取水体数据的行为。

```cpp
// 来源：基于 PCGGetWaterSpline.h 的 ProcessActor 方法设计
class FMyCustomWaterSplineElement : public FPCGGetWaterSplineElement
{
protected:
    // 重写 ProcessActor 以添加自定义逻辑
    virtual void ProcessActor(FPCGContext* Context, const UPCGDataFromActorSettings* Settings, AActor* FoundActor) const override
    {
        // 调用父类的实现来完成标准的水体样条线提取
        FPCGGetWaterSplineElement::ProcessActor(Context, Settings, FoundActor);

        // 在这里添加自定义后处理逻辑
        // 例如，过滤掉某些点，或者根据额外的 Actor 标签修改点数据
        if (FoundActor && FoundActor->ActorHasTag(FName(TEXT("DeepRiver"))))
        {
            // 修改或处理刚刚为这个 Actor 生成的 PCGData...
        }
    }
};

// 然后，你需要一个对应的 Settings 类来使用这个自定义元素
UCLASS()
class UMyCustomWaterSplineSettings : public UPCGGetWaterSplineSettings
{
    GENERATED_BODY()

protected:
    virtual FPCGElementPtr CreateElement() const override
    {
        return MakeShared<FMyCustomWaterSplineElement>();
    }
};
```

## Demo 示例

一个最小的示例，展示如何创建一个能生成水体样条线数据的 PCG 图表设置。

**头文件 (`DemoWaterSplineSettings.h`)**:

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Elements/PCGGetWaterSpline.h"
#include "DemoWaterSplineSettings.generated.h"

/**
 * 示例：一个获取水体样条线数据的 PCG 节点设置
 * 这个类可以被放置在 PCG 图表中。
 */
UCLASS(BlueprintType, ClassGroup = (Procedural))
class UDemoWaterSplineSettings : public UPCGGetWaterSplineSettings
{
	GENERATED_BODY()

public:
	UDemoWaterSplineSettings();

#if WITH_EDITOR
	virtual FName GetDefaultNodeName() const override { return FName(TEXT("DemoWaterSpline")); }
	virtual FText GetDefaultNodeTitle() const override { return NSLOCTEXT("DemoWaterSpline", "NodeTitle", "Demo: Get Water Spline"); }
#endif
};
```

**源文件 (`DemoWaterSplineSettings.cpp`)**:

```cpp
#include "DemoWaterSplineSettings.h"
#include "PCGWaterSplineData.h" // 为了完整性引入

UDemoWaterSplineSettings::UDemoWaterSplineSettings()
{
	// 可以在此设置默认的 Actor 过滤器或其他属性
	bSearchForActorTag = false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | 核心 PCG 框架，提供基础数据类型和图表执行机制。 |
| `Water` | 水体插件，提供 `UWaterSplineComponent` 和 `WaterSplineMetadata` 等类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-01-29 | `f7cc83da` | [PCG] Add support for Spline Metadata on Control points | 为控制点添加样条线元数据支持 |
| 2024-08-13 | `ab69dd9d` | [PCG] Move all interops into a dedicated folder for tidiness purposes. | 将所有交互插件移入专用文件夹以保持整洁 |

### 维护评价

该插件**创建时间非常近（2024年8月）**，并且**在 2025 年 1 月有最新的功能性更新**，增加了对样条线控制点元数据的支持。这表明它仍处于**活跃的早期开发或完善阶段**。

由于标记为 `IsExperimentalVersion: true` 且默认不启用，表明 Epic Games 将其视为实验性功能，其 API 和稳定性在未来版本中可能会发生变化。

**结论**：对于需要在 PCG 中精确利用 Water 系统数据的项目，这是一个关键且正在积极维护的工具插件。推荐在实验性或原型项目中使用，但在用于最终产品时需要关注其后续版本的更新日志，以应对潜在的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGWaterInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGWaterInterop/Tests) *(通常位于此路径，但未在提供的信息中列出)*