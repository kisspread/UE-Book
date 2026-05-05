# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DMX资产） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 插件提供了一套完整的工具集，用于将虚拟的像素内容（如纹理、材质、蓝图逻辑）精确映射到物理世界的 LED 灯具阵列或像素灯带上。它解决了在虚拟制作（Virtual Production）、舞台灯光、建筑照明等场景中，如何高效、灵活地控制大量 DMX 像素设备的核心问题。无论 LED 阵列的形状是平面、曲面还是不规则形状，该插件都能通过其组件化架构和渲染管线进行适配和驱动。

## 使用场景

- **虚拟制作 LED 墙**：将虚拟摄像机视图或特定内容实时渲染并映射到大型 LED 墙的物理像素上。
- **舞台灯光设计**：控制由数百或数千个独立像素组成的 LED 灯带、灯条或矩阵，实现复杂的动态灯光效果。
- **建筑立面照明**：为建筑外墙的 LED 灯光系统创建和播放像素动画。
- **任何需要精确控制大量 DMX 像素设备的场合**：该插件提供了从内容创建、布局设计到实时渲染和输出的完整工作流。

## 蓝图用法

核心的运行时功能和组件主要位于 `DMXPixelMappingRuntime` 模块中。通过蓝图，您可以创建和配置像素映射组件（如 `UDMXPixelMappingRendererComponent`），设置其尺寸、像素布局以及要映射的材质或纹理。

**核心功能**：
- 创建和管理像素映射布局。
- 将材质或纹理的像素数据实时转换为 DMX 信号。
- 通过蓝图逻辑动态控制映射效果。

*详细的蓝图节点和用法，请参阅子模块文档：[DMXPixelMappingRuntime](DMXPixelMappingRuntime.md)。*

## C++ 用法

在 C++ 中，您可以利用 `DMXPixelMappingRuntime` 模块提供的类来程序化地创建和管理像素映射。核心类包括用于定义映射布局的 `UDMXPixelMapping` 和用于执行渲染输出的 `UDMXPixelMappingRendererComponent`。

**基本步骤**：
1.  引入必要的头文件。
2.  创建或加载一个 `UDMXPixelMapping` 资产。
3.  在 Actor 中添加 `UDMXPixelMappingRendererComponent` 并关联映射资产。
4.  配置组件的属性（如输出分辨率、DMX 协议等）。

*详细的 C++ API 和示例，请参阅子模块文档：[DMXPixelMappingRuntime](DMXPixelMappingRuntime.md) 和 [DMXPixelMappingCore](DMXPixelMappingCore.md)。*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在 Actor 中设置一个 DMX 像素映射渲染器。

**MyDMXActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyDMXActor.generated.h"

class UDMXPixelMappingRendererComponent;

UCLASS()
class AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMX")
    UDMXPixelMappingRendererComponent* PixelMappingRenderer;
};
```

**MyDMXActor.cpp**
```cpp
#include "MyDMXActor.h"
#include "DMXPixelMappingRendererComponent.h"

AMyDMXActor::AMyDMXActor()
{
    PixelMappingRenderer = CreateDefaultSubobject<UDMXPixelMappingRendererComponent>(TEXT("PixelMappingRenderer"));
    RootComponent = PixelMappingRenderer;

    // 在编辑器中或通过蓝图进一步配置 PixelMappingRenderer 的属性，
    // 例如关联一个 UDMXPixelMapping 资产。
}
```

## 模块依赖

要使用此插件，您的项目模块通常需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingRuntime` | 提供运行时像素映射的核心类和组件。 |
| `DMXPixelMappingCore` | 提供基础数据类型和接口。 |
| `DMX` | UE 的 DMX 协议基础框架。 |
| `DMXEngine` | DMX 引擎，处理信号的发送与接收。 |

*编辑器功能需要额外依赖 `DMXPixelMappingEditor` 等模块。*

## 维护状态

### 近期更新

由于未提供具体的 git log 信息，无法列出近期 commit。该插件作为 Unreal Engine 虚拟制作工具链的一部分，通常会随着引擎版本更新而获得维护。

### 维护评价

- **创建时间**：2020年9月，相对较新。
- **活跃度**：作为 Epic Games 官方维护的虚拟制作核心组件，预计会持续更新以支持新功能和引擎版本。
- **推荐度**：**强烈推荐**。这是 UE 中处理 DMX 像素映射的官方且功能完整的解决方案，适用于所有相关专业领域。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dmx-pixel-mapping-in-unreal-engine/) (UE 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Tests)