# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingCore` (Runtime), `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 是 UE5 虚拟制片工具链中的 **LED 像素映射系统**。它解决的核心问题是：如何将视频/材质/UMG Widget 的画面内容，按照任意形状和尺寸，精确映射到物理 LED 灯带、LED 面板或灯具阵列上，并通过 DMX 协议实时输出颜色数据。

具体来说，这个插件提供了一套完整的管线：

1. **输入源处理（Preprocess）**：支持纹理、材质、UMG Widget 作为输入源，可应用滤镜材质进行预处理
2. **像素映射（Pixel Mapping）**：将输入画面的像素区域映射到 DMX 灯具的物理位置，支持任意布局
3. **渲染输出（Rendering）**：通过 GPU 着色器高效采样颜色，支持多种混合质量等级（Low/Medium/High），并通过三缓冲机制实现线程安全的数据传输
4. **DMX 输出**：将采样到的颜色数据通过 DMX 协议发送到物理设备

这是大型虚拟制片项目（如 LED Volume / LED Wall）中不可或缺的工具，用于将 Unreal 的渲染画面实时投射到 LED 屏幕上。

## 使用场景

- 你在搭建 LED Volume（LED 墙）虚拟制片场景 → 用 DMXPixelMapping 将 Unreal 画面映射到 LED 面板
- 你需要控制大量 LED 灯带/像素条，按形状排列 → 用 DMXPixelMapping 定义像素布局
- 你需要将 UMG Widget 或材质的视觉效果实时输出到 DMX 灯具 → 用 DMXPixelMapping 的预处理+渲染管线
- 你在做建筑立面灯光秀，需要将视频内容映射到不规则 LED 阵列 → 用 DMXPixelMapping

## 子模块概览

本插件规模较大（306 个源文件），按功能拆分为 6 个子模块：

| 模块 | 类型 | 职责 |
|---|---|---|
| `DMXPixelMappingCore` | Runtime | 核心数据模型：像素映射布局、组件层次结构、DMX 灯具绑定 |
| `DMXPixelMappingRuntime` | Runtime | 运行时逻辑：像素映射执行、颜色采样、DMX 数据输出 |
| `DMXPixelMappingRenderer` | Runtime | GPU 渲染管线：预处理渲染、像素映射渲染、着色器管理 |
| `DMXPixelMappingBlueprintGraph` | Runtime | 蓝图集成：自定义蓝图节点和图表支持 |
| `DMXPixelMappingEditor` | Runtime | 编辑器工具：像素映射编辑器 UI、布局编辑、预览 |
| `DMXPixelMappingEditorWidgets` | Runtime | 编辑器自定义控件：专用 Widget 和交互组件 |

## 渲染管线架构

```
输入源 (Texture / Material / UMG Widget)
         │
         ▼
┌─────────────────────────┐
│  Preprocess Renderer    │  ← 预处理：渲染输入源，可应用滤镜材质
│  (UDMXPixelMapping      │     支持缩放模式：SameAsInput / Downsampled / CustomSize
│   PreprocessRenderer)   │
└───────────┬─────────────┘
            │ 预处理后的纹理
            ▼
┌─────────────────────────┐
│  Pixel Map Renderer     │  ← 像素映射：按 FPixelMapRenderElement 采样颜色
│  (UDMXPixelMapping      │     支持 Low(1采样) / Medium(5采样) / High(9采样)
│   PixelMapRenderer)     │
└───────────┬─────────────┘
            │ 采样后的颜色数据
            ▼
┌─────────────────────────┐
│  Triple Buffered Data   │  ← 线程安全传输：三缓冲机制
│  (TDMXPixelMapping      │     生产者线程写入 → 原子交换 → 消费者线程读取
│   TripleBufferedData)   │
└───────────┬─────────────┘
            │
            ▼
      DMX 协议输出到物理设备
```

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputTexture` | 设置纹理作为像素映射的输入源 | `UDMXPixelMappingPreprocessRenderer` |
| `SetInputMaterial` | 设置材质作为像素映射的输入源 | `UDMXPixelMappingPreprocessRenderer` |
| `SetInputUserWidget` | 设置 UMG Widget 作为像素映射的输入源 | `UDMXPixelMappingPreprocessRenderer` |
| `ClearInput` | 清除当前输入源 | `UDMXPixelMappingPreprocessRenderer` |
| `Render` | 执行预处理渲染 | `UDMXPixelMappingPreprocessRenderer` |
| `GetRenderedTexture` | 获取预处理后的纹理 | `UDMXPixelMappingPreprocessRenderer` |
| `GetResultingSize2D` | 获取预处理结果的尺寸 | `UDMXPixelMappingPreprocessRenderer` |
| `SetElements` | 设置像素映射渲染元素 | `UDMXPixelMappingPixelMapRenderer` |
| `Render` | 执行像素映射渲染并采样颜色 | `UDMXPixelMappingPixelMapRenderer` |

### 使用示例（蓝图描述）

**示例 1：基本纹理输入 → 像素映射**

1. 创建 `UDMXPixelMappingPreprocessRenderer` 对象
2. 调用 `SetInputTexture`，传入你的视频纹理和目标像素格式
3. 调用 `Render` 执行预处理
4. 创建 `UDMXPixelMappingPixelMapRenderer` 对象
5. 调用 `SetElements`，传入像素映射元素数组（每个元素定义了 UV 位置和采样质量）
6. 调用 `Render`，传入预处理后的纹理和亮度值
7. 采样后的颜色数据通过三缓冲机制自动传输到 DMX 输出线程

**示例 2：UMG Widget 作为输入源**

1. 创建你的 UMG Widget（如一个动态仪表盘）
2. 调用 `SetInputUserWidget` 将 Widget 设为输入源
3. 后续流程同上——Widget 会被渲染为纹理，然后进行像素映射

## C++ 用法

### 头文件引入

```cpp
// 渲染器模块
#include "IDMXPixelMappingRendererModule.h"
#include "DMXPixelMappingPixelMapRenderer.h"
#include "DMXPixelMappingPreprocessRenderer.h"
#include "DMXPixelMappingRenderElement.h"
```

### 基本用法：创建像素映射渲染器

```cpp
// 来源: DMXPixelMappingRenderer/Public/IDMXPixelMappingRendererModule.h

// 检查模块是否可用
if (IDMXPixelMappingRendererModule::IsAvailable())
{
    // 获取模块实例
    IDMXPixelMappingRendererModule& RendererModule = IDMXPixelMappingRendererModule::Get();
    
    // 创建渲染器实例（可创建多个）
    TSharedPtr<IDMXPixelMappingRenderer> Renderer = RendererModule.CreateRenderer();
}
```

### 基本用法：预处理渲染

```cpp
// 来源: DMXPixelMappingRenderer/Public/DMXPixelMappingPreprocessRenderer.h

// 创建预处理渲染器
UDMXPixelMappingPreprocessRenderer* PreprocessRenderer = NewObject<UDMXPixelMappingPreprocessRenderer>();

// 设置输入源（三选一）
PreprocessRenderer->SetInputTexture(MyTexture, EPixelFormat::PF_B8G8R8A8);
// 或
PreprocessRenderer->SetInputMaterial(MyMaterial, EPixelFormat::PF_B8G8R8A8);
// 或
PreprocessRenderer->SetInputUserWidget(MyWidget, EPixelFormat::PF_B8G8R8A8);

// 执行预处理渲染
PreprocessRenderer->Render();

// 获取结果
UTexture* RenderedTexture = PreprocessRenderer->GetRenderedTexture();
FVector2D ResultSize = PreprocessRenderer->GetResultingSize2D();
```

### 基本用法：像素映射渲染

```cpp
// 来源: DMXPixelMappingRenderer/Public/DMXPixelMappingPixelMapRenderer.h
// 来源: DMXPixelMappingRenderer/Public/DMXPixelMappingRenderElement.h

// 创建像素映射渲染器
UDMXPixelMappingPixelMapRenderer* PixelMapRenderer = NewObject<UDMXPixelMappingPixelMapRenderer>();

// 定义渲染元素
TArray<TSharedRef<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>> Elements;

UE::DMXPixelMapping::Rendering::FPixelMapRenderElementParameters Params;
Params.UV = FVector2D(0.5f, 0.5f);          // UV 中心位置
Params.UVSize = FVector2D(0.1f, 0.1f);      // UV 采样区域大小
Params.Rotation = 0.0;                        // 旋转角度
Params.CellBlendingQuality = EDMXPixelBlendingQuality::Medium; // 5 采样点
Params.bStaticCalculateUV = true;             // 静态 UV 计算

Elements.Add(MakeShared<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>(Params));

// 设置元素并指定像素格式
PixelMapRenderer->SetElements(Elements, EPixelFormat::PF_B8G8R8A8);

// 执行渲染，传入输入纹理和全局亮度
PixelMapRenderer->Render(InputTexture, 1.0f);
```

### 进阶用法：线程安全的颜色读取

```cpp
// 来源: DMXPixelMappingRenderer/Public/DMXPixelMappingRenderElement.h

// FPixelMapRenderElement 使用三缓冲机制实现线程安全
// 渲染线程（生产者）写入颜色
auto Element = MakeShared<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>(Params);
Element->SetColor(FLinearColor(1.0f, 0.0f, 0.0f, 1.0f)); // 红色

// 游戏线程（消费者）读取颜色
FLinearColor Color = Element->GetColor(); // 线程安全读取

// 参数也可以线程安全地更新
UE::DMXPixelMapping::Rendering::FPixelMapRenderElementParameters NewParams;
NewParams.UV = FVector2D(0.3f, 0.3f);
NewParams.CellBlendingQuality = EDMXPixelBlendingQuality::High; // 9 采样点
Element->SetParameters(NewParams); // 线程安全写入
```

### 进阶用法：自定义预处理尺寸模式

```cpp
// 来源: DMXPixelMappingRenderer/Public/DMXPixelMappingPreprocessRenderer.h

// 预处理支持三种尺寸模式
// EDMXPixelMappingRenderingPreprocessorSizeMode::SameAsInput  - 与输入同尺寸
// EDMXPixelMappingRenderingPreprocessorSizeMode::Downsampled  - 降采样
// EDMXPixelMappingRenderingPreprocessorSizeMode::CustomSize   - 自定义尺寸

// 通过 PreprocessRenderer 的 Filter Material 可以在预处理阶段
// 应用自定义材质进行色彩校正、亮度调整等操作
```

## Demo 示例

### 完整的像素映射渲染管线

```cpp
// DMXPixelMappingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMXPixelMappingDemo.generated.h"

class UDMXPixelMappingPreprocessRenderer;
class UDMXPixelMappingPixelMapRenderer;
class UTextureRenderTarget2D;
class UTexture;

UCLASS()
class ADMXPixelMappingDemo : public AActor
{
    GENERATED_BODY()

public:
    ADMXPixelMappingDemo();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 输入纹理（如视频纹理） */
    UPROPERTY(EditAnywhere, Category = "DMX")
    TObjectPtr<UTexture> InputTexture;

    /** 全局亮度 */
    UPROPERTY(EditAnywhere, Category = "DMX", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float Brightness = 1.0f;

private:
    /** 预处理渲染器 */
    UPROPERTY(Transient)
    TObjectPtr<UDMXPixelMappingPreprocessRenderer> PreprocessRenderer;

    /** 像素映射渲染器 */
    UPROPERTY(Transient)
    TObjectPtr<UDMXPixelMappingPixelMapRenderer> PixelMapRenderer;

    /** 像素映射元素 */
    TArray<TSharedRef<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>> RenderElements;
};
```

```cpp
// DMXPixelMappingDemo.cpp
#include "DMXPixelMappingDemo.h"
#include "DMXPixelMappingPreprocessRenderer.h"
#include "DMXPixelMappingPixelMapRenderer.h"
#include "DMXPixelMappingRenderElement.h"

ADMXPixelMappingDemo::ADMXPixelMappingDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ADMXPixelMappingDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建预处理渲染器
    PreprocessRenderer = NewObject<UDMXPixelMappingPreprocessRenderer>(this);

    // 2. 设置输入源
    if (InputTexture)
    {
        PreprocessRenderer->SetInputTexture(InputTexture, EPixelFormat::PF_B8G8R8A8);
    }

    // 3. 创建像素映射渲染器
    PixelMapRenderer = NewObject<UDMXPixelMappingPixelMapRenderer>(this);

    // 4. 定义 4x4 网格的像素映射元素
    const int32 GridSize = 4;
    for (int32 Y = 0; Y < GridSize; ++Y)
    {
        for (int32 X = 0; X < GridSize; ++X)
        {
            UE::DMXPixelMapping::Rendering::FPixelMapRenderElementParameters Params;
            Params.UV = FVector2D(
                (X + 0.5f) / GridSize,
                (Y + 0.5f) / GridSize
            );
            Params.UVSize = FVector2D(1.0f / GridSize, 1.0f / GridSize);
            Params.Rotation = 0.0;
            Params.CellBlendingQuality = EDMXPixelBlendingQuality::Medium;
            Params.bStaticCalculateUV = true;

            RenderElements.Add(
                MakeShared<UE::DMXPixelMapping::Rendering::FPixelMapRenderElement>(Params)
            );
        }
    }

    // 5. 设置元素到像素映射渲染器
    PixelMapRenderer->SetElements(RenderElements, EPixelFormat::PF_B8G8R8A8);
}

void ADMXPixelMappingDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!PreprocessRenderer || !PixelMapRenderer)
    {
        return;
    }

    // 6. 每帧执行预处理
    PreprocessRenderer->Render();

    // 7. 获取预处理后的纹理
    UTexture* PreprocessedTexture = PreprocessRenderer->GetRenderedTexture();
    if (PreprocessedTexture)
    {
        // 8. 执行像素映射渲染，采样颜色
        PixelMapRenderer->Render(PreprocessedTexture, Brightness);

        // 9. 从渲染元素读取颜色（线程安全）
        for (int32 i = 0; i < RenderElements.Num(); ++i)
        {
            FLinearColor Color = RenderElements[i]->GetColor();
            // 此处可将 Color 通过 DMX 协议发送到对应的灯具
            // 例如: DMXOutput->SetColor(i, Color);
        }
    }
}
```

## 模块依赖

从各模块的 Build.cs 分析，本插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | DMX 协议核心，用于 DMX 数据的发送和接收 |
| `DMXRuntime` | DMX 运行时，管理 DMX 端口和连接 |
| `DMXEditor` | DMX 编辑器工具（编辑器模块依赖） |
| `RenderCore` | 渲染核心，用于 GPU 渲染管线和着色器 |
| `RHI` | 渲染硬件接口，用于 RenderTarget 和纹理操作 |
| `MediaAssets` | 媒体资产，支持视频纹理作为输入源 |
| `MediaUtils` | 媒体工具函数 |

## 维护状态

### 近期更新

```
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
  → 代码规范化，移除 FORCEINLINE 宏的使用
- 3a2759851c2b DMX: Fix an issue where OSX did not render DMX Pixel Mappings correctly and sent zero instead of color values
  → 修复 macOS 平台上像素映射渲染错误（输出零值而非正确颜色）的关键 bug
- 9fb339dda676 Fix macros for RDG GPU stats to support new GPU profiler
  → 适配 UE5 新版 GPU Profiler，更新 RDG 统计宏
```

### 维护评价

- **创建时间**：2020 年 9 月，约 5 年历史
- **活跃度**：活跃维护中。近期有平台兼容性修复（macOS）和引擎适配更新（GPU Profiler），表明 Epic 持续关注此插件
- **代码质量**：有完善的三缓冲线程安全机制、GPU 着色器管线、多种输入源支持，架构成熟
- **已知限制**：部分旧 API 已标记为 `UE_DEPRECATED(5.4)`，建议使用新版本的带像素格式参数的重载
- **推荐程度**：✅ **强烈推荐**用于虚拟制片 LED Volume 项目。这是 Epic 官方维护的核心虚拟制片工具，与 DMX 协议栈深度集成，适合大型 LED 墙场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [DMXPixelMappingRenderer 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingRenderer)
- [DMXPixelMappingCore 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingCore)
- [DMXPixelMappingRuntime 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingRuntime)
- [DMXPixelMappingEditor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingEditor)