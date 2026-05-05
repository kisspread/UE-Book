# Texture Graph

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime), `Continuable` (External), `Function2` (External) |
| 实验性 | 否 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

---

## 用途

TextureGraph 是一个**基于节点图的程序化纹理生成工具**，允许用户通过连接各种表达式节点来创建复杂的纹理资产。它解决的核心问题是：**在不依赖外部纹理编辑软件的情况下，在引擎内以可视化、可参数化、可复用的方式生成纹理**。

与 UE 内置的 Material Editor 不同，TextureGraph 专注于**纹理数据的生成和处理**，而非材质着色。它提供了一套完整的节点图系统，涵盖：

- **输入**：加载现有纹理资产、文件路径、标量/向量/颜色参数
- **处理**：模糊、边缘检测、膨胀/腐蚀、扭曲、混合、反转、亮度对比度调整等
- **通道操作**：拆分/合并/重排 RGBA 通道
- **数学运算**：条件选择（IfThenElse）、混合模式
- **输出**：将结果导出为纹理资产或渲染目标

该插件特别针对 **MetaHuman 烘焙** 等场景进行了优化（从 commit 记录可见），支持异步渲染和导出，以及 Blob 缓存系统来提升性能。

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

---

## 使用场景

- 你需要在引擎内**程序化生成纹理**（如噪声、渐变、图案），不想依赖 Substance Designer 等外部工具
- 你在做 **MetaHuman 或角色定制系统**，需要动态烘焙和生成纹理贴图
- 你需要创建**可参数化的纹理生成管线**，通过蓝图暴露输入参数，运行时动态生成纹理
- 你需要批量处理纹理（模糊、调整亮度、通道重排等），并希望以可视化节点图的方式组织处理流程
- 你需要将节点图生成的纹理**异步导出为资产文件**

---

## 蓝图用法

TextureGraph 提供了异步蓝图节点用于渲染和导出纹理图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TG_AsyncRenderTask` | 异步渲染纹理图，完成后返回渲染目标数组 | `UTG_AsyncRenderTask` |
| `TG_AsyncExportTask` | 异步导出纹理图，支持覆盖、保存、全量导出等选项 | `UTG_AsyncExportTask` |

### 使用示例（蓝图描述）

**异步渲染纹理图**：

1. 获取一个 `UTextureGraphBase` 对象引用（你的 TextureGraph 资产）
2. 调用 `Texture Graph Render (Async)` 节点，传入 TextureGraph 资产
3. 连接 `OnDone` 委托，该委托会返回 `TArray<UTextureRenderTarget2D*>`，即所有输出的渲染目标
4. 在 `OnDone` 回调中使用渲染目标（如赋值给材质参数、转为纹理等）

**异步导出纹理图**：

1. 调用 `Texture Graph Export (Async)` 节点
2. 参数包括：TextureGraph 资产、是否覆盖纹理（OverwriteTextures）、是否保存（bSave）、是否导出全部（bExportAll）、是否禁用缓存（bDisableCache）
3. 连接 `OnDone` 委托等待导出完成

---

## C++ 用法

### 头文件引入

```cpp
#include "TextureGraph.h"
#include "TG_HelperFunctions.h"
#include "TG_Graph.h"
#include "TG_Texture.h"
```

### 基本用法：同步渲染纹理图

```cpp
#include "TextureGraph.h"
#include "TG_HelperFunctions.h"

// 假设已有 UTextureGraphBase* TextureGraphAsset
UTextureGraphBase* TextureGraphAsset = /* ... */;

// 初始化渲染批次
JobBatchPtr Batch = FTG_HelperFunctions::InitRenderBatch(TextureGraphAsset);

// 同步等待渲染完成
// ActivateBlocking 会阻塞当前线程直到渲染完成
// 返回值是输出的渲染目标数组
```

### 基本用法：异步导出纹理

```cpp
#include "TG_HelperFunctions.h"

UTextureGraphBase* TextureGraphAsset = /* ... */;
FString ExportPath = TEXT("/Game/ExportedTextures");
FString AssetName = TEXT("MyTexture");
FExportSettings ExportSettings;

// 异步导出，返回 AsyncInt（可等待的异步结果）
AsyncInt Result = FTG_HelperFunctions::ExportAsync(
    TextureGraphAsset,
    ExportPath,
    AssetName,
    ExportSettings,
    /*OverrideExportPath=*/ true,
    /*OverwriteTextures=*/ true,
    /*ExportAllOutputs=*/ false,
    /*bSave=*/ true
);
```

### 进阶用法：使用 Helper 函数获取节点输出

```cpp
#include "TG_HelperFunctions.h"

// 获取某个节点的所有纹理输出
const UTG_Node* SomeNode = /* ... */;
TArray<BlobPtr> Outputs = FTG_HelperFunctions::GetTexturedOutputs(SomeNode);

// 获取特定类型的输出
TArray<FTG_Texture> TextureOutputs = FTG_HelperFunctions::GetOutputsOfType<FTG_Texture>(SomeNode);
```

---

## 节点图系统详解

TextureGraph 的核心是基于 **Expression（表达式）** 的节点图系统。每个节点都是 `UTG_Expression` 的子类，通过 Pin（引脚）连接形成数据流图。

### 节点分类总览

| 分类 | 说明 | 代表节点 |
|---|---|---|
| **Input** | 输入参数节点，自动暴露为图参数 | Texture, Scalar, Color, Vector, Bool, String, TexturePath, TextureDescriptor, OutputSettings, MaterialFunction |
| **Output** | 输出节点，将数据标记为图输出 | Output |
| **Channel** | 通道操作 | ChannelSplitter, ChannelCombiner, ChannelSwizzle |
| **Filter** | 图像滤镜 | Blur, EdgeDetect, ErodeDilate, Warp, Threshold |
| **Adjustment** | 图像调整 | Grayscale, Premult, NormalFromHeightMap, Brightness |
| **Maths** | 数学运算 | Blend, Invert, IfThenElse |
| **Arrays** | 数组操作 | Array4, ArrayGrid |
| **Utilities** | 工具节点 | MaterialID |

### 输入节点详解

#### Texture（纹理输入）

加载现有纹理资产，自动暴露为图输入参数。

```cpp
// 属性
UPROPERTY(EditAnywhere, Setter, BlueprintReadWrite)
TObjectPtr<UTexture> Source;        // 纹理资产引用

UPROPERTY(EditAnywhere, Setter)
FTG_Texture Texture;                // 纹理数据

// 输出
UPROPERTY(meta = (TGType = "TG_Output"))
FTG_Texture Output;                 // 输出纹理
```

#### Scalar / Color / Vector / Bool / String

基础类型输入参数，均继承自 `UTG_Expression_InputParam`，支持在参数和常量之间切换：

```cpp
// 所有输入参数节点都有这个属性
UPROPERTY(Setter)
bool bIsConstant = false;  // true 时为常量，false 时暴露为图参数
```

#### TexturePath（纹理路径）

从文件路径或目录加载纹理。如果路径是目录，则加载目录下所有纹理。

```cpp
UPROPERTY(EditAnywhere, BlueprintReadWrite)
FString Path;  // 文件路径或目录路径

UPROPERTY(meta = (TGType = "TG_Output"))
FTG_VariantArray Output;  // 输出纹理数组
```

#### TextureDescriptor（纹理描述符）

自定义纹理设置（分辨率、格式、sRGB 等）。

```cpp
UPROPERTY(EditAnywhere) int32 Width = 2048;
UPROPERTY(EditAnywhere) int32 Height = 2048;
UPROPERTY(EditAnywhere) bool bIsSRGB = false;
UPROPERTY(EditAnywhere) ETG_TextureFormat Format = ETG_TextureFormat::Auto;
```

#### MaterialFunction（材质函数）

将材质函数渲染为纹理，支持 Virtual Texture 预热帧数设置。

```cpp
UPROPERTY(EditAnywhere, BlueprintReadWrite)
TObjectPtr<UMaterialFunctionInterface> MaterialFunction;

UPROPERTY(EditAnywhere, BlueprintReadWrite)
int32 NumWarmupFrames = 0;  // VT 预热帧数，0 使用 CVar 默认值
```

### 通道操作节点

#### ChannelSplitter（通道拆分）

将 RGBA 图像拆分为独立的 R、G、B、A 通道。

#### ChannelCombiner（通道合并）

将独立的 R、G、B、A 通道合并为 RGBA 图像。

#### ChannelSwizzle（通道重排）

重新排列通道映射，支持自定义每个输出通道的来源。

```cpp
UPROPERTY(EditAnywhere, BlueprintReadWrite)
EColorChannel RedChannel = EColorChannel::Red;

UPROPERTY(EditAnywhere, BlueprintReadWrite)
EColorChannel GreenChannel = EColorChannel::Green;

UPROPERTY(EditAnywhere, BlueprintReadWrite)
EColorChannel BlueChannel = EColorChannel::Blue;

UPROPERTY(EditAnywhere, BlueprintReadWrite)
EColorChannel AlphaChannel = EColorChannel::Alpha;
```

### 滤镜节点

#### Blur（模糊）

支持三种模糊类型：高斯、方向、径向。

```cpp
UPROPERTY(EditAnywhere) int32 Radius = 1;           // 模糊半径
UPROPERTY(EditAnywhere) float Angle = 0.0f;          // 方向角度
UPROPERTY(EditAnywhere) float Strength = 0.1f;       // 强度
UPROPERTY(EditAnywhere) EBlurType BlurType = EBlurType::Gaussian;
```

#### EdgeDetect（边缘检测）

检测输入图像中的边缘区域（颜色突变区域）。

```cpp
UPROPERTY(EditAnywhere) float Thickness = 1;  // 边缘厚度
```

#### ErodeDilate（膨胀/腐蚀）

对图像进行形态学膨胀或腐蚀操作。

```cpp
UPROPERTY(EditAnywhere) int32 Size = 2;                              // 核大小
UPROPERTY(EditAnywhere) EErodeDilateKernelType Kernel = Box;         // 核类型：Box/Circular/Diamond
UPROPERTY(EditAnywhere) EErodeOrDilate Type = Erode;                 // 膨胀或腐蚀
```

#### Warp（扭曲）

支持方向扭曲和正弦波扭曲。

```cpp
UPROPERTY(EditAnywhere) EWarp::Type Type = EWarp::Directional;
UPROPERTY(EditAnywhere) float Intensity = 1;    // 扭曲强度
UPROPERTY(EditAnywhere) float Angle = 0;         // 方向角度
UPROPERTY(EditAnywhere) float PhaseU = 0.0f;     // U 方向相位
UPROPERTY(EditAnywhere) float PhaseV = 0.0f;     // V 方向相位
```

#### Threshold（阈值）

将图像转为黑白，亮度大于阈值的像素为白色，否则为黑色。

```cpp
UPROPERTY(EditAnywhere) float Threshold;  // 阈值 [0, 1]
```

### 调整节点

#### Grayscale（灰度化）

将输入图像转换为单通道灰度图。

#### Premult（预乘 Alpha）

将 RGB 通道与 Alpha 通道预乘，Alpha 保持不变。

#### NormalFromHeightMap（高度图转法线）

从高度图生成法线贴图。

```cpp
UPROPERTY(EditAnywhere) float Offset = 0.002;    // 采样偏移
UPROPERTY(EditAnywhere) float Strength = 1;       // 法线强度
```

#### Brightness（亮度/对比度）

调整图像的亮度和对比度。

```cpp
UPROPERTY(EditAnywhere) float Brightness = 0;  // 亮度 [-1, 1]
UPROPERTY(EditAnywhere) float Contrast = 1;    // 对比度 [0, 10]
```

### 数学节点

#### Blend（混合）

支持多种混合模式，带遮罩和不透明度控制。

```cpp
UPROPERTY(EditAnywhere) EBlendModes::Type BlendMode = EBlendModes::Normal;
UPROPERTY(EditAnywhere) float Opacity = 1.0;
UPROPERTY(EditAnywhere) bool bIgnoreAlpha = true;
UPROPERTY(EditAnywhere) bool bClamp = true;
```

输入：Foreground（前景）、Background（背景）、Mask（遮罩）

#### Invert（反转）

计算 `MaxValue - Input`，即颜色反转。

```cpp
UPROPERTY(EditAnywhere) bool IncludeAlpha = false;  // 是否反转 Alpha
UPROPERTY(EditAnywhere) bool Clamp = false;          // 是否钳制到 [0,1]
```

#### IfThenElse（条件选择）

根据比较结果选择 Then 或 Else 输出。

```cpp
UPROPERTY(EditAnywhere) EIfThenElseOperator Operator = GT;       // 比较运算符
UPROPERTY(EditAnywhere) EIfThenElseType ComparisonType = IndividualComponent;  // 比较方式
```

输入：LHS（左值）、RHS（右值）、Then（真值）、Else（假值）

### 数组节点

#### Array4

将 4 个输入组合为数组。

#### ArrayGrid

将纹理数组排列为 M×N 网格。

```cpp
UPROPERTY(meta = (TGType = "TG_Input")) int32 Rows = 0;       // 行数（0=自动）
UPROPERTY(meta = (TGType = "TG_Input")) int32 Columns = 0;    // 列数（0=自动）
UPROPERTY(meta = (TGType = "TG_Input")) FLinearColor BackgroundColor = FLinearColor::Transparent;
```

### 输出节点

#### Output

将输入标记为图输出，可导出为纹理资产。

```cpp
UPROPERTY(meta = (TGType = "TG_Input"))
FTG_Variant Source;                    // 输入数据

UPROPERTY(meta = (TGType = "TG_OutputParam"))
FTG_Variant Output;                    // 输出值

UPROPERTY(EditAnywhere)
FTG_OutputSettings OutputSettings;     // 输出设置（分辨率、格式等）
```

---

## Demo 示例

### 最小示例：异步渲染 TextureGraph 并获取结果

**MyTextureGraphUser.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TG_AsyncRenderTask.h"
#include "MyTextureGraphUser.generated.h"

class UTextureGraphBase;
class UTextureRenderTarget2D;

UCLASS()
class AMyTextureGraphUser : public AActor
{
    GENERATED_BODY()

public:
    AMyTextureGraphUser();

    // 在蓝图或编辑器中指定 TextureGraph 资产
    UPROPERTY(EditAnywhere, Category = "TextureGraph")
    TObjectPtr<UTextureGraphBase> TextureGraphAsset;

    // 渲染完成后获取的结果
    UPROPERTY(VisibleAnywhere, Category = "TextureGraph")
    TArray<UTextureRenderTarget2D*> RenderResults;

    // 开始异步渲染
    UFUNCTION(BlueprintCallable, Category = "TextureGraph")
    void StartRender();

private:
    UFUNCTION()
    void OnRenderComplete(const TArray<UTextureRenderTarget2D*>& OutputRts);
};
```

**MyTextureGraphUser.cpp**

```cpp
#include "MyTextureGraphUser.h"
#include "TG_AsyncRenderTask.h"
#include "TG_HelperFunctions.h"

AMyTextureGraphUser::AMyTextureGraphUser()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTextureGraphUser::StartRender()
{
    if (!TextureGraphAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("TextureGraphAsset is null"));
        return;
    }

    // 创建异步渲染任务
    UTG_AsyncRenderTask* RenderTask = UTG_AsyncRenderTask::TG_AsyncRenderTask(TextureGraphAsset);

    // 绑定完成回调
    RenderTask->OnDone.AddDynamic(this, &AMyTextureGraphUser::OnRenderComplete);

    // Activate 会自动开始异步渲染
    // 任务生命周期由 FTG_AsyncTaskManager 管理
}

void AMyTextureGraphUser::OnRenderComplete(const TArray<UTextureRenderTarget2D*>& OutputRts)
{
    RenderResults = OutputRts;

    UE_LOG(LogTemp, Log, TEXT("TextureGraph render complete. Got %d render targets."), OutputRts.Num());

    // 在这里使用渲染结果，例如：
    // - 赋值给材质参数
    // - 转换为 UTexture2D
    // - 保存到磁盘
}
```

---

## 模块依赖

从源码头文件推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `Materials` | 材质函数集成（`UMaterialFunctionInterface`、`UMaterialInterface`） |
| `RenderCore` | 渲染核心（纹理渲染管线） |
| `RHI` | 渲染硬件接口 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：该插件包含两个第三方外部模块 `Continuable` 和 `Function2`，提供异步编程支持（类似 C++ 的 futures/promises 和函数式编程工具）。

---

## 子模块架构

作为 xlarge 插件（782 个源文件），TextureGraph 由以下子模块组成：

| 模块 | 类型 | 职责 |
|---|---|---|
| **TextureGraph** | Runtime | 核心运行时模块，包含表达式节点、图系统、数据类型定义 |
| **TextureGraphEngine** | Runtime | 引擎核心，包含 Job 系统、Blob 数据管理、材质渲染管线 |
| **TextureGraphEditor** | Runtime | 编辑器集成，节点图编辑器 UI、属性面板自定义 |
| **TextureGraphInsight** | Runtime | 调试和分析工具运行时 |
| **TextureGraphInsightEditor** | Runtime | 调试工具的编辑器 UI |
| **Continuable** | External | 第三方异步编程库（类似 futures/promises） |
| **Function2** | External | 第三方高性能函数对象库 |

### 核心数据类型

| 类型 | 说明 |
|---|---|
| `FTG_Texture` | 纹理数据包装，TextureGraph 内部的纹理表示 |
| `FTG_Variant` | 通用变体类型，可存储标量、向量、纹理等 |
| `FTG_VariantArray` | 变体数组 |
| `FTG_TextureDescriptor` | 纹理描述符（分辨率、格式、sRGB 等） |
| `FTG_OutputSettings` | 输出设置 |
| `FTG_Material` | 材质引用包装 |
| `FTG_Hash` | 哈希值类型 |
| `BlobPtr` / `TiledBlobPtr` | 数据 Blob 指针，用于高效纹理数据传输 |

### 关键系统

- **Job 系统**（`JobBatch`）：管理纹理生成任务的调度和执行
- **Blob 系统**：高效的数据传输和缓存机制
- **Async Task Manager**：管理异步任务生命周期，防止任务被过早销毁
- **Export 系统**：将生成的纹理导出为资产文件

---

## 维护状态

### 近期更新

```
- 6a2920da3c25 Fix for crash when cooking TG assets for MH
- c9825f7f0d79 [TG] optimization of the MaterialBase expression which consumes less memory in MetaHuman baking use case
- 563b73821a65 TG Export crash fix
```

### 维护评价

- **创建时间**：2023-12-20，约 2 年历史
- **版本状态**：`VersionName: "1.0 Beta"`，仍处于 Beta 阶段
- **默认启用**：否（`EnabledByDefault: false`），需要手动启用
- **近期活动**：最近的 commit 集中在 MetaHuman 烘焙场景的优化和崩溃修复，表明该插件仍在**活跃维护**中
- **代码规模**：782 个源文件，属于大型插件，架构成熟
- **已知限制**：
  - Beta 版本，API 可能发生变化
  - 需要手动启用
  - 部分功能可能与 MetaHuman 工作流紧密耦合

**综合评价**：✅ **推荐使用**（Beta 阶段但活跃维护）。该插件是 Epic 官方维护的程序化纹理生成工具，特别适合 MetaHuman 相关工作流。虽然标记为 Beta，但代码量大、架构完整，且持续有 bug 修复和性能优化。建议在生产环境中谨慎使用，关注版本更新。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph)
- 官方文档（无）