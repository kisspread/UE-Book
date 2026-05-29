# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 中文名 | DMX像素映射 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `DMXPixelMappingCore` (Runtime), `DMXPixelMappingRuntime` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 插件提供了一套完整的工具，用于将任意形状和大小的 LED 数字像素条或灯具阵列映射到视觉内容。其核心是解决虚拟制作中的一个关键问题：如何将二维或三维的视觉内容（如纹理、材质、UMG 控件）精确地采样、处理和分配到大量的物理 DMX 控制的像素点上。

该插件**不仅仅是一个简单的渲染工具**，它是一个完整的像素映射管线。它允许艺术家和开发者在 Unreal Engine 中创建复杂的像素布局，将视觉输入（如实时合成的视频、材质效果或 UI 动画）经过预处理（降采样、滤波）后，最终将颜色数据精确地分配到每个像素点对应的 DMX 通道上，从而控制舞台、建筑立面或 LED 墙面的灯光效果。

## 使用场景

- **虚拟制作 LED 墙面**：您正在为一个虚拟拍摄项目构建一个由数千个 LED 面板组成的弧形屏幕。需要将摄像机的实拍画面或 CG 场景实时渲染并映射到这个不规则的物理屏幕上，确保视觉内容无变形、无撕裂。→ 使用 DMX Pixel Mapping 创建像素映射布局，并将渲染目标作为输入。
- **建筑立面灯光秀**：您需要设计一个控制建筑外墙灯光的程序，灯光阵列并非简单的网格，而是包含窗户、装饰条等不规则形状。您希望用一个动态的材质或视频来驱动整个灯光效果。→ 使用本插件定义每个像素灯的位置，并将材质/纹理输入进行预处理后映射。
- **舞台演出像素控制**：在演唱会或活动中，您需要控制大量像素灯条、灯带或 LED 地砖。您希望基于音乐节奏或互动，用简单的 UMG 动画或程序化材质来驱动所有灯光。→ 将 UMG 动画作为输入，经过降采样和滤波后映射到所有像素。

## 蓝图用法

以下节点来自 `DMXPixelMappingRenderer` 模块的核心类，可在蓝图中用于控制像素映射的渲染流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Input Texture` | 设置要进行像素映射的源纹理。 | `UDMXPixelMappingPreprocessRenderer` |
| `Set Input Material` | 设置要进行像素映射的源材质。 | `UDMXPixelMappingPreprocessRenderer` |
| `Set Input User Widget` | 设置要进行像素映射的 UMG 控件。 | `UDMXPixelMappingPreprocessRenderer` |
| `Render` | 执行预处理渲染，生成用于采样的中间纹理。 | `UDMXPixelMappingPreprocessRenderer` |
| `Get Rendered Texture` | 获取经过预处理（降采样、滤波）后的纹理结果。 | `UDMXPixelMappingPreprocessRenderer` |
| `Set Elements` | 设置需要进行像素映射渲染的元素数组。 | `UDMXPixelMappingPixelMapRenderer` |
| `Render` | 根据设置的元素，将输入纹理的颜色采样并映射到输出。 | `UDMXPixelMappingPixelMapRenderer` |

### 使用示例（蓝图描述）

1.  **创建预处理渲染器**：使用 `Create Object (UDMXPixelMappingPreprocessRenderer)` 节点创建一个预处理渲染器实例。
2.  **设置输入源**：将您的纹理、材质或 UMG 控件分别通过 `Set Input Texture`、`Set Input Material` 或 `Set Input User Widget` 节点连接到该实例。需要指定像素格式。
3.  **配置处理参数**：通过设置实例的属性（如 `Num Down Sample Passes`，`Filter Material`，`Blur Distance`）来配置降采样次数、滤波材质和模糊强度。
4.  **获取预处理结果**：调用 `Render` 节点后，使用 `Get Rendered Texture` 节点获取处理后的纹理。
5.  **进行像素映射**：创建 `UDMXPixelMappingPixelMapRenderer` 实例，通过 `Set Elements` 节点传入一个包含所有 `FPixelMapRenderElement` 的数组（这些元素定义了每个像素在 UV 空间中的位置和大小）。最后调用其 `Render` 节点，传入上一步得到的纹理，即可完成最终的像素颜色采样与映射。

## C++ 用法

本模块主要提供渲染相关的 API，用于在运行时或自定义逻辑中执行像素映射操作。

### 头文件引入

```cpp
#include “DMXPixelMappingPreprocessRenderer.h”
#include “DMXPixelMappingPixelMapRenderer.h”
#include “DMXPixelMappingRenderElement.h”
```

### 基本用法

以下代码展示了如何创建预处理渲染器并设置输入材质。
*来源：根据 `UDMXPixelMappingPreprocessRenderer` 接口推断*

```cpp
// 1. 创建一个预处理渲染器实例
UDMXPixelMappingPreprocessRenderer* PreprocessRenderer = NewObject<UDMXPixelMappingPreprocessRenderer>();

// 2. 设置输入为一个材质，并指定像素格式
UMaterialInterface* MyMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT(“/Game/Materials/M_LED_Effect”));
PreprocessRenderer->SetInputMaterial(MyMaterial, PF_B8G8R8A8);

// 3. (可选) 配置参数，如降采样次数
PreprocessRenderer->SetNumDownSamplePasses(2); // 注意：这是一个假设的公开setter，实际属性为私有

// 4. 执行渲染
PreprocessRenderer->Render();

// 5. 获取结果
UTexture* ResultTexture = PreprocessRenderer->GetRenderedTexture();
```

### 进阶用法

以下代码展示了如何创建像素映射元素并执行最终渲染。
*来源：根据 `UDMXPixelMappingPixelMapRenderer` 和 `FPixelMapRenderElement` 接口推断*

```cpp
// 承接上面的 ResultTexture

// 1. 创建像素映射元素数组
TArray<TSharedRef<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>> Elements;

// 2. 创建几个代表不同像素的元素（实际数量可能成千上万）
for (int32 i = 0; i < 100; ++i)
{
    UE::DMXPixelMapping::Rendering::FPixelMapRenderElementParameters Params;
    Params.UV = FVector2D(i % 10 * 0.1f, i / 10 * 0.1f); // 假设的UV位置
    Params.UVSize = FVector2D(0.1f, 0.1f); // 假设的UV大小
    Params.CellBlendingQuality = EDMXPixelBlendingQuality::High;
    Params.bStaticCalculateUV = true;

    TSharedRef<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement> Element = MakeShared<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>(Params);
    Elements.Add(Element);
}

// 3. 创建像素映射渲染器并设置元素
UDMXPixelMappingPixelMapRenderer* PixelMapRenderer = NewObject<UDMXPixelMappingPixelMapRenderer>();
PixelMapRenderer->SetElements(Elements, PF_FloatRGBA); // 指定输出格式

// 4. 执行最终的像素映射渲染
PixelMapRenderer->Render(ResultTexture, 1.0f); // 传入预处理纹理和亮度

// 渲染完成后，PixelMapRenderer内部会将采样到的颜色值通过 FPixelMapRenderElement::SetColor 线程安全地传递给每个元素。
// 您可以通过 Element->GetColor() 获取每个像素最终映射到的颜色。
```

## Demo 示例

一个最小化的 C++ 示例，演示如何将纹理输入经过预处理后进行简单的像素映射。

### DMXPixelMappingDemo.h
```cpp
// 版权声明省略
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “DMXPixelMappingDemo.generated.h”

class UDMXPixelMappingPreprocessRenderer;
class UDMXPixelMappingPixelMapRenderer;
namespace UE::DMXPixelMapping { namespace Rendering { class FPixelMapRenderElement; } }

UCLASS()
class ADMXPixelMappingDemo : public AActor
{
    GENERATED_BODY()

public:
    ADMXPixelMappingDemo();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = “DMX”)
    UTexture* InputTexture;

private:
    UPROPERTY()
    UDMXPixelMappingPreprocessRenderer* PreprocessRenderer;

    UPROPERTY()
    UDMXPixelMappingPixelMapRenderer* PixelMapRenderer;

    TArray<TSharedRef<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>> RenderElements;
};
```

### DMXPixelMappingDemo.cpp
```cpp
// 版权声明省略
#include “DMXPixelMappingDemo.h”
#include “DMXPixelMappingPreprocessRenderer.h”
#include “DMXPixelMappingPixelMapRenderer.h”
#include “DMXPixelMappingRenderElement.h”

ADMXPixelMappingDemo::ADMXPixelMappingDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ADMXPixelMappingDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 初始化预处理渲染器
    PreprocessRenderer = NewObject<UDMXPixelMappingPreprocessRenderer>(this);
    if (InputTexture)
    {
        PreprocessRenderer->SetInputTexture(InputTexture, PF_B8G8R8A8);
    }

    // 2. 创建一些示例像素元素（例如一个4x4的网格）
    for (int32 i = 0; i < 16; ++i)
    {
        UE::DMXPixelMapping::Rendering::FPixelMapRenderElementParameters Params;
        Params.UV = FVector2D(i % 4 * 0.25f, i / 4 * 0.25f);
        Params.UVSize = FVector2D(0.25f, 0.25f);
        Params.CellBlendingQuality = EDMXPixelBlendingQuality::Medium;
        Params.bStaticCalculateUV = true;

        TSharedRef<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement> Element = MakeShared<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>(Params);
        RenderElements.Add(Element);
    }

    // 3. 初始化像素映射渲染器
    PixelMapRenderer = NewObject<UDMXPixelMappingPixelMapRenderer>(this);
    PixelMapRenderer->SetElements(RenderElements, PF_FloatRGBA);
}

void ADMXPixelMappingDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 每帧执行渲染管线（实际项目中可能需要优化调用频率）
    if (PreprocessRenderer && InputTexture)
    {
        // 步骤A：预处理
        PreprocessRenderer->Render();
        UTexture* PreprocessedTexture = PreprocessRenderer->GetRenderedTexture();

        // 步骤B：像素映射
        if (PixelMapRenderer && PreprocessedTexture)
        {
            PixelMapRenderer->Render(PreprocessedTexture, 1.0f);

            // 可选：读取像素颜色（例如用于调试或发送到外部设备）
            // for (const auto& Element : RenderElements)
            // {
            //     FLinearColor Color = Element->GetColor();
            //     // ... 使用颜色值
            // }
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。本模块 `DMXPixelMappingRenderer` 的 Build.cs 文件中的依赖项主要是基础引擎模块（如 `Core`, `Engine`, `RenderCore`, `RHI`, `SlateCore`），以及可能存在的 `DMXPixelMappingCore` 内部模块。对于插件使用者，无需引入除 `DMXPixelMappingCore` 和 `DMXPixelMappingRuntime` 之外的独特模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5f2a2a90` | DMX - Fix a crash when pixel mapping has unpatched components and draws patch colors | 修复了当像素映射包含未连接组件并绘制补丁颜色时发生的崩溃。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口代码，通过通知机制减少重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了 CL53913857 的更改。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口代码，通过通知机制减少重复代码。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数导致的警告。 |

### 维护评价

- **创建时间**：插件于 2021 年创建，属于相对较新的功能。
- **最近更新**：最近一次更新在 2026 年 5 月，包含了 Bug 修复和代码重构。更新频率稳定，显示该模块仍在**积极维护**中。
- **活跃度**：属于虚拟制作的核心功能之一，随着虚拟制片技术的普及，其重要性日益增加，预计将持续获得支持。
- **已知问题**：源码中存在大量从 5.2 到 5.4 版本标记的 `DEPRECATED` 函数和结构体，表明该模块经历了重大重构和 API 清理。使用时应遵循最新的 API（如 `UDMXPixelMappingPixelMapRenderer`）。
- **推荐使用**：**推荐使用**。该模块是实现大规模 LED 像素映射的标准解决方案，API 在持续演进中，能够满足虚拟制作中复杂的像素控制需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- 官方文档：无
- 测试用例：无（测试用例可能位于 `Engine/Tests/` 或插件内部，但未在提供的路径中直接列出）