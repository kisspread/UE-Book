# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、模型、蓝图、配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 虚拟人创作工具集的核心组件。它并非一个单一功能的插件，而是一个庞大的生态系统，旨在将真实的演员面部表演（通过手机视频或专业设备捕捉）转化为 MetaHuman 角色的高质量、可控的面部动画。

**它解决了什么问题？**
传统的面部动画制作流程复杂、耗时且昂贵。MetaHuman Animator 的目标是简化这一流程，让用户能够：
1.  **捕捉面部表演**：从 iPhone 的深度摄像头、其他深度传感器或普通 2D 视频中提取面部关键点和深度信息。
2.  **追踪与求解**：利用计算机视觉算法（如 `MetaHumanFaceContourTracker`）追踪面部轮廓，再通过求解器（如 `MetaHumanFaceAnimationSolver`, `MetaHumanFaceFittingSolver`）将追踪数据转换为驱动 MetaHuman 骨骼的控制数据。
3.  **驱动 MetaHuman**：将求解出的控制数据应用到 MetaHuman 角色模型上，生成逼真的面部动画。
4.  **集成到工作流**：提供从素材导入、数据处理、动画编辑到最终输出的全套工具，深度集成到 Unreal Editor 和 Sequencer 中。

**为什么存在？**
为了推动实时虚拟人技术的发展，降低创作高质量数字人的门槛，让影视、游戏、虚拟直播等领域能够大规模、高效率地使用逼真的数字人角色。

## 使用场景

-   **你正在使用 iPhone 拍摄演员的面部表演** → 使用 `MetaHumanCaptureSource` 和相关模块从 iPhone 视频中提取深度和追踪数据，为 MetaHuman 生成动画。
-   **你有一个预先录制好的面部表演视频（2D 或深度）** → 使用 `MetaHumanFootageIngest` 将素材导入项目，并通过 `MetaHumanCaptureDataEditor` 进行管理和预处理。
-   **你需要创建一个基于演员表演的 MetaHuman 角色** → 使用 `MetaHumanIdentity` 模块，通过多张参考照片（甚至单张）创建面部几何和材质，然后结合动画数据生成完整的数字人。
-   **你希望用语音自动生成口型动画** → 使用 `MetaHumanSpeech2Face` 模块，从音频文件自动生成对应的面部动画。
-   **你需要在 Sequencer 中精细调整 MetaHuman 的面部动画** → `MetaHumanSequencer` 模块提供了专用的轨道和编辑功能。

## 蓝图用法

**注意**：由于整个插件功能复杂，且许多核心求解和追踪算法在底层 C++ 中实现，蓝图可直接调用的高级接口相对有限。主要集中在资产管理、数据处理和流程控制上。

### 核心节点

以下节点分散在各个模块中，主要提供数据导入、处理和资产管理功能。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IngestFootage` | 导入视频素材（如 iPhone 拍摄的 .mov 文件）到项目，并生成可用于后续处理的追踪数据。 | `UMetaHumanFootageIngest` (推测) |
| `ProcessCaptureSource` | 对已导入的捕捉数据源执行追踪和求解过程。 | `UMetaHumanCaptureSource` (推测) |
| `CreateMetaHumanIdentity` | 从参考图像创建一个新的 MetaHuman 身份资产。 | `UMetaHumanIdentity` (推测) |
| `ApplyPerformance` | 将一个性能（Performance）资产应用到 MetaHuman 角色上。 | `UMetaHumanPerformance` (推测) |
| `GenerateAnimationSequence` | 从处理好的捕捉数据生成动画序列。 | `UMetaHumanPipeline` (推测) |

### 使用示例（蓝图描述）

一个典型的蓝图工作流可能如下：
1.  使用 `Import Asset` 或专用的 `IngestFootage` 节点将 iPhone 视频文件导入到项目的内容浏览器中。
2.  创建一个 `MetaHumanIdentity` 资产，并关联捕捉数据。
3.  在 `MetaHumanIdentity` 的编辑器界面或通过蓝图节点，启动面部追踪和求解过程。
4.  求解完成后，将生成的动画数据拖拽到 Sequencer 中 MetaHuman 骨骼网格体的动画轨道上。
5.  在 Sequencer 中，使用 `MetaHumanSequencer` 提供的工具对动画进行微调。

## C++ 用法

MetaHuman Animator 的主要价值在于其底层的计算机视觉和几何处理算法。C++ 开发主要围绕集成、自动化处理和扩展其管道。

### 头文件引入

根据你要使用的具体功能模块引入相应头文件。例如，使用错误处理工具：
```cpp
#include "Error/Result.h"
```

### 基本用法

以下是一个使用 `TResult` 进行错误处理的通用模式，这在插件的内部代码中非常常见。

**来源：`Public/Error/Result.h`**

```cpp
#include "Error/Result.h"

// 定义一个可能失败并返回字符串结果，或返回错误码的函数
TResult<FString, int32> GetProcessedData(const FString& InRawData)
{
    // 模拟处理过程
    if (InRawData.IsEmpty())
    {
        return 101; // 返回错误码
    }
    
    return TEXT("Processed: ") + InRawData; // 返回成功结果
}

void ExampleUsage()
{
    auto Result = GetProcessedData(TEXT("Sample"));

    if (Result.IsValid())
    {
        // 成功，获取结果
        const FString& Data = Result.GetResult();
        UE_LOG(LogTemp, Log, TEXT("Success: %s"), *Data);
    }
    else if (Result.IsError())
    {
        // 失败，获取错误
        int32 ErrorCode = Result.GetError();
        UE_LOG(LogTemp, Error, TEXT("Failed with code: %d"), ErrorCode);
    }
}
```

### 进阶用法

插件内部广泛使用了线程安全的委托和任务管理。例如，使用 `TManagedMulticastDelegate` 在工作线程执行任务后安全地将结果广播到游戏线程。

**来源：`Public/Async/ManagedDelegate.h`**

```cpp
#include "Async/ManagedDelegate.h"

// 定义一个委托，将在游戏线程执行
TManagedMulticastDelegate<FString> OnProcessingComplete;

// 在某个异步任务中
void SomeAsyncProcessingFunction()
{
    // 模拟耗时工作
    // ...

    // 完成后，安全地将结果广播到游戏线程
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [&]()
    {
        FString ResultData = TEXT("Processing Done!");
        // 此调用会自动将委托调度到游戏线程执行
        OnProcessingComplete.Broadcast(ResultData);
    });
}

// 在游戏线程中绑定委托
void SetupDelegate()
{
    OnProcessingComplete.AddLambda([](const FString& Message)
    {
        // 此 Lambda 将在游戏线程执行，可以安全地更新 UI 或游戏对象
        GLog->Log(TEXT("Game Thread Received: ") + Message);
    });
}
```

## Demo 示例

由于 MetaHuman Animator 的集成性极强，一个最小的可编译示例通常需要借助编辑器模块。以下是一个概念性的示例，展示如何通过 C++ 创建一个简单的服务，使用插件提供的错误处理和异步任务工具。

```cpp
// MyMetaHumanService.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Async/ManagedDelegate.h"
#include "Error/Result.h"

UCLASS()
class UMyMetaHumanService : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 一个在游戏线程广播完成事件的委托
    DECLARE_DELEGATE_OneParam(FOnSequenceGenerated, bool /*bSuccess*/);
    
    void GenerateAnimationFromCapture(const FString& CaptureSourceName);

    FOnSequenceGenerated OnSequenceGenerated;

private:
    // 使用 TResult 处理内部流程的失败
    TResult<bool, FString> ValidateCaptureSource(const FString& CaptureSourceName);
};

// MyMetaHumanService.cpp
#include "MyMetaHumanService.h"
#include "Async/Task.h"

TResult<bool, FString> UMyMetaHumanService::ValidateCaptureSource(const FString& CaptureSourceName)
{
    if (CaptureSourceName.IsEmpty())
    {
        return TEXT("Capture source name is empty.");
    }
    
    // 这里应该调用 MetaHumanAnimator 的实际验证逻辑
    // 例如检查是否存在对应的资产等
    bool bExists = true; // 模拟检查
    
    if (!bExists)
    {
        return FString::Printf(TEXT("Capture source '%s' not found."), *CaptureSourceName);
    }
    
    return true; // 验证成功
}

void UMyMetaHumanService::GenerateAnimationFromCapture(const FString& CaptureSourceName)
{
    // 先在游戏线程验证
    auto ValidationResult = ValidateCaptureSource(CaptureSourceName);
    if (ValidationResult.IsError())
    {
        UE_LOG(LogTemp, Error, TEXT("Validation failed: %s"), *ValidationResult.GetError());
        OnSequenceGenerated.ExecuteIfBound(false);
        return;
    }

    // 创建一个可中止的异步任务来执行耗时的生成工作
    auto Task = MakeUnique<FAbortableAsyncTask>(
        [this, CaptureSourceName](const FStopToken& StopToken)
        {
            // 模拟长时间运行的生成过程
            for (int32 i = 0; i < 100; ++i)
            {
                if (StopToken.IsStopRequested())
                {
                    UE_LOG(LogTemp, Warning, TEXT("Generation aborted."));
                    return;
                }
                // 模拟进度
                FPlatformProcess::Sleep(0.05f);
            }

            // 完成后，需要安全地调用回到游戏线程
            AsyncTask(ENamedThreads::GameThread, [this]()
            {
                OnSequenceGenerated.ExecuteIfBound(true);
            });
        });

    Task->StartAsync();
    // 注意：这里为了示例，Task 被立即销毁了。
    // 在实际应用中，你需要将 Task 作为类的成员变量来管理其生命周期，并支持中止。
}
```

**注意**：此示例演示了如何组合使用 `TResult`、`FAbortableAsyncTask` 和线程安全的委托。一个真正的完整 Demo 将需要集成具体的 `MetaHumanCaptureSource`、`MetaHumanPipeline` 等类，这超出了简单示例的范围。

## 模块依赖

MetaHumanCaptureUtils 模块本身是一个工具库，为其他模块提供基础功能。

| 模块 | 用途 |
|---|---|
| `CaptureManagerCore/CaptureUtils` | MetaHumanCaptureUtils 的许多功能在 UE 5.7 中已被废弃并迁移到此模块。新代码应优先使用此模块。 |

**注意**：在使用 MetaHuman Animator 插件的其他核心模块（如 `MetaHumanCaptureSource`, `MetaHumanFaceAnimationSolver`）时，你将依赖于它们各自声明的依赖项，这些依赖项可能包括 `MetaHumanCore`, `MetaHumanPipeline` 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在进行身体追踪时过滤掉可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 的战略性产品，处于**活跃维护**状态。从近期的提交记录可以看出，团队正在持续修复问题、优化工作流（如身体追踪集成、序列器改进）并添加新功能（如为已有网格体导出动画）。虽然单个模块（如 `MetaHumanCaptureUtils`）已标记为废弃，但这代表了代码的模块化重构和功能迁移（至 `CaptureManagerCore`），而非项目本身的废弃。

**结论**：强烈推荐用于创建基于真实表演的 MetaHuman 动画。它是一个复杂但功能强大的系统，适用于追求高保真数字人动画的项目。需要注意，由于插件功能庞大且迭代迅速，开发时应密切关注版本更新和 API 变化（特别是废弃警告）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Characters/MetaHuman/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)