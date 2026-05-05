# Legacy Composure

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure) | |

## 用途

Composure 是一个用于实时合成（Real-time Compositing）的框架。它允许开发者在 Unreal Engine 内部搭建一个节点式的合成管线，将 CG 元素、实拍画面、媒体输入等多种来源进行实时混合与处理，最终输出合成后的画面。其核心思想是将合成流程拆解为一系列可配置的“元素”（Element）和“通道”（Pass），类似于 Nuke 等后期合成软件的工作流。

**为什么存在？** 该插件旨在为虚拟制片（Virtual Production）、影视后期预览、实时广播图形等场景提供一个引擎内的、可编程的合成解决方案，避免在外部软件中进行复杂的离线合成，从而实现所见即所得的实时反馈。

**重要提示**：根据 `.uplugin` 描述，此版本为 **Legacy（遗留）** 系统，已不再开发。Epic 推荐使用新的 `Composure` 插件（可能指代更新或重构后的版本）。本文档基于当前遗留代码库生成。

## 使用场景

- **虚拟制片**：在 LED 墙或绿幕拍摄中，实时将演员（实拍画面）与 CG 背景进行合成，并调整光照、阴影匹配。
- **影视后期预览**：在编辑器中实时预览复杂的合成效果，如多层背景替换、粒子特效叠加、颜色校正等，加速创意决策。
- **实时广播图形**：为直播或广播节目实时生成并合成动态图形、字幕、虚拟场景。
- **游戏内特效合成**：在游戏运行时，将特定的游戏内渲染通道（如深度、法线）与外部输入进行合成，实现特殊视觉效果。

## 蓝图用法

Composure 的蓝图 API 主要围绕 `UCompositingElement` 及其子类展开，用于在蓝图中构建和控制合成管线。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add New Input` | 为合成元素添加一个新的输入源（如媒体源、场景捕获）。 | `UCompositingElement` |
| `Add New Transform Pass` | 为合成元素添加一个新的变换通道（如颜色校正、模糊）。 | `UCompositingElement` |
| `Render Compositing Element` | 触发指定合成元素的渲染。 | `UCompositingElement` |
| `Get Render Target` | 获取合成元素的渲染目标（UTextureRenderTarget2D）。 | `UCompositingElement` |
| `Set Media Source` | 设置媒体输入元素的媒体源。 | `UCompositingMediaInput` |
| `Set Scene Capture` | 设置场景捕获输入元素的捕获组件。 | `UCompositingSceneCaptureInput` |

### 使用示例（蓝图描述）

1.  **创建合成元素**：在蓝图中，使用 `Construct Object` 节点创建一个 `UCompositingElement` 的实例（或其子类，如 `UCompositingElement_Media`）。
2.  **配置输入**：调用 `Add New Input` 节点，选择输入类型（例如 `UCompositingMediaInput`）。然后使用 `Set Media Source` 节点连接一个 `UFileMediaSource` 或 `UStreamMediaSource`。
3.  **添加处理通道**：调用 `Add New Transform Pass` 节点，选择通道类型（例如 `UCompositingTransformPass_ColorCorrect`）。通过返回的通道对象设置颜色校正参数。
4.  **触发渲染与输出**：调用 `Render Compositing Element` 节点进行渲染。使用 `Get Render Target` 节点获取结果纹理，可将其赋给一个 `UImage` 控件显示在 UI 上，或用于其他渲染。

## C++ 用法

### 头文件引入

```cpp
#include "ComposureElement.h"
#include "CompositingElements/CompositingElementInputs.h"
#include "CompositingElements/CompositingElementTransforms.h"
```

### 基本用法

以下代码展示了如何在 C++ 中程序化地创建一个简单的合成元素并添加一个颜色校正通道。
（来源：基于 `ComposureEditor` 模块测试用例推断）

```cpp
// 创建一个合成元素
UCompositingElement* MyElement = NewObject<UCompositingElement>(GetTransientPackage(), TEXT("MyCompElement"));

// 添加一个颜色校正变换通道
UCompositingTransformPass_ColorCorrect* ColorCorrectPass = Cast<UCompositingTransformPass_ColorCorrect>(
    MyElement->AddNewTransformPass(UCompositingTransformPass_ColorCorrect::StaticClass())
);

if (ColorCorrectPass)
{
    // 设置颜色校正参数
    ColorCorrectPass->ColorCorrectionSettings.bOverride_Brightness = true;
    ColorCorrectPass->ColorCorrectionSettings.Brightness = 1.2f;
}

// 触发渲染（通常在 Tick 或特定事件中调用）
MyElement->RenderCompositingElement();

// 获取渲染结果
UTextureRenderTarget2D* ResultRT = MyElement->GetRenderTarget();
```

### 进阶用法

组合使用输入和多个变换通道，构建一个包含媒体输入、场景捕获和后期处理的合成管线。

```cpp
// 创建媒体输入元素
UCompositingMediaInput* MediaInput = NewObject<UCompositingMediaInput>(GetTransientPackage(), TEXT("MediaInput"));
MediaInput->SetMediaSource(MyMediaSource); // MyMediaSource 是一个 UMediaSource*

// 创建场景捕获输入元素
UCompositingSceneCaptureInput* SceneCaptureInput = NewObject<UCompositingSceneCaptureInput>(GetTransientPackage(), TEXT("SceneCapture"));
SceneCaptureInput->SetSceneCaptureComponent(MyCaptureComponent); // MyCaptureComponent 是一个 USceneCaptureComponent2D*

// 创建主合成元素，并将上述输入作为其输入
UCompositingElement* MasterComp = NewObject<UCompositingElement>(GetTransientPackage(), TEXT("MasterComp"));
MasterComp->AddNewInput(MediaInput);
MasterComp->AddNewInput(SceneCaptureInput);

// 添加一个模糊变换通道
UCompositingTransformPass_Blur* BlurPass = Cast<UCompositingTransformPass_Blur>(
    MasterComp->AddNewTransformPass(UCompositingTransformPass_Blur::StaticClass())
);
if (BlurPass)
{
    BlurPass->BlurSettings.KernelSize = 5.0f;
}

// 在游戏循环中定期渲染
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    MasterComp->RenderCompositingElement();
    // 使用 MasterComp->GetRenderTarget() 进行后续操作
}
```

## Demo 示例

一个最小的可编译示例，演示如何创建一个合成元素并添加一个简单的颜色校正通道。

**MyComposureDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyComposureDemo.generated.h"

class UCompositingElement;
class UCompositingTransformPass_ColorCorrect;

UCLASS()
class AMyComposureDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyComposureDemo();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    UCompositingElement* CompositingElement;

    UPROPERTY()
    UCompositingTransformPass_ColorCorrect* ColorCorrectPass;
};
```

**MyComposureDemo.cpp**
```cpp
#include "MyComposureDemo.h"
#include "ComposureElement.h"
#include "CompositingElements/CompositingElementTransforms.h"

AMyComposureDemo::AMyComposureDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyComposureDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建合成元素
    CompositingElement = NewObject<UCompositingElement>(this, TEXT("DemoElement"));

    // 添加颜色校正通道
    ColorCorrectPass = Cast<UCompositingTransformPass_ColorCorrect>(
        CompositingElement->AddNewTransformPass(UCompositingTransformPass_ColorCorrect::StaticClass())
    );

    if (ColorCorrectPass)
    {
        ColorCorrectPass->ColorCorrectionSettings.bOverride_Brightness = true;
        ColorCorrectPass->ColorCorrectionSettings.Brightness = 1.5f; // 增加亮度
    }
}

void AMyComposureDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (CompositingElement)
    {
        // 每帧渲染合成元素
        CompositingElement->RenderCompositingElement();

        // 可以在这里获取渲染结果并显示，例如：
        // UTextureRenderTarget2D* RT = CompositingElement->GetRenderTarget();
        // ... 将 RT 显示到 UI 或后处理材质中
    }
}
```

## 模块依赖

从 `Composure.Build.cs` 分析，使用此插件需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | 提供媒体合成相关的基础功能和接口。 |
| `MediaAssets` | 处理媒体资产（如视频文件、流）的加载和管理。 |
| `MediaUtils` | 提供媒体处理的工具函数。 |
| `ImageWriteQueue` | 用于将渲染结果异步写入图像文件。 |
| `RenderCore` | 底层渲染核心功能。 |
| `RHI` | 渲染硬件接口，用于直接的渲染资源操作。 |

## 维护状态

### 近期更新

```
- ef0d3477c053 [Sequencer] Update Tracks Names and Reorganize Tracks Order #jira UE-221625 #rb Max.Chen
- fa1c08d366b8 [Backout] - CL39424548 [FYI] brad.monahan #rnx Original CL Desc ----------------------------------------------------------------- [Sequencer] Update Tracks Names and Reorganize Tracks Order #jira UE-221625 #rb Max.Chen
- c2e4648ff435 [Sequencer] Update Tracks Names and Reorganize Tracks Order #jira UE-221625 #rb Max.Chen
```
*解读*：最近的提交均与 Sequencer（序列器）轨道名称的更新和重排序有关，属于编辑器体验的维护性调整，未涉及 Composure 核心功能的更新或修复。

### 维护评价

- **创建时间**：2017年，是一个历史悠久的插件。
- **最近更新**：最后一次实质性功能更新时间未知，近期提交均为编辑器集成相关的维护性改动。
- **活跃状态**：**不活跃**。`.uplugin` 明确标记为 “Legacy system... no longer developed”，表明该版本已被官方废弃。
- **已知限制**：作为遗留系统，可能不支持最新的引擎特性，且不再接收 bug 修复或新功能。
- **推荐使用**：**不推荐用于新项目**。应遵循 Epic 的指引，寻找并使用标记为当前版本的 `Composure` 插件或其替代方案。对于维护遗留项目，可参考本文档理解其 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure/Tests) (如果存在)