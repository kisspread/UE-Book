# Legacy Composure

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 中文名 | 遗留合成系统 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure) | |

## 用途

此插件提供了一套在虚幻引擎中进行实时合成的工具集。其核心设计思想是将场景中的不同元素（如3D模型、2D图像、后处理效果）拆分成独立的“合成通道”，并对这些通道进行混合、叠加和后处理，最终在屏幕上输出一个合成结果。它旨在简化虚拟制片、电影预渲染等需要复杂合成的工作流程，通过蓝图和编辑器工具提供直观的操作界面。

然而，根据 .uplugin 的描述，此插件 (`Composure`) 已被标记为**遗留系统**（Legacy System），Epic Games 已停止开发并推荐使用新的 `Composure` 插件。本插件可能仅用于兼容旧有项目或特定工作流。

## 使用场景

- **虚拟制片 (Virtual Production)**：将实时渲染的3D场景与拍摄的实拍素材（作为合成通道输入）进行实时合成预览。
- **电影预渲染 (Pre-visualization)**：快速搭建和预览包含复杂视觉效果（如镜头光晕、粒子、背景板）的镜头。
- **镜头失真校正**：与 `LensDistortion` 插件配合，在合成流水线中应用或移除摄像机镜头畸变。
- **自定义渲染通道管理**：为特定的合成任务（如绿幕抠像、雾气分层）创建独立的渲染通道并进行管理。

## 蓝图用法

插件提供了多个蓝图可调用的核心功能，主要用于创建和操作合成元素及通道。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Output` | 从给定的媒体纹理创建一个合成元素。 | `UComposureBlueprintLibrary` |
| `Set Texture Parameter` | 为指定的后处理材质通道设置纹理参数。 | `UComposureBlueprintLibrary` |
| `Set Pass with Render Target` | 为指定的合成通道设置一个渲染目标作为其输出。 | `UComposureBlueprintLibrary` |
| `Add Input Proxy` | 为合成通道添加一个输入代理，用于获取特定元素的渲染结果。 | `UComposureElement` |
| `Get Element Name` | 获取合成元素的名称。 | `UComposureElement` |
| `Export to Sequence` | 将合成通道的输出导出为序列器中的媒体轨迹。 | `UComposureExportTrack` |

### 使用示例（蓝图描述）

1.  **创建合成通道**：在蓝图中创建一个 `UComposurePass` 的子类（如 `UComposurePostProcessPass`），并将其作为场景中的Actor放置或动态生成。
2.  **设置输入**：通过调用 `Add Input Proxy` 节点，将场景中其他渲染元素（如一个显示3D角色的 `UComposureTransformPass`）的输出连接为当前通道的输入。
3.  **应用后处理**：在通道的材质（Material）中设置好混合逻辑（如Alpha混合），然后使用 `Set Texture Parameter` 节点动态设置该材质所需的纹理。
4.  **输出与查看**：使用 `Set Pass with Render Target` 将最终合成结果输出到一个可查看的渲染目标，或使用 `Export to Sequence` 将其保存为视频序列。

## C++ 用法

插件的核心类如 `UComposureElement`, `UComposurePass` 等通常通过子类化来定义特定的合成行为。以下为基本用法示例。

### 头文件引入

```cpp
#include "ComposureElement.h"
#include "ComposurePass.h"
#include "ComposureBlueprintLibrary.h"
```

### 基本用法

创建一个自定义的合成通道，重写其合成逻辑。

```cpp
// MyCustomComposurePass.h
#pragma once
#include "ComposurePass.h"
#include "MyCustomComposurePass.generated.h"

UCLASS(BlueprintType)
class UMyCustomComposurePass : public UComposurePass
{
    GENERATED_BODY()

public:
    UMyCustomComposurePass();

    // 重写合成函数，实现自定义混合逻辑
    virtual void Composite_Implementation(UTexture* InputA, UTexture* InputB, UComposurePostProcessBlendable* Blendable, FLinearColor ColorTint, FComposurePrePassPolicy PrePassPolicy, UTexture*& Output) override;
};

// MyCustomComposurePass.cpp
#include "MyCustomComposurePass.h"
#include "ComposureBlueprintLibrary.h"
#include "Engine/TextureRenderTarget2D.h"

UMyCustomComposurePass::UMyCustomComposurePass()
{
    // 设置通道所需的材质
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BlendMatFinder(TEXT("/Composure/Materials/M_SimpleBlend"));
    if (BlendMatFinder.Succeeded())
    {
        SetBlendMaterial(BlendMatFinder.Object);
    }
}

void UMyCustomComposurePass::Composite_Implementation(UTexture* InputA, UTexture* InputB, UComposurePostProcessBlendable* Blendable, FLinearColor ColorTint, FComposurePrePassPolicy PrePassPolicy, UTexture*& Output)
{
    // 获取或创建输出渲染目标
    UTextureRenderTarget2D* OutputRT = GetRenderOutput();
    if (!OutputRT)
    {
        OutputRT = UComposureBlueprintLibrary::CreateRenderOutput(this);
        SetRenderOutput(OutputRT);
    }

    // 使用材质实例进行渲染
    if (BlendMaterialInstance && OutputRT)
    {
        BlendMaterialInstance->SetTextureParameterValue(TEXT("InputA"), InputA);
        BlendMaterialInstance->SetTextureParameterValue(TEXT("InputB"), InputB);
        BlendMaterialInstance->SetVectorParameterValue(TEXT("ColorTint"), ColorTint);
        UComposureBlueprintLibrary::SetPassWithRenderTarget(this, BlendMaterialInstance, OutputRT);
    }

    Output = OutputRT;
}
```

### 进阶用法

在运行时动态创建合成通道并将其链接起来。

```cpp
// 在某个Actor或管理器类中
void AMyComposureManager::SetupCompositingPipeline()
{
    // 1. 创建用于显示3D角色的通道
    UComposureTransformPass* TransformPass = NewObject<UComposureTransformPass>(this, TEXT("CharacterPass"));
    TransformPass->SetCaptureActor(CharacterActor);

    // 2. 创建后处理通道
    UMyCustomComposurePass* PostProcessPass = NewObject<UMyCustomComposurePass>(this, TEXT("FXPass"));

    // 3. 将角色通道的输出作为后处理通道的输入A
    PostProcessPass->AddInputProxy(TransformPass, TEXT("InputA"));

    // 4. 将后处理通道的输出设置到屏幕上的某个渲染目标Widget上
    UTexture* FinalOutput = PostProcessPass->GetRenderOutput();
    // ... 将 FinalOutput 传递给 UI Widget 或场景捕获组件进行显示。
}
```

## Demo 示例

一个最小化的 C++ 类，演示如何定义一个执行简单颜色校正的合成通道。

```cpp
// ColorCorrectComposurePass.h
#pragma once
#include "ComposurePass.h"
#include "ColorCorrectComposurePass.generated.h"

UCLASS()
class UColorCorrectComposurePass : public UComposurePass
{
    GENERATED_BODY()

public:
    UColorCorrectComposurePass();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Composure")
    FLinearColor TintColor = FLinearColor::White;

    virtual void Composite_Implementation(UTexture* InputA, UTexture* InputB, UComposurePostProcessBlendable* Blendable, FLinearColor ColorTint, FComposurePrePassPolicy PrePassPolicy, UTexture*& Output) override;
};
```

```cpp
// ColorCorrectComposurePass.cpp
#include "ColorCorrectComposurePass.h"
#include "ComposureBlueprintLibrary.h"
#include "Materials/MaterialInstanceDynamic.h"

UColorCorrectComposurePass::UColorCorrectComposurePass()
{
    // 使用一个简单颜色调整材质
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> MatFinder(TEXT("/Engine/EngineMaterials/DefaultMaterial"));
    if (MatFinder.Succeeded())
    {
        SetBlendMaterial(MatFinder.Object);
    }
}

void UColorCorrectComposurePass::Composite_Implementation(UTexture* InputA, UTexture* InputB, UComposurePostProcessBlendable* Blendable, FLinearColor ColorTint, FComposurePrePassPolicy PrePassPolicy, UTexture*& Output)
{
    UTextureRenderTarget2D* OutputRT = GetRenderOutput();
    if (!OutputRT)
    {
        OutputRT = UComposureBlueprintLibrary::CreateRenderOutput(this);
        SetRenderOutput(OutputRT);
    }

    if (BlendMaterialInstance && OutputRT)
    {
        // 应用颜色校正
        BlendMaterialInstance->SetTextureParameterValue(TEXT("InputA"), InputA);
        BlendMaterialInstance->SetVectorParameterValue(TEXT("TintColor"), TintColor * ColorTint);
        UComposureBlueprintLibrary::SetPassWithRenderTarget(this, BlendMaterialInstance, OutputRT);
    }

    Output = OutputRT;
}
```

## 模块依赖

要使用此插件的功能，你的项目模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Composure` | 核心合成逻辑、元素和通道类 |
| `ComposureEditor` | 编辑器内的合成工具、自定义资产编辑器 |
| `LensDistortion` | 插件隐含依赖，用于处理镜头畸变（在创建时引入） |
| `MovieScene` | 用于集成到 Sequencer 电影序列系统 |
| `MediaUtils` | 用于媒体输入输出相关功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口代码重构，优化客户端关联通知逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了变更 CL53913857。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 同 `cfb610df`，视口相关重构。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统 UE_LOG 迁移到新的 UE_LOGF 宏格式。 |
| 2026-04-13 | `efbf4c0b` | Viewport: Use managed pointer for reference to Client | 在视口中使用智能指针管理 Client 引用，防止野指针。 |

### 维护评价

**可能废弃 / 不推荐用于新项目。**

- **状态**：此插件 (`Composure`) 在 .uplugin 中被明确标记为“Legacy”，并指出“不再开发”（no longer developed），推荐使用新的 `Composure` 插件。
- **活动**：近期的提交（如 2026 年）主要是引擎级别的底层重构（如日志宏迁移、视口代码优化），而非该插件自身功能的改进或修复。
- **风险**：由于官方已停止维护，该插件可能存在未修复的Bug，且与未来虚幻引擎版本的兼容性无法保证。任何新项目都**不应**依赖此插件。
- **建议**：仅在维护需要兼容此遗留系统的旧项目时使用。所有新的合成工作流应迁移到官方推荐的新版 `Composure` 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure/Tests)