# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX像素映射 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、内容资产） |
| 模块 | `DMXPixelMappingCore` (Runtime), `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 插件提供了一套完整的工具集，用于将虚拟场景中的像素网格（如 LED 屏幕、像素条）映射到真实的 DMX 灯具或设备上。它解决了在虚拟制作（Virtual Production）环境中，如何精确控制由大量 DMX 灯具组成的、形状和大小各异的像素阵列，使其能实时显示场景中的图像、材质或渲染纹理的核心问题。它是 UE5 内置 DMX 协议栈的重要组成部分，主要服务于 LED 墙（Volume）控制、舞台灯光秀、建筑立面灯光设计等需要复杂像素映射的场景。

## 使用场景

- **虚拟制片（LED Volume）**：你正在用一块由大量 LED 面板组成的墙（Volume）作为拍摄背景，需要将 UE5 中渲染的画面实时、准确地映射到每一块 LED 面板上 → 使用本插件定义面板的物理布局和像素分布，实现精确的同步映射。
- **舞台灯光设计**：你设计了一个由数百个独立 LED 灯具组成的矩阵或不规则阵列，希望将其控制集成到 UE5 中进行预览和编程 → 使用本插件创建自定义的像素映射布局，驱动这些灯具。
- **动态灯光艺术装置**：你创建了一个互动艺术装置，由许多 DMX 控制的灯点组成，需要实时响应游戏逻辑或用户输入来改变颜色和图案 → 使用本插件管理和发送复杂的 DMX 数据到这些灯点。

## 蓝图用法

根据提供的源码分析，`DMXPixelMappingCore` 模块主要提供底层的工具类和类型定义，直接的蓝图节点暴露较少。蓝图集成更多依赖于 `DMXPixelMappingRuntime` 和 `DMXPixelMappingRenderer` 模块。

### 核心节点（基于类型定义）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EDMXPixelMappingRendererType` | 枚举，指定像素映射的输入源类型（纹理、材质、UMG） | `DMXPixelMappingTypes.h` |
| `EDMXCellFormat` | 枚举，定义 DMX 像素的颜色通道顺序（如 R, RGB, RGBA, GRB 等） | `DMXPixelMappingTypes.h` |
| `EDMXColorMode` | 枚举，定义颜色模式（RGB 或单色） | `DMXPixelMappingTypes.h` |

### 使用示例（蓝图描述）

在蓝图中，你通常会创建或修改一个 `UDMXPixelMappingBaseComponent`（或其子类，如 `UDMXPixelMappingRendererComponent`）。在组件的详细信息面板中，你会设置以下关键属性：
1. **Renderer Type**：选择你的像素输入是来自一个 `Texture`，一个 `Material`，还是一个 `UMG Widget`。
2. **Cell Format**：根据你的 DMX 灯具规格，选择正确的 `EDMXCellFormat`（例如，一个 RGB 灯具对应 `PF_RGB`）。
3. **Universe ID** 和 **Start Address**：指定 DMX 数据发送的起始宇宙和地址。
4. **Panel Size X / Y**：定义像素网格的行数和列数。
5. **Distribution**：选择像素在网格中的遍历顺序（例如，从左到右、从上到下、蛇形扫描等），这个值对应 `EDMXPixelMappingDistribution` 枚举，其排序逻辑由 `FDMXPixelMappingUtils::TextureDistributionSort` 实现。

## C++ 用法

`DMXPixelMappingCore` 模块主要提供核心的枚举定义和静态工具函数，用于处理像素分布排序和 DMX 通道计算。

### 头文件引入

```cpp
#include "DMXPixelMappingUtils.h"
#include "DMXPixelMappingTypes.h"
```

### 基本用法

计算一个特定像素格式下，一个 DMX 宇宙从指定起始地址开始还能容纳多少像素。
（来源：`Public/DMXPixelMappingUtils.h`）

```cpp
#include "DMXPixelMappingUtils.h"
#include "DMXPixelMappingTypes.h"

// 假设一个 RGBW (4通道) 灯具，从 DMX 地址 481 开始
EDMXCellFormat CellFormat = EDMXCellFormat::PF_RGBA; // RGBW 模式
uint32 StartAddress = 481;

// 计算一个 RGBW 像素需要多少通道 (应该是 4)
uint32 ChannelsPerCell = FDMXPixelMappingUtils::GetNumChannelsPerCell(CellFormat);

// 计算在该起始地址下，一个 DMX 宇宙最多还能放多少个 RGBW 像素
uint32 MaxPixelsInUniverse = FDMXPixelMappingUtils::GetUniverseMaxChannels(CellFormat, StartAddress);

// 检查是否至少能放下一个像素
bool bCanFitOnePixel = FDMXPixelMappingUtils::CanFitCellIntoChannels(CellFormat, StartAddress);
```

### 进阶用法

对一个包含组件指针的数组进行排序，以匹配你定义的像素分布模式（如蛇形扫描）。这在构建自定义的像素映射器时会用到。
（来源：`Public/DMXPixelMappingUtils.h` 中 `TextureDistributionSort` 的用法推断）

```cpp
#include "DMXPixelMappingUtils.h"
#include "DMXPixelMappingTypes.h"

// 假设有一个面板，尺寸为 10列 (X) x 8行 (Y)，共 80 个像素
const int32 NumXPanels = 10;
const int32 NumYPanels = 8;

// 一个未排序的组件数组，顺序是简单的从左到右，从上到下
TArray<UDMXPixelMappingComponent*> UnorderedComponents;
// ... 填充 UnorderedComponents 数组 ...

TArray<UDMXPixelMappingComponent*> SortedComponents;

// 选择一种分布模式，例如 “从左上角开始，按蛇形（顺时针）扫描”
EDMXPixelMappingDistribution Distribution = EDMXPixelMappingDistribution::TopLeftToClockwise;

// 使用核心工具函数进行排序
FDMXPixelMappingUtils::TextureDistributionSort<UDMXPixelMappingComponent*>(
    Distribution,
    NumXPanels,
    NumYPanels,
    UnorderedComponents,
    SortedComponents
);

// 现在 SortedComponents 中的顺序就是实际发送 DMX 数据的顺序
// 例如，第一行从左到右，第二行从右到左，以此类推
```

## Demo 示例

一个演示如何计算 DMX 通道使用情况的最小示例。这不是一个完整的插件组件，而是展示核心工具函数的用法。

**PixelMappingDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXPixelMappingTypes.h"
#include "PixelMappingDemo.generated.h"

UCLASS()
class APixelMappingDemo : public AActor
{
	GENERATED_BODY()
	
public:	
	APixelMappingDemo();

	// 在编辑器中运行此函数来演示计算
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "DMX Demo")
	void DemonstrateChannelCalculation();

	UPROPERTY(EditAnywhere, Category = "DMX Demo")
	EDMXCellFormat PixelFormat = EDMXCellFormat::PF_RGB;

	UPROPERTY(EditAnywhere, Category = "DMX Demo", meta = (ClampMin = "1", ClampMax = "512"))
	uint32 StartAddress = 1;
};
```

**PixelMappingDemo.cpp**
```cpp
#include "PixelMappingDemo.h"
#include "DMXPixelMappingUtils.h"

APixelMappingDemo::APixelMappingDemo()
{
	PrimaryActorTick.bCanEverTick = false;
}

void APixelMappingDemo::DemonstrateChannelCalculation()
{
	// 1. 计算单个像素占用的通道数
	uint32 ChannelsPerPixel = FDMXPixelMappingUtils::GetNumChannelsPerCell(PixelFormat);
	UE_LOG(LogTemp, Log, TEXT("Format: %s, Channels per pixel: %d"), *UEnum::GetValueAsString(PixelFormat), ChannelsPerPixel);

	// 2. 检查是否至少能容纳一个像素
	bool bCanFit = FDMXPixelMappingUtils::CanFitCellIntoChannels(PixelFormat, StartAddress);
	UE_LOG(LogTemp, Log, TEXT("Can fit at least one pixel at address %d? %s"), StartAddress, bCanFit ? TEXT("Yes") : TEXT("No"));

	// 3. 计算该地址下能容纳的最大像素数（可能跨宇宙，但此函数仅计算当前宇宙剩余空间）
	uint32 MaxPixels = FDMXPixelMappingUtils::GetUniverseMaxChannels(PixelFormat, StartAddress);
	UE_LOG(LogTemp, Log, TEXT("Max pixels in remaining universe space: %d"), MaxPixels);
}
```

## 模块依赖

从 Build.cs 的公共依赖来看，本插件的模块主要依赖于核心引擎和 DMX 模块。对于插件使用者（在你的项目中使用它的功能），无需额外添加依赖。如果你需要**扩展或开发新的 DMX 像素映射组件**，你可能需要依赖：

| 模块 | 用途 |
|---|---|
| `DMXCore` | 提供 DMX 协议、端口、Universe 等核心运行时类 |
| `RenderCore`, `RHI` | 用于 `DMXPixelMappingRenderer` 模块中与渲染纹理和材质交互的底层功能 |
| `Slate`, `SlateCore` | 用于 `DMXPixelMappingEditorWidgets` 模块中编辑器自定义界面 |
| `PropertyEditor` | 用于 `DMXPixelMappingEditor` 模块中自定义属性编辑器界面 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5f2a2a90` | DMX - Fix a crash when pixel mapping has unpatched components and draws patch colors | 修复了当像素映射包含未连接数据源的组件且尝试绘制Patch颜色时导致的崩溃问题。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 重构了视口客户端通知逻辑，减少了代码重复。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一次提交。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 同上，对视口通知逻辑的重复提交/修正。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量隐式转换为浮点数导致的编译警告。 |

### 维护评价

- **状态**：**活跃维护**。
- **分析**：插件创建于 2021 年，属于 UE5 早期组件。从 Git 历史看，最近一次更新在 2026 年 5 月，且近期提交聚焦于**稳定性修复**（如崩溃修复、编译警告消除）和**代码重构**。这表明 Epic 团队仍在积极维护此插件，并关注其代码质量与可靠性。
- **限制与建议**：该插件作为 UE5 虚拟制作管线的一部分，与引擎版本强绑定。其复杂度较高（源文件超过 200 个），涉及编辑器、运行时、渲染等多个子模块，因此学习曲线较陡。建议在官方示例项目（如 Virtual Production 模板）中先观察其工作流程。由于其设计目标明确，对于符合其使用场景（LED墙、复杂灯光阵列）的项目，**强烈推荐使用**，它是 UE5 内处理此类需求的标准且成熟的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档]() (暂无专门文档链接，参考 UE5 官方文档中 “Virtual Production” 和 “DMX” 相关章节)
- [测试用例]() (测试用例位于插件内部 `Source/*/Private/Tests/` 目录下)