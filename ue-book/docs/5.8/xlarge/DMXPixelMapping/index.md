# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 中文名 | DMX 像素映射 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 是 UE5 虚拟制作灯光工具链中的核心组件。它解决的核心问题是：如何将 DMX 协议控制的灯光数据，灵活、高效地映射到各种形状和大小的 LED 像素条、LED 灯具阵列或任何由多个独立像素组成的数字灯光设备上。

简单来说，它是一个**视觉化的像素地址分配和渲染系统**。设计师可以在编辑器中通过直观的拖拽操作，将虚拟的灯光矩阵（例如 10x10 的网格）与真实的物理 LED 设备（可能是弯曲的灯带、圆环或不规则形状）进行一一对应，并将 DMX 通道数据转换为每个像素点的颜色和亮度，最终驱动这些设备。

## 使用场景

*   你在搭建一个虚拟舞台，需要控制一个由数百个 LED 模块组成的背景墙，使其播放动态视频效果。
*   你正在为建筑外观设计动态灯光秀，需要将复杂的灯光图案精确地映射到建筑立面的多个不规则排列的发光单元上。
*   你需要创建一个交互式艺术装置，其中的灯光由 DMX 控制，并需要精确控制每个像素。
*   你正在为现实世界中的灯光秀进行预览和编程，需要在 Unreal Engine 中精确模拟最终效果。

## 蓝图用法

该插件的核心功能通过 `UDMXPixelMapping` 和相关组件暴露给蓝图，用于运行时创建和控制像素映射。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create DMXPixel Mapping` | 创建一个新的 DMX 像素映射资产实例。 | `UDMXPixelMappingLibrary` |
| `Apply DMXPixel Mapping` | 将配置好的像素映射应用到场景中的组件上。 | `UDMXPixelMappingLibrary` |
| `Add DMXPixel Mapping Fixture Group` | 添加一个灯具组，用于组织多个像素组件。 | `UDMXPixelMapping` |
| `Add DMXPixel Mapping Fixture` | 向灯具组中添加一个具体的灯具（像素组件）。 | `UDMXPixelMappingFixtureGroup` |
| `Set Size` | 设置像素映射矩阵的行数和列数。 | `UDMXPixelMapping` |
| `Render DMXPixel Mapping` | 将当前的 DMX 通道数据渲染（输出）到映射的像素组件上。 | `UDMXPixelMappingLibrary` |
| `Get All Fixture Groups` | 获取该像素映射下所有的灯具组。 | `UDMXPixelMapping` |
| `Get Fixture` | 根据地址获取特定的灯具组件。 | `UDMXPixelMappingFixtureGroup` |

### 使用示例（蓝图描述）

1.  **初始化**：在 BeginPlay 中，调用 `Create DMXPixel Mapping` 节点生成一个映射对象。使用 `Set Size` 节点设定你的灯光矩阵尺寸（如 10x10）。
2.  **配置映射**：使用循环节点配合 `Add DMXPixel Mapping Fixture Group` 和 `Add DMXPixel Mapping Fixture` 节点，为矩阵中的每个虚拟位置分配一个真实的物理灯具组件引用。
3.  **绑定数据**：将你的 DMX 输入组件（如来自物理 Art-Net 节点）的输出数据连接到 `Render DMXPixel Mapping` 节点的输入。
4.  **应用与渲染**：调用 `Apply DMXPixel Mapping` 将配置应用到目标 Actor，然后每帧或按需调用 `Render DMXPixel Mapping` 来更新灯光显示。

## C++ 用法

在 C++ 中，主要通过 `DMXPixelMappingRuntime` 和 `DMXPixelMappingCore` 模块来操作像素映射。

### 头文件引入

```cpp
#include "DMXPixelMapping.h"
#include "DMXPixelMappingComponent.h"
#include "DMXPixelMappingFixtureGroup.h"
#include "DMXPixelMappingFixture.h"
#include "DMXPixelMappingUtils.h"
```

### 基本用法

以下代码展示了如何以编程方式创建并配置一个简单的像素映射。
*来源：Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingRuntime/Tests/DMXPixelMappingTest.cpp*

```cpp
// 创建一个像素映射对象
UDMXPixelMapping* PixelMapping = NewObject<UDMXPixelMapping>();

// 设置基础尺寸
const int32 NumRows = 4;
const int32 NumColumns = 8;
PixelMapping->SetSize(NumRows, NumColumns);

// 添加一个灯具组
UDMXPixelMappingFixtureGroup* FixtureGroup = PixelMapping->AddFixtureGroup(FName(TEXT("MainGroup")));

// 为矩阵的第一个位置（0，0）添加一个具体的灯具组件
// 假设 MyDMXFixtureComponent 是一个已经存在并配置好的 UDMXFixtureComponent
UDMXPixelMappingFixture* Fixture = FixtureGroup->AddFixture(MyDMXFixtureComponent);
Fixture->SetCellCoordinate(FIntPoint(0, 0));
```

### 进阶用法

结合渲染和更新，在 `Tick` 中将接收到的 DMX 通道数据应用到映射上。
*来源：综合多个测试用例*

```cpp
// 假设已拥有 PixelMapping 对象和 DMX 输入组件 InputComponent

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 从输入组件获取最新的 DMX 数据 (TMap<FDMXAttributeName, float>)
    const TMap<FDMXAttributeName, float>& ChannelData = InputComponent->GetChannelData();

    // 使用工具函数将通道数据渲染到像素映射中的各个 Fixture
    FDMXPixelMappingUtils::Render(PixelMapping, ChannelData);
}
```

## Demo 示例

以下是一个最小的 C++ Actor 示例，演示了如何在场景中设置并驱动一个 2x2 的像素映射。

```cpp
// DMXPixelMappingDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXPixelMapping.h"
#include "DMXPixelMappingDemoActor.generated.h"

class UDMXFixtureComponent;
class UDMXPixelMappingFixtureComponent;

UCLASS()
class ADMXPixelMappingDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ADMXPixelMappingDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMX")
    UDMXPixelMapping* PixelMapping;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMX")
    UDMXPixelMappingFixtureComponent* FixtureComponent00;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMX")
    UDMXPixelMappingFixtureComponent* FixtureComponent01;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMX")
    UDMXPixelMappingFixtureComponent* FixtureComponent10;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMX")
    UDMXPixelMappingFixtureComponent* FixtureComponent11;
};
```

```cpp
// DMXPixelMappingDemoActor.cpp
#include "DMXPixelMappingDemoActor.h"
#include "DMXPixelMappingFixtureGroup.h"
#include "DMXPixelMappingFixture.h"
#include "DMXPixelMappingUtils.h"
#include "Components/DMXFixtureComponent.h"

ADMXPixelMappingDemoActor::ADMXPixelMappingDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ADMXPixelMappingDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建并设置像素映射 (2行 x 2列)
    PixelMapping = NewObject<UDMXPixelMapping>();
    PixelMapping->SetSize(2, 2);

    // 2. 创建一个灯具组
    UDMXPixelMappingFixtureGroup* Group = PixelMapping->AddFixtureGroup(FName(TEXT("DemoGroup")));

    // 3. 创建并绑定四个 Fixture 组件
    FixtureComponent00 = NewObject<UDMXPixelMappingFixtureComponent>(this);
    FixtureComponent01 = NewObject<UDMXPixelMappingFixtureComponent>(this);
    FixtureComponent10 = NewObject<UDMXPixelMappingFixtureComponent>(this);
    FixtureComponent11 = NewObject<UDMXPixelMappingFixtureComponent>(this);

    // 假设每个 FixtureComponent 都已配置好对应的物理组件和起始通道
    // UDMXFixtureComponent* PhysComp00 = ...; FixtureComponent00->SetFixtureComponent(PhysComp00);

    // 4. 将 Fixture 组件分配到矩阵的特定坐标
    UDMXPixelMappingFixture* PF00 = Group->AddFixture(FixtureComponent00);
    PF00->SetCellCoordinate(FIntPoint(0, 0));

    UDMXPixelMappingFixture* PF01 = Group->AddFixture(FixtureComponent01);
    PF01->SetCellCoordinate(FIntPoint(0, 1));

    UDMXPixelMappingFixture* PF10 = Group->AddFixture(FixtureComponent10);
    PF10->SetCellCoordinate(FIntPoint(1, 0));

    UDMXPixelMappingFixture* PF11 = Group->AddFixture(FixtureComponent11);
    PF11->SetCellCoordinate(FIntPoint(1, 1));

    // 在实际应用中，你需要从外部（如 Art-Net 接收器）获取 DMX 数据
}

void ADMXPixelMappingDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 模拟 DMX 数据：全红色
    TMap<FDMXAttributeName, float> SimulatedData;
    SimulatedData.Add(FDMXAttributeName::Red, 1.0f);

    // 将数据渲染到像素映射中
    FDMXPixelMappingUtils::Render(PixelMapping, SimulatedData);
}
```

## 模块依赖

要在你的模块中使用 `DMXPixelMappingRuntime`，需要在 `.Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingRuntime` | 提供像素映射的核心运行时逻辑和组件。 |
| `DMXPixelMappingCore` | 提供基础数据类型和接口。 |
| `DMXProtocol` | DMX 协议通信底层支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5f2a2a90` | DMX - Fix a crash when pixel mapping has unpatched components and draws patch colors | 修复了当像素映射存在未连接的组件且绘制补丁颜色时导致的崩溃。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 视图口：重构客户端关联逻辑，通过通知来解耦重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的一次提交。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | （同上，是修复前的提交，随后被部分回滚）。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数会产生警告的代码。 |

### 维护评价

DMXPixelMapping 是 **活跃维护** 的插件。它于 2021 年 UE5 早期版本引入，是 Epic Games 官方虚拟制作工具链的重要组成部分。从近期（2026年5月）的 Git 提交历史来看，该插件仍在持续接收功能优化和关键的 Bug 修复（例如修复崩溃、重构代码以消除警告）。这表明它仍然是 Epic 重点支持的模块，状态稳定，适合用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingRuntime/Tests)