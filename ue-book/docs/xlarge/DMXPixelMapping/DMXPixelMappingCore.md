# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `DMXPixelMappingCore` (Runtime), `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 插件的核心功能是将虚拟场景中的视觉内容（如纹理、材质、UMG控件）精确地映射到物理世界的LED像素阵列或灯具上。它解决了在虚拟制作（Virtual Production）中，如何将UE5渲染的画面实时、同步地输出到大量、任意形状排列的LED像素点（如LED灯带、矩阵屏幕、建筑立面照明）的复杂问题。该插件是连接数字内容创作与物理显示设备的关键桥梁。

## 使用场景

- **演唱会/舞台演出**：将UE5中设计的动态视觉效果、粒子效果或视频内容，实时映射到舞台背景的LED墙或灯带上。
- **建筑立面照明**：为大型建筑的外立面LED灯光秀设计内容，通过插件将纹理或动画精确分配到每个物理像素点。
- **沉浸式体验装置**：在博物馆、展览馆中，将交互式内容输出到由大量LED组成的异形装置上。
- **XR虚拟拍摄**：在LED Volume影棚中，精细控制LED面板上每个像素的显示内容，确保与摄像机视角完美匹配。

## 蓝图用法

### 核心数据类型

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EDMXPixelMappingRendererType` | 定义像素映射的源类型：纹理、材质或UMG控件 | `DMXPixelMappingTypes.h` |
| `EDMXCellFormat` | 定义DMX通道数据的颜色格式（如RGB, GRB, RGBA等） | `DMXPixelMappingTypes.h` |
| `EDMXColorMode` | 定义颜色模式：RGB或单色 | `DMXPixelMappingTypes.h` |

### 布局工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDMXPixelMappingUtils::TextureDistributionSort` | 根据指定的分布模式（如从左到右、蛇形排列等）对像素阵列进行排序 | `FDMXPixelMappingUtils` |

### 使用示例（蓝图描述）

1.  **创建DMX像素映射资产**：在内容浏览器中右键，选择“DMX” -> “DMX Pixel Mapping”。
2.  **配置像素阵列**：在资产编辑器中，设置阵列的行数、列数以及每个像素点的DMX地址。
3.  **选择渲染源**：在“Renderer”部分，选择`EDMXPixelMappingRendererType`（例如`Texture`），并指定一个纹理资产。
4.  **设置分布模式**：根据物理LED的排列方式，选择合适的`EDMXPixelMappingDistribution`（如`TopLeftToClockwise`用于蛇形排列）。
5.  **预览与输出**：在编辑器中预览映射效果，并通过DMX协议输出到物理设备。

## C++ 用法

### 头文件引入

```cpp
#include "DMXPixelMappingTypes.h"
#include "DMXPixelMappingUtils.h"
```

### 基本用法

```cpp
// 来源: DMXPixelMappingTypes.h
// 定义一个像素映射的渲染源为材质
EDMXPixelMappingRendererType RendererType = EDMXPixelMappingRendererType::Material;

// 定义DMX数据格式为常见的GRB顺序（许多LED灯带使用此格式）
EDMXCellFormat CellFormat = EDMXCellFormat::PF_GRB;

// 来源: DMXPixelMappingUtils.h
// 对一个表示像素位置的数组进行蛇形排序
TArray<FVector2D> UnorderedPixelPositions = { /* ... */ };
TArray<FVector2D> SortedPixelPositions;
FDMXPixelMappingUtils::TextureDistributionSort(
    EDMXPixelMappingDistribution::TopLeftToClockwise,
    10, // 列数
    5,  // 行数
    UnorderedPixelPositions,
    SortedPixelPositions
);
```

### 进阶用法

结合多个模块，可以实现从内容创建到渲染输出的完整流程。这通常涉及使用`DMXPixelMappingRuntime`模块中的类来管理映射资产，并通过`DMXPixelMappingRenderer`模块驱动实际的渲染和数据输出。

## Demo 示例

以下是一个最小化的C++示例，展示如何创建一个简单的DMX像素映射配置。

**DMXPixelMappingDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DMXPixelMappingTypes.h"

class FDMXPixelMappingDemo
{
public:
    void SetupSimpleMapping();
    
private:
    // 模拟一个2x2的像素阵列
    TArray<FVector2D> PixelGrid;
    EDMXPixelMappingRendererType CurrentRenderer = EDMXPixelMappingRendererType::Texture;
    EDMXCellFormat CurrentFormat = EDMXCellFormat::PF_RGB;
};
```

**DMXPixelMappingDemo.cpp**
```cpp
#include "DMXPixelMappingDemo.h"
#include "DMXPixelMappingUtils.h"

void FDMXPixelMappingDemo::SetupSimpleMapping()
{
    // 1. 初始化一个2x2的网格坐标
    PixelGrid.Add(FVector2D(0, 0)); // 左上
    PixelGrid.Add(FVector2D(1, 0)); // 右上
    PixelGrid.Add(FVector2D(0, 1)); // 左下
    PixelGrid.Add(FVector2D(1, 1)); // 右下

    // 2. 设置渲染源为纹理
    CurrentRenderer = EDMXPixelMappingRendererType::Texture;

    // 3. 设置DMX数据格式为RGB
    CurrentFormat = EDMXCellFormat::PF_RGB;

    // 4. 对网格进行排序（例如，按从左到右，从上到下的顺序）
    TArray<FVector2D> SortedGrid;
    FDMXPixelMappingUtils::TextureDistributionSort(
        EDMXPixelMappingDistribution::TopLeftToRight,
        2, // 列数
        2, // 行数
        PixelGrid,
        SortedGrid
    );

    // 此时 SortedGrid 中的顺序即为DMX数据发送的顺序
    // 后续可将此顺序与DMX Universe的地址绑定，并驱动渲染器输出对应像素的颜色。
}
```

## 模块依赖

该插件由多个模块组成，彼此间存在依赖关系。作为使用者，你的项目模块通常需要依赖 `DMXPixelMappingRuntime` 来访问核心运行时功能。编辑器功能则由 `DMXPixelMappingEditor` 模块提供。

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingRuntime` | 提供运行时核心类，用于加载、管理和驱动DMX像素映射资产。 |
| `DMXPixelMappingRenderer` | 负责实际的渲染逻辑，将纹理/材质/UMG内容采样并转换为DMX数据。 |
| `DMXPixelMappingCore` | 定义核心数据类型、枚举和工具函数。 |
| `DMXPixelMappingEditor` | 提供编辑器内的资产编辑器、预览窗口和工具。 |
| `DMXPixelMappingBlueprintGraph` | 提供蓝图节点支持，允许在蓝图中操作像素映射。 |
| `DMXPixelMappingEditorWidgets` | 提供编辑器专用的UI控件。 |

## 维护状态

### 近期更新

```
- f333b1c99a59 DMX - Remove type aliases to improve readability of pixel mapping code, reduce inclusion of monolithic headers
- bbc37aa2f5e6 [Engine/Plugins] * Another batch iwyu updates to reduce number of includes used in files
- dc856801cdec Merge from Release-Engine-Test @ 17059716 to UE5/Main This represents UE4/Main @ 17030256 and Dev-PerfTest @ 17029914
```
*   `f333b1c99a59`: 重构代码，移除类型别名以提高可读性，并减少对大型头文件的包含。这是一次代码质量改进。
*   `bbc37aa2f5e6`: 批量进行IWYU（Include What You Use）更新，优化头文件包含，属于编译优化和代码清理。
*   `dc856801cdec`: 从引擎测试分支合并的常规集成。

### 维护评价

- **创建时间**：约5年前（2020年），属于较新的插件。
- **近期活动**：最近的提交集中在代码清理、可读性提升和编译优化上，表明插件仍在积极维护和优化中，但没有重大的新功能提交。
- **维护状态**：**维护中**。作为虚拟制作管线的关键组件，Epic Games 会持续维护其与引擎版本的兼容性和稳定性。
- **推荐使用**：**推荐**。对于任何涉及将UE5内容输出到物理LED像素阵列的虚拟制作项目，此插件是官方且功能完备的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档]()（暂无）
- [测试用例]()（路径待确认，通常位于 `Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Tests/`）