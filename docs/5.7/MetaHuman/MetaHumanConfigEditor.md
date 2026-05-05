# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 数字人动画制作核心工具包。它不仅仅是一个简单的插件，而是一个完整的、端到端的面部动画解决方案。其核心目的是将真实的面部表演（来自 iPhone、专业头盔相机或音频）转化为驱动 MetaHuman 角色的高质量动画数据。

该插件解决的核心问题包括：
1.  **面部捕捉与追踪**：从视频源（如 iPhone 的 TrueDepth 相机）中提取面部特征点、轮廓和深度信息。
2.  **动画求解**：将追踪到的面部数据转换为 MetaHuman 骨骼的动画控制曲线（Control Rigs）。
3.  **身份与表演分离**：通过 `MetaHumanIdentity` 资产管理数字人的“身份”（基础网格、纹理），通过 `MetaHumanPerformance` 资产管理“表演”（动画数据），实现身份复用。
4.  **流程自动化**：提供批处理工具 (`MetaHumanBatchProcessor`) 和可配置的处理管线 (`MetaHumanPipeline`)，以标准化和自动化从原始素材到最终动画的流程。
5.  **音频驱动**：集成 `MetaHumanSpeech2Face` 模块，支持仅从音频生成口型动画。

## 使用场景

-   **影视与过场动画制作**：你需要为游戏或影视项目中的 MetaHuman 角色制作大量逼真的面部动画，且表演数据来源于真人演员的 iPhone 拍摄或专业动捕设备。
-   **虚拟主播与实时应用**：你正在开发一个虚拟主播应用，需要将主播的面部表情实时或准实时地映射到 MetaHuman 角色上。
-   **游戏开发**：你的游戏包含大量对话和过场，需要高效、批量地生成高质量的口型同步和面部表情动画。
-   **数字人资产创建**：你需要创建和管理一个 MetaHuman 数字人库，每个数字人拥有独立的身份和可替换的表演动画。

## 蓝图用法

由于 MetaHuman Animator 是一个极其庞大的插件，其蓝图 API 分布在众多子模块中。核心的蓝图可调用函数和属性主要集中在 `MetaHumanIdentity`、`MetaHumanPerformance`、`MetaHumanPipeline` 等模块。以下是一些关键的功能分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaHuman Identity` | 从源图像或扫描数据创建一个新的 MetaHuman 身份资产。 | `UMetaHumanIdentity` |
| `Add Frame to Performance` | 向表演资产中添加一帧捕捉数据（图像、深度等）。 | `UMetaHumanPerformance` |
| `Solve Animation` | 对已有的表演数据运行动画求解，生成最终的动画曲线。 | `UMetaHumanPerformance` |
| `Export to Sequence` | 将求解出的动画数据导出为 Sequencer 可用的动画序列。 | `UMetaHumanSequencer` |
| `Run Pipeline` | 执行一个预定义的 `MetaHumanPipeline` 资产，自动化处理流程。 | `UMetaHumanPipeline` |
| `Batch Process` | 使用 `MetaHumanBatchProcessor` 对一组资产进行批量处理。 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

一个典型的蓝图工作流可能如下：
1.  使用 `Create MetaHuman Identity` 节点，传入演员的正面和侧面照片，创建身份资产。
2.  使用 `Create MetaHuman Performance` 节点，创建一个空的表演资产。
3.  通过循环，使用 `Add Frame to Performance` 节点将 iPhone 录制的每一帧视频数据添加到表演资产中。
4.  调用 `Solve Animation` 节点，对表演资产进行求解。
5.  最后，使用 `Export to Sequence` 节点将结果输出到关卡序列中，供 MetaHuman 角色使用。

## C++ 用法

C++ 用法主要围绕管理 `UMetaHumanIdentity` 和 `UMetaHumanPerformance` 资产，以及调用底层的处理模块。

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanPipeline.h"
```

### 基本用法

以下代码展示了如何以编程方式创建和操作一个 MetaHuman 表演资产。
（来源：基于 `MetaHumanPerformance` 模块的典型用法推断）

```cpp
// 获取 MetaHuman 子系统（如果存在）
UMetaHumanSubsystem* MetaHumanSubsystem = GEngine->GetEngineSubsystem<UMetaHumanSubsystem>();

// 创建一个新的表演资产
UPackage* Package = CreatePackage(TEXT("/Game/MetaHuman/MyPerformance"));
UMetaHumanPerformance* Performance = NewObject<UMetaHumanPerformance>(Package, TEXT("MyPerformance"), RF_Public | RF_Standalone);

// 假设我们有一帧图像数据 FFrameData FrameData
Performance->AddFrame(FrameData);

// 运行求解
FMetaHumanSolveResult SolveResult;
Performance->SolveAnimation(SolveResult);

if (SolveResult.bSuccess)
{
    // 求解成功，可以访问动画数据
    UAnimSequence* AnimSequence = Performance->ExportToAnimSequence();
}
```

### 进阶用法

结合 `MetaHumanPipeline` 模块，可以构建自定义的自动化处理流程。
（来源：基于 `MetaHumanPipeline` 模块结构推断）

```cpp
// 加载一个预定义的管线资产
UMetaHumanPipeline* Pipeline = LoadObject<UMetaHumanPipeline>(nullptr, TEXT("/Game/MetaHuman/Pipelines/MyCustomPipeline"));

// 配置管线输入
FMetaHumanPipelineInput Input;
Input.IdentityAsset = MyIdentity;
Input.PerformanceAsset = MyPerformance;
Input.VideoFilePath = TEXT("D:/Captures/Actor01.mp4");

// 执行管线
FMetaHumanPipelineOutput Output;
Pipeline->Execute(Input, Output);

if (Output.bSuccess)
{
    // 管线执行成功，Output 中包含处理后的资产和数据
}
```

## Demo 示例

由于插件复杂性，以下是一个高度简化的示例，展示如何引用核心类型并进行基本操作。

**MyMetaHumanManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyMetaHumanManager.generated.h"

class UMetaHumanIdentity;
class UMetaHumanPerformance;

UCLASS()
class UMyMetaHumanManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 创建一个简单的身份资产（实际需要更多参数）
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    UMetaHumanIdentity* CreateSimpleIdentity(const FString& AssetName);

    // 创建一个表演资产并添加一帧虚拟数据
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    UMetaHumanPerformance* CreateAndPopulatePerformance(const FString& AssetName);
};
```

**MyMetaHumanManager.cpp**
```cpp
#include "MyMetaHumanManager.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanPerformance.h"
#include "UObject/SavePackage.h"

UMetaHumanIdentity* UMyMetaHumanManager::CreateSimpleIdentity(const FString& AssetName)
{
    FString PackagePath = FString::Printf(TEXT("/Game/MetaHuman/Demo/%s"), *AssetName);
    UPackage* Package = CreatePackage(*PackagePath);
    UMetaHumanIdentity* Identity = NewObject<UMetaHumanIdentity>(Package, *AssetName, RF_Public | RF_Standalone);
    // 在实际应用中，这里需要调用 Identity 的初始化函数并传入源数据
    Package->MarkPackageDirty();
    return Identity;
}

UMetaHumanPerformance* UMyMetaHumanManager::CreateAndPopulatePerformance(const FString& AssetName)
{
    FString PackagePath = FString::Printf(TEXT("/Game/MetaHuman/Demo/%s"), *AssetName);
    UPackage* Package = CreatePackage(*PackagePath);
    UMetaHumanPerformance* Performance = NewObject<UMetaHumanPerformance>(Package, *AssetName, RF_Public | RF_Standalone);

    // 模拟添加一帧数据
    FFrameData DummyFrame;
    // ... 填充 DummyFrame 数据 ...
    Performance->AddFrame(DummyFrame);

    Package->MarkPackageDirty();
    return Performance;
}
```

## 模块依赖

要使用 MetaHuman Animator 插件，你的项目模块需要依赖以下核心模块。由于插件模块众多，这里列出的是最可能需要直接依赖的、具有独特功能的模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供核心数据类型、工具函数和子系统。 |
| `MetaHumanIdentity` | 管理 MetaHuman 数字人身份资产。 |
| `MetaHumanPerformance` | 管理面部表演数据资产和动画求解。 |
| `MetaHumanPipeline` | 定义和执行可配置的动画处理管线。 |
| `MetaHumanCaptureSource` | 处理来自不同设备（如 iPhone）的原始捕捉数据。 |
| `MetaHumanFaceAnimationSolver` | 核心的面部动画求解算法。 |
| `MetaHumanSequencer` | 与 Sequencer 集成，导出动画数据。 |
| `MetaHumanCoreTechLib` | 底层计算机视觉和数学库（通常由其他模块间接依赖）。 |
| `ControlRigDeveloper` | 用于生成和操作 Control Rig 资产。 |
| `MetaHumanSDKEditor` | 提供编辑器扩展和资产类型注册。 |

## 维护状态

### 近期更新

```
- 2024-10-03 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 2024-10-03 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
- 2024-10-03 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

-   **创建时间**：2024年2月，是一个相对较新的插件。
-   **最近更新**：最近的提交（2024年10月）主要是代码维护性更新（添加内联宏、调整DLL导出标记），以及一次重要的代码库迁移。没有发现新的功能性更新。
-   **活跃度**：作为 Epic 官方维护的核心 MetaHuman 工具链的一部分，它处于**持续维护**状态，但近期（截至2024年10月）的更新偏向于底层代码整理而非功能迭代。
-   **已知限制**：该插件高度依赖 Epic 的 MetaHuman 云服务（用于某些高级处理步骤），并且对硬件（如支持 TrueDepth 的 iPhone）和软件环境有特定要求。
-   **推荐使用**：**强烈推荐**。对于任何需要创建高质量 MetaHuman 面部动画的项目，这是官方且功能最完整的解决方案。尽管近期更新以维护为主，但其核心功能稳定，且是 Epic 生态系统的战略组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Epic 官方文档站点)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (位于插件源码内的测试模块)