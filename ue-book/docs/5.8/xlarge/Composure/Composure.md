# Legacy Composure

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 中文名 | 旧版合成系统 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure) | |

## 用途

Composure 是一个完整的实时合成框架，旨在将虚幻引擎打造成一个强大的节点式合成器。它允许用户在引擎内创建复杂的合成管线，将 CG 元素、媒体输入（如摄像机信号或视频文件）、后处理效果和变换操作组合在一起，生成最终输出。该插件为虚拟制作（Virtual Production）和实时视觉效果（In-Camera VFX）提供核心功能，解决了在引擎内进行高质量、可扩展合成的需求。

尽管 `.uplugin` 的 Description 指出这是一个“遗留系统”且不再开发，但从其庞大的源码和功能来看，它仍然是一个功能完备且在引擎内广泛使用的系统。对于需要在引擎内进行合成的工作流，理解此插件至关重要。

## 使用场景

- **虚拟制作 (Virtual Production)**：将摄像机实时画面与 CG 场景、LED 墙背景进行合成，实现沉浸式拍摄。
- **实时色度键合成 (Live Chroma Keying)**：实时去除绿幕/蓝幕背景，将演员合成到虚拟环境中。
- **多层渲染合成**：将渲染通道（如 CG 层、遮罩层、特效层）分开渲染，再通过节点图进行混合与合成，实现复杂的后期效果。
- **通过 Sequencer 导出合成层**：利用 Sequencer 动画系统，导出带有特定通道（如深度、法线）的中间结果，用于后期合成软件。

## 蓝图用法

Composure 提供了丰富的蓝图 API，用于管理和驱动合成管线。核心逻辑围绕着 `ACompositingElement`（合成元素）及其通道（Pass）展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateComposureElement` | 创建一个新的合成元素（Actor） | `UComposureBlueprintLibrary` |
| `GetComposureElement` | 按名称获取场景中的合成元素 | `UComposureBlueprintLibrary` |
| `DeleteComposureElementAndChildren` | 删除一个合成元素及其所有子元素 | `UComposureBlueprintLibrary` |
| `AttachComposureElement` | 将一个元素作为子元素附加到另一个元素 | `UComposureBlueprintLibrary` |
| `RequestNamedRenderTarget` | 请求一个命名的渲染目标，用于内部通道渲染 | `ACompositingElement` |
| `FindTransformPass` | 查找特定类型的变换通道 | `ACompositingElement` |
| `RenderCompElement` | 触发合成元素进行一帧的渲染 | `ACompositingElement` |

### 使用示例（蓝图描述）

1.  **创建一个简单的 CG 合成层**：
    *   使用 `CreateComposureElement` 节点，在场景中创建一个名为 `MyCGLayer` 的 `ACompositingCaptureBase` 类型的元素。
    *   在该元素的细节面板中，配置其 `Input`（如使用场景捕获）、`Transform`（如添加一个材质通道来调整颜色）和 `Output`（如输出到渲染目标）。

2.  **在蓝图中驱动合成**：
    *   将 `MyCGLayer` 元素的引用拖入蓝图。
    *   在事件图表（EventGraph）中，例如在 `Tick` 或自定义事件中，调用 `MyCGLayer` 的 `RenderCompElement` 节点来更新其渲染结果。
    *   通过 `GetLatestRenderResult` 获取渲染后的纹理，用于后续逻辑或显示在 UI 上。

## C++ 用法

### 头文件引入

```cpp
#include "CompositingElement.h"
#include "ComposureBlueprintLibrary.h"
```

### 基本用法

以下代码演示了如何在 C++ 中创建并配置一个简单的合成元素。

```cpp
// 假设在某个 Actor 或 GameMode 的 BeginPlay 中
UWorld* World = GetWorld();
if (World)
{
    // 1. 创建一个合成元素
    ACompositingElement* NewCompElement = UComposureBlueprintLibrary::CreateComposureElement(
        FName("MyCPPElement"),
        ACompositingCaptureBase::StaticClass(),
        nullptr // Level Context, 使用默认关卡
    );

    if (NewCompElement)
    {
        // 2. 设置其渲染分辨率
        NewCompElement->SetRenderResolution(FIntPoint(1920, 1080));

        // 3. 手动添加一个材质变换通道
        UCompositingElementMaterialPass* MaterialPass = NewCompElement->AddNewPass<UCompositingElementMaterialPass>(FName("ColorCorrectionPass"));
        if (MaterialPass)
        {
            // 假设我们有一个调整亮度的材质
            UMaterialInterface* BrightnessMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_BrightnessAdjust"));
            MaterialPass->Material.Material = BrightnessMat;
        }

        // 4. 在下一帧触发渲染
        NewCompElement->RenderCompElement(false);
    }
}
```
*代码灵感来源于 `ACompositingElement` 的通道管理 API 和 `UComposureBlueprintLibrary` 的创建函数。*

### 进阶用法

合成管线的核心是通道（Pass）的组合与数据传递。以下示例展示了如何将一个通道的输出结果作为另一个通道的输入。

```cpp
// 在某个合成元素的上下文中 (例如重写其蓝图事件)
ACompositingElement* MyElement = ...;
// 获取某个输入通道的结果
UTexture* InputTexture = nullptr;
UCompositingElementInput* MediaInput = MyElement->FindInputPass(UMediaTextureCompositingInput::StaticClass(), InputTexture);
// 获取某个材质变换通道
UCompositingElementMaterialPass* CompositePass = ...;

if (InputTexture && CompositePass)
{
    // 假设我们的材质有一个名为 “BaseLayer” 的纹理参数
    // 将输入通道的结果设置给这个材质参数
    CompositePass->Material.SetTextureOverride(FName("BaseLayer"), InputTexture);
    // 标记材质参数已修改
    CompositePass->Material.MarkDirty();
}
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何在运行时创建一个包含输入和输出的简单合成管线。

**ComposureDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ComposureDemoActor.generated.h"

class ACompositingElement;
class UCompositingElementMaterialPass;

UCLASS()
class AComposureDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AComposureDemoActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY(Transient)
	TObjectPtr<ACompositingElement> CompElement;

	UPROPERTY(Transient)
	TObjectPtr<UCompositingElementMaterialPass> MaterialPass;
};
```

**ComposureDemoActor.cpp**
```cpp
#include "ComposureDemoActor.h"
#include "CompositingElement.h"
#include "CompositingElements/CompositingElementPasses.h"
#include "CompositingElements/CompositingElementTransforms.h"
#include "ComposureBlueprintLibrary.h"

AComposureDemoActor::AComposureDemoActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AComposureDemoActor::BeginPlay()
{
	Super::BeginPlay();

	UWorld* World = GetWorld();
	if (!World) return;

	// 创建合成元素
	CompElement = UComposureBlueprintLibrary::CreateComposureElement(
		FName("DemoElement"),
		ACompositingElement::StaticClass(), // 使用基础类，手动添加通道
		GetLevel()
	);

	if (!CompElement) return;

	// 设置渲染分辨率
	CompElement->SetRenderResolution(FIntPoint(512, 512));

	// 添加一个材质变换通道 (示例：使用引擎默认材质)
	MaterialPass = CompElement->AddNewPass<UCompositingElementMaterialPass>(FName("DefaultMaterialPass"));
	if (MaterialPass)
	{
		MaterialPass->Material.Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial"));
	}

	// 添加一个输出通道，输出到渲染目标
	URenderTargetCompositingOutput* OutputPass = CompElement->AddNewPass<URenderTargetCompositingOutput>(FName("OutputPass"));
	if (OutputPass)
	{
		// 可以创建一个新的 RT 或使用现有的
		OutputPass->RenderTarget = NewObject<UTextureRenderTarget2D>(this);
		OutputPass->RenderTarget->InitAutoFormat(512, 512);
	}
}

void AComposureDemoActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (CompElement)
	{
		// 每帧驱动合成元素渲染
		CompElement->RenderCompElement(false);
	}
}
```

## 模块依赖

由于用户未提供 `Build.cs` 文件内容，无法给出精确的依赖列表。通常，要使用 Composure 功能，你的模块需要依赖 `Composure` 模块本身。更具体的功能（如媒体输入）可能需要额外依赖 `MediaAssets`、`MediaUtils` 等。

**建议**：在你的模块 `.Build.cs` 文件中添加以下依赖（根据实际使用情况调整）：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "Composure" // 核心合成模块
    // 根据需要添加: "MediaAssets", "MediaUtils", "RenderCore", "Renderer" 等
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口代码重构：通过客户端关联/解关联通知来移除重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退 CL53913857 的改动。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏。 |
| 2026-04-13 | `efbf4c0b` | Viewport: Use managed pointer for reference to Client | 视口代码：使用托管指针管理客户端引用。 |

### 维护评价

**综合评价：维护不活跃的遗留系统**
- **创建时间**：2017年6月，历史相当悠久。
- **最近更新**：最近的更新（2026年）都是底层视口代码的重构和日志宏迁移，并没有针对合成系统本身的新功能或重要修复。这表明核心合成功能已经稳定，近期维护主要针对引擎基础架构的适配。
- **活跃度**：插件已被官方标记为“Legacy”（遗留），意味着它不再进行主要开发，其功能将由新的 `Composure` 插件（非此目录下的）继承。当前版本主要进行兼容性维护。
- **已知限制**：作为遗留系统，它可能无法利用最新的渲染技术或 API。其蓝图编辑器工具链（ComposureLayersEditor）可能不如新系统完善。
- **使用建议**：对于新项目，应优先考虑使用引擎内置的新版 Composure（如果存在且功能满足需求）。对于维护已有项目或特定功能依赖此旧版本的情况，它仍然是一个可靠、功能完整的解决方案。由于其长期稳定，Bug 相对较少。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure)
- **官方文档**：无（`DocsURL` 字段为空）
- **测试用例**：从源码提交记录看，测试代码位于 `EngineTests` 中，但具体路径未提供。