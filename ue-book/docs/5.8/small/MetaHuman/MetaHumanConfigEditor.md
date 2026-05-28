# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-06-12 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman 角色提供的官方动画工具包。它不仅仅是一个“动画编辑器”，而是一个完整的、以表演驱动的 MetaHuman 面部动画流水线。这个插件的核心目的是让用户能够使用 iPhone、深度相机或音频文件作为输入源，快速、高质量地创建出逼真的 MetaHuman 面部动画。

插件解决的主要问题包括：
1.  **面部动画采集**：提供从移动设备（如 iPhone 的 TrueDepth 相机）或其他深度传感器捕获面部运动数据的能力。
2.  **面部追踪与解算**：包含复杂的算法（面部轮廓追踪器、动画解算器），能够从捕获的视频或深度数据中精确地提取面部肌肉运动参数（控制点）。
3.  **身份与动画绑定**：通过 MetaHuman Identity 系统，将提取的面部动画数据应用到特定的 MetaHuman 角色模型上，驱动其骨骼动画。
4.  **语音驱动动画**：支持从音频文件生成面部动画。
5.  **批处理与流水线**：提供批处理工具，方便对大量表演数据进行自动化处理。
6.  **编辑器集成**：为 Unreal Editor 提供一整套自定义 UI（如细节面板自定义、资产浏览器），无缝地集成动画创建工作流。

简而言之，它的存在是为了将 MetaHuman 角色从一个静态的数字人模型，转变为一个能够表演、有真实感动画的角色，大幅降低创建高质量数字人动画的门槛和成本。

## 使用场景

-   **数字人内容创作**：你正在制作一个数字人主播、虚拟偶像或数字人客服。你需要通过手机录制演员的表演，然后快速生成该表演驱动 MetaHuman 模型的动画。→ 使用 **MetaHuman Animator**
-   **影视预演与视觉特效**：在影视制作中，你需要快速生成角色面部动画作为预览，或者将现场表演数据应用到数字替身上。→ 使用 **MetaHuman Animator**
-   **游戏开发**：你需要为游戏中的过场动画或 NPC 对话创建大量逼真的面部表情，特别是需要与音频口型同步时。→ 使用 **MetaHuman Animator** 的 **Speech2Face** 功能
-   **学术研究**：你在研究面部动画、动作捕捉或人机交互，需要一个功能强大的工具来处理深度传感器数据。→ 使用其底层的 **MetaHumanCaptureUtils** 和 **MetaHumanFaceContourTracker** 等模块

## 蓝图用法

MetaHuman Animator 的主要功能通过 `MetaHumanPerformance` 和 `MetaHumanPipeline` 等模块中的类暴露给蓝图。核心工作流是数据驱动的，通常围绕“捕获数据”、“配置资产”、“管线处理”和“生成动画”展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建性能资产` | 从捕获数据（视频、深度序列）创建一个 MetaHuman Performance 资产，这是后续所有处理的基础。 | `UMetaHumanPerformance` |
| `设置动画解算器` | 为 Performance 资产指定用于生成动画的“动画解算器”资产。 | `UMetaHumanPerformance` |
| `设置面部适配器` | 为 Performance 资产指定“面部适配器”资产，用于将动画数据映射到具体 MetaHuman 骨骼上。 | `UMetaHumanPerformance` |
| `生成动画` | 执行最终处理，根据捕获数据、解算器和适配器，生成最终的动画序列。 | `UMetaHumanPerformance` |
| `处理序列` | 触发一个预定义的处理管线（Pipeline）来对数据进行批处理或复杂操作。 | `UMetaHumanPipeline` |
| `设置元数据` | 为捕获数据资产设置关键元数据，如音频文件、场景描述等。 | `UMetaHumanCaptureSource` |

### 使用示例（蓝图描述）

以下是一个基本的蓝图工作流描述，用于从 iPhone 录制的视频生成面部动画：

1.  **创建 Performance 资产**：
    -   在内容浏览器中右键，选择 `Animation > MetaHuman Performance`，创建一个新资产。
    -   在其细节面板中，通过下拉菜单或文件浏览器，指定一个包含人脸视频（如 .mov）和对应音频文件的“捕获源”文件夹。

2.  **配置资产**：
    -   选中刚才创建的 Performance 资产，在细节面板中找到 `Animation Solver` 和 `Face Adapter` 属性。
    -   从内容浏览器中拖入一个合适的 `MetaHumanFaceAnimationSolver` 资产（用于控制如何解算面部）和一个 `MetaHumanIdentity` 资产（用于绑定到具体的 MetaHuman 角色）。

3.  **生成动画**：
    -   在 Performance 资产的细节面板或编辑器工具栏中，找到 `Generate Animation` 或类似按钮并点击。
    -   处理完成后，会在 Performance 资产同目录下生成一个动画序列资产。

## C++ 用法

C++ 用法主要集中在初始化管道、自定义处理步骤以及处理底层捕获数据流上。以下示例展示如何编程式地启动一个处理任务。

### 头文件引入

```cpp
#include "MetaHumanPerformance.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanIdentity.h"
```

### 基本用法

这个示例展示了如何从代码中触发一个 Performance 资产的动画生成过程。

```cpp
// 假设我们已经有了一个 UMetaHumanPerformance 资产的指针
UMetaHumanPerformance* PerformanceAsset = /* 例如通过 LoadObject 或 CreateNewObject 获得 */;

// 1. 确保资产已被初始化并关联了捕获数据
if (PerformanceAsset && PerformanceAsset->IsCaptureDataValid())
{
    // 2. 设置解算器和适配器（如果尚未设置）
    UMetaHumanFaceAnimationSolver* Solver = /* 获取或创建一个解算器资产 */;
    UMetaHumanIdentity* Identity = /* 获取或创建一个身份资产 */;
    
    PerformanceAsset->SetAnimationSolver(Solver);
    PerformanceAsset->SetFaceAdapter(Identity);

    // 3. 启动生成任务（这是异步的）
    PerformanceAsset->GenerateAnimation();
    
    // 4. 可以通过绑定到 PerformanceAsset 的委托来监听完成事件
    // PerformanceAsset->OnAnimationGenerationCompleted.AddDynamic(this, &AMyClass::OnAnimationFinished);
}
```

### 进阶用法：自定义处理管线

MetaHuman Pipeline 模块允许你创建和执行自定义的处理步骤序列。以下是一个概念性示例，展示如何构建一个简单的管线。

```cpp
#include "MetaHumanPipeline.h"

// 定义一个自定义管线步骤
class FMyCustomPipelineStep : public FMetaHumanPipelineStep
{
public:
    virtual bool Process(const FMetaHumanPipelineContext& InContext) override
    {
        // 获取输入数据（例如：原始视频帧）
        const FMediaTextureSample* InputFrame = InContext.GetValue<FMediaTextureSample>(TEXT("InputFrame"));
        
        if (InputFrame)
        {
            // 在这里进行你的自定义处理（例如：应用一个自定义滤镜）
            // ... 处理逻辑 ...
            
            // 将处理后的数据设置为输出
            FMediaTextureSample* ProcessedFrame = /* 处理后的数据 */;
            InContext.SetValue(TEXT("ProcessedFrame"), ProcessedFrame);
            return true;
        }
        return false;
    }
    
    virtual FName GetStepName() const override { return FName(TEXT("MyCustomStep")); }
};

// 在某个 Actor 或 GameInstance 中构建并运行管线
void RunCustomPipeline()
{
    // 创建管线上下文
    FMetaHumanPipelineContext Context;
    Context.SetValue(TEXT("InputVideoPath"), FString("/Game/Captures/MyVideo.mov"));

    // 创建并注册自定义步骤
    TSharedPtr<FMyCustomPipelineStep> MyStep = MakeShared<FMyCustomPipelineStep>();
    
    // 假设有一个管线管理器
    UMetaHumanPipelineManager* PipelineManager = UMetaHumanPipelineManager::Get();
    PipelineManager->RegisterPipelineStep(MyStep);

    // 构建管线序列
    TArray<TSharedPtr<FMetaHumanPipelineStep>> PipelineSteps;
    PipelineSteps.Add(MyStep);
    // 可以添加更多的步骤，例如面部追踪、动画解算等
    
    // 执行管线
    PipelineManager->ExecutePipeline(PipelineSteps, Context);
}
```

## Demo 示例

以下是一个最小化示例，展示如何创建一个简单的 Actor，该 Actor 在被放置到关卡中时，自动加载一个现有的 MetaHuman Performance 资产并提示用户配置它。

```cpp
// MyMetaHumanActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMetaHumanActor.generated.h"

class UMetaHumanPerformance;

UCLASS()
class MYPROJECT_API AMyMetaHumanActor : public AActor
{
    GENERATED_BODY()
    
public:    
    AMyMetaHumanActor();

protected:
    virtual void BeginPlay() override;

    // 在编辑器中指定要加载的 Performance 资产
    UPROPERTY(EditAnywhere, Category="MetaHuman")
    TSoftObjectPtr<UMetaHumanPerformance> PerformanceAssetToLoad;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanPerformance> LoadedPerformanceAsset;

    UFUNCTION()
    void OnPerformanceAssetLoaded();
};
```

```cpp
// MyMetaHumanActor.cpp
#include "MyMetaHumanActor.h"
#include "MetaHumanPerformance.h"
#include "Engine/StreamableManager.h"

AMyMetaHumanActor::AMyMetaHumanActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanActor::BeginPlay()
{
    Super::BeginPlay();

    // 异步加载指定的 Performance 资产
    if (!PerformanceAssetToLoad.IsNull())
    {
        FStreamableManager& StreamableManager = UAssetManager::GetStreamableManager();
        StreamableManager.RequestAsyncLoad(
            PerformanceAssetToLoad.ToSoftObjectPath(),
            FStreamableDelegate::CreateUObject(this, &AMyMetaHumanActor::OnPerformanceAssetLoaded)
        );
    }
}

void AMyMetaHumanActor::OnPerformanceAssetLoaded()
{
    // 加载完成，获取资产指针
    LoadedPerformanceAsset = PerformanceAssetToLoad.Get();
    
    if (LoadedPerformanceAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Performance Asset Loaded: %s"), *LoadedPerformanceAsset->GetName());
        // 在此处可以进一步操作资产，例如检查其状态、显示UI等。
        // 由于大部分配置需要在编辑器UI中进行，这里主要演示加载流程。
    }
}
```

## 模块依赖

要使用 MetaHuman Animator 插件的功能，你的模块通常需要依赖其中的一个或多个特定模块。以下列出了除通用引擎模块外的关键依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanPerformance` | 核心模块，用于管理和生成面部动画。 |
| `MetaHumanIdentity` | 用于定义和管理 MetaHuman 角色的面部身份，是动画绑定的关键。 |
| `MetaHumanFaceAnimationSolver` | 包含面部动画解算算法。 |
| `MetaHumanFaceContourTracker` | 包含从视频/深度数据中追踪面部轮廓的算法。 |
| `MetaHumanPipeline` | 用于构建和执行自定义的数据处理管线。 |
| `MetaHumanCaptureSource` | 提供对捕获数据源（视频、深度序列）的抽象和管理。 |
| `MetaHumanConfig` | 管理插件运行所需的各类配置资产。 |
| `MetaHumanSDKEditor` | 提供编辑器扩展，依赖关系来自 MetaHumanIdentity。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

-   **创建时间**：该插件于 2024 年 6 月首次提交，是一个相对较新的工具集。
-   **更新频率与内容**：最近的更新（2026年5月）非常密集，主要集中在 **修复已知问题**（渲染瑕疵、缓存问题）和 **增强功能/集成**（身体追踪兼容性、动画导出）。这表明插件正处于 **活跃的维护和功能完善期**。
-   **活跃度**：**高度活跃**。更新内容反映了 Epic Games 正在积极将其与 UE5 的最新特性（如身体追踪）以及 MetaHuman 项目的新需求进行整合和适配。
-   **已知限制**：作为官方工具，它与 MetaHuman 角色深度绑定，通用性有限。部分高级功能（如深度数据处理）可能需要特定的硬件支持。
-   **推荐使用**：**强烈推荐**。如果你正在使用 MetaHuman 角色并需要为其创建高质量动画，这是 Epic 官方提供的、最直接、功能最强大的解决方案。它集成了最佳实践，能极大提升工作流效率。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档]()（暂无公开链接，文档可能通过 Epic Games 开发者社区或内部渠道提供）