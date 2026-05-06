# Procedural Content Generation Framework (PCG) Water Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Water system.

| 属性 | 值 |
|---|---|
| 中文名 | PCG-水体互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGWaterInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGWaterInterop) | |

---

## 用途

该插件扩展了 **PCG（程序化内容生成框架）**，使其能够读取 **水体系统（Water System）** 中的样条线数据。通过提供一个特殊的 PCG 数据源节点 `Get Water Spline Data`，可以将水体样条（`UWaterSplineComponent`）中的深度、流速、河流宽度、音频强度等元数据转换为 PCG 可以处理的样条线数据（`UPCGWaterSplineData`），并在 PCG 图表中使用这些信息驱动后续的地形生成、植被放置等逻辑。

**为什么存在？**  
水体系统本身提供了丰富的河流、湖泊样条线，但这些数据原本无法直接在 PCG 图表中使用。该插件架起了 PCG 与水体系统之间的桥梁，使得 PCG 可以用水体信息（如深度、流速）来动态调整世界生成效果（例如只在浅水区放置石头、在急流处生成特殊植被等）。

---

## 使用场景

- **程序化河流环境**：基于水体样条的深度和流速，动态调整河床材质、水生植物的分布密度。
- **混合地形生成**：将河流的样条线数据输入 PCG 图表，沿河岸生成特定地貌（如悬崖、沙滩、桥梁等）。
- **动态水位响应**：利用水体元数据中的“深度”控制 PCG 生成元素的高度偏移（例如浮木的位置）。

---

## 蓝图用法

虽然该插件没有暴露直接的 `BlueprintCallable` 函数，但它的核心功能通过 PCG 节点图系统暴露。在 PCG 图表编辑器中，你可以找到名为 **【Get Water Spline Data】** 的节点。

### 核心节点

| 节点 | 说明 | 设置类 |
|---|---|---|
| `Get Water Spline Data` | 从世界中选择的 Actor 收集所有 `UWaterSplineComponent`，并输出为 `UPCGWaterSplineData` 数据流。 | `UPCGGetWaterSplineSettings` |

### 使用示例（蓝图描述）

1. 在关卡中放置一个水体样条 Actor（例如 `APlacedRiver`），确保它包含 `UWaterSplineComponent`。
2. 打开 **PCG 图表编辑器**，右键搜索 `Get Water Spline Data` 节点并放置。
3. 在节点的细节面板中，设置 **Actor Selection** 为“指定 Actor”并选择之前放置的水体 Actor，或者设置为“从世界标签”自动捕获。
4. 将该节点的输出连接到后面的 PCG 处理节点（如 `PCGSurfaceSampler`、`PCGDensityFilter` 等）。
5. 在后续节点中，你可以通过 **Attribute** 访问水体样条点的元数据：
   - `Depth`：水深
   - `WaterVelocityScalar`：水流速度标量
   - `RiverWidth`：河宽（仅河流）
   - `AudioIntensity`：音频强度

> 注意：该节点本质上是一个“数据获取”节点，输出的是沿样条线的点数据，后续可使用 `PCGSampleSpline` 或 `PCGTransformPoints` 等节点进行进一步处理。

---

## C++ 用法

### 头文件引入

```cpp
#include "Data/PCGWaterSplineData.h"
#include "Elements/PCGGetWaterSpline.h"
```

### 基本用法

以下示例展示了如何在 C++ 中手动创建 `UPCGWaterSplineData` 并将其用于 PCG 上下文中。

```cpp
// 来源: Source/PCGWaterInterop/Public/Data/PCGWaterSplineData.h

// 获取一个水体样条组件
UWaterSplineComponent* WaterSpline = /* ... */;

// 创建 PCGWaterSplineData 并初始化
UPCGWaterSplineData* WaterData = NewObject<UPCGWaterSplineData>();
WaterData->Initialize(WaterSpline);

// 现在 WaterData 包含了该样条的所有点及其水体元数据
// 可以传递给其他 PCG 操作使用
```

### 进阶用法

通过 `UPCGGetWaterSplineSettings` 的派生类实现自定义采集逻辑。该节点是 `FPCGDataFromActorElement` 的变体，其核心处理函数 `ProcessActor` 可被重写以支持更复杂的选择机制（例如按标签、距离等）。

```cpp
// 来源: Source/PCGWaterInterop/Public/Elements/PCGGetWaterSpline.h

// 模拟 PCG 图表中“Get Water Spline Data”节点的执行过程
class FPCGGetWaterSplineElement : public FPCGDataFromActorElement
{
protected:
    virtual void ProcessActor(FPCGContext* Context, 
                               const UPCGDataFromActorSettings* Settings, 
                               AActor* FoundActor) const override
    {
        // 在 FoundActor 上查找 UWaterSplineComponent
        // 提取数据并生成 UPCGWaterSplineData
        // 此函数由框架自动调用，开发者通常无需直接实现
    }
};
```

---

## Demo 示例

### WaterInteropDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WaterInteropDemo.generated.h"

class UWaterSplineComponent;
class UPCGComponent;

UCLASS()
class AWaterInteropDemo : public AActor
{
    GENERATED_BODY()

public:
    AWaterInteropDemo();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "PCG")
    UPCGComponent* PCGComponent;

    UFUNCTION(BlueprintCallable, Category = "PCG")
    void RunPCGWithWaterSpline();
};
```

### WaterInteropDemo.cpp

```cpp
#include "WaterInteropDemo.h"
#include "Data/PCGWaterSplineData.h"
#include "Components/SplineComponent.h"
#include "WaterSplineComponent.h"
#include "PCGComponent.h"
#include "PCGContext.h"
#include "Elements/PCGExecuteBlueprintElement.h"

AWaterInteropDemo::AWaterInteropDemo()
{
    PCGComponent = CreateDefaultSubobject<UPCGComponent>(TEXT("PCGComponent"));
}

void AWaterInteropDemo::RunPCGWithWaterSpline()
{
    // 获取场景中第一个水体样条组件（示例）
    UWaterSplineComponent* WaterSpline = nullptr;
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        AActor* Actor = *It;
        WaterSpline = Actor->FindComponentByClass<UWaterSplineComponent>();
        if (WaterSpline) break;
    }

    if (!WaterSpline) return;

    // 创建 PCG 数据
    UPCGWaterSplineData* WaterData = NewObject<UPCGWaterSplineData>(this);
    WaterData->Initialize(WaterSpline);

    // 将数据注入 PCG 组件
    TArray<UPCGData*> InputData;
    InputData.Add(WaterData);
    PCGComponent->SetGraphInputs(InputData);

    // 执行 PCG 图表（需要提前设置好图表资产）
    PCGComponent->Generate();
}
```

> 注意：实际使用时建议将 PCG 图表资产与逻辑分离，此处仅为展示数据初始化步骤。

---

## 模块依赖

使用该插件时，你的模块需要添加以下依赖项（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心 PCG 框架 |
| `Water` | 水体系统，提供 `UWaterSplineComponent` |

```cpp
// 你的模块 Build.cs 中添加
PublicDependencyModuleNames.AddRange(new string[] { "PCG", "Water" });
```

---

## 维护状态

### 近期更新

- 2025-01-29 `f7cc83da` — [PCG] Add support for Spline Metadata on Control points  
  （重要更新：为样条控制点添加了元数据支持，可能影响该插件的数据读取逻辑）
- 2024-08-13 `ab69dd9d` — [PCG] Move all interops into a dedicated folder for tidiness purposes.  
  （初始创建：将所有互操作插件迁移到专用文件夹，此插件首次出现）

### 维护评价

该插件创建于 2024 年 8 月，属于较新的实验性插件。虽然公开的更新较少，但最近一次提交（2025 年 1 月）对 PCG 样条元数据支持进行了改进，表明其仍在积极开发中。作为实验性插件，API 可能不稳定，且尚未大规模使用。推荐在需要 PCG 与水体系统深度集成的项目中尝试使用，但需留意未来可能的重大变更。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGWaterInterop)
- [官方文档 - PCG 框架](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGWaterInterop/Tests) *(目前缺少公开测试)*