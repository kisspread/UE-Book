# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产， 材质， 控制器， 动画资产等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的完整 MetaHuman 角色创建与动画工具集。它不仅仅是一个插件，而是一个包含 29 个模块的庞大生态系统，旨在解决从真实人类表演到数字角色驱动的端到端流程。其核心功能包括：
1.  **捕获与导入**：从 iPhone (Live Link Face) 或其他设备捕获面部表演数据、音频以及身体动作数据。
2.  **解算与追踪**：将捕获的视频/深度数据解算为面部控制点，追踪面部轮廓，并拟合成最终的 MetaHuman 面部骨骼动画。
3.  **资产生成与管理**：基于一张或多张照片创建 MetaHuman Identity（身份资产），管理不同角色的配置。
4.  **动画驱动**：将解算后的动画数据应用到 MetaHuman 角色骨骼上，支持从音频生成面部动画（Speech2Face），并可在 Sequencer 中进行精细编辑。
5.  **批处理与流水线**：提供批量处理和自定义流水线的能力，适用于需要处理大量数据的生产环境。

该插件存在的意义是提供一个统一、高效且高质量的工具链，让艺术家和开发者能够大规模地将真实世界的人物和表演转化为虚幻引擎中的高保真数字角色。

## 使用场景

-   你正在开发一款需要大量高保真 NPC 对话的游戏 → 使用 **MetaHumanAnimator** 捕获演员的面部表演，并批量驱动游戏中的 MetaHuman 角色。
-   你正在制作一个虚拟人直播或演示项目 → 使用 **MetaHumanAnimator** 通过 iPhone 的实时视频流驱动一个 MetaHuman 虚拟形象。
-   你有一段现成的音频文件，需要为一个 MetaHuman 角色生成匹配的口型和面部表情动画 → 使用 **MetaHumanSpeech2Face** 模块。
-   你需要为多个角色创建数字分身，照片素材有限（甚至只有一张正面照） → 使用 **MetaHumanIdentity** 模块来创建和优化角色身份。
-   你的工作室需要建立一套标准化的面部动画生产流程，从数据采集到最终动画导出 → 使用 **MetaHumanPipeline** 和 **MetaHumanBatchProcessor** 来定制和自动化整个流程。

## 蓝图用法

由于 MetaHuman Animator 模块众多，其蓝图接口分布在多个模块中。以下是按功能分组的核心节点概览。具体节点需在对应模块的头文件（`Public/` 目录）中查找 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)` 定义。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaHuman Identity` | 从照片资产创建新的 MetaHuman Identity 身份资产 | `UMetaHumanIdentity` |
| `Solve Facial Animation` | 对捕获的面部数据运行解算流程，生成骨骼动画 | `UMetaHumanFaceAnimationSolver` |
| `Apply Animation to MetaHuman` | 将解算后的动画数据应用到目标 MetaHuman 骨骼网格体组件 | `UMetaHumanPerformance` |
| `Generate Face Mesh from Images` | 从一组图像生成面部网格（用于轮廓追踪和拟合） | `UMetaHumanFaceContourTracker` |
| `Batch Process Capture Data` | 对指定文件夹内的捕获数据运行批处理流水线 | `UMetaHumanBatchProcessor` |
| `Start/Stop Live Capture` | 控制从 Live Link Face 等源开始或停止实时捕获 | `UMetaHumanCaptureSource` |

### 使用示例（蓝图描述）

1.  **创建身份资产**：在 Content Browser 中右键，选择 `Animation > MetaHuman > Identity`。在打开的编辑器面板中导入正面照片，系统将自动生成基础面部网格和身份资产。
2.  **实时驱动角色**：将一个 MetaHuman 角色拖入场景。在该角色的 Details 面板中，找到 `Animation > MetaHuman` 分类，指定其使用的 `MetaHuman Identity` 资产。然后，打开 `Live Link Face` 应用连接设备，角色便会实时跟随你的面部表情。
3.  **从视频解算动画**：导入一段面部表演的视频文件。右键点击视频资产，选择 `MetaHuman > Create Capture Data`。在新创建的捕获数据资产上右键，选择 `Solve Facial Animation`。解算完成后，即可将生成的动画序列应用到角色上。

## C++ 用法

### 头文件引入

```cpp
// 引入结果处理工具
#include "MetaHumanCaptureUtils/Error/Result.h"

// 引入异步任务工具
#include "MetaHumanCaptureUtils/Async/Task.h"

// 引入作用域守卫工具
#include "MetaHumanCaptureUtils/Error/ScopeGuard.h"
```

### 基本用法

`MetaHumanCaptureUtils` 模块提供了许多底层的、与捕获无关的实用工具类，被插件其他模块广泛使用。

**使用 `TResult` 进行错误处理**（来源：`Public/Error/Result.h`）
`TResult` 是一个轻量级的“结果或错误”返回值包装器，类似于 Rust 的 `Result`。

```cpp
#include "MetaHumanCaptureUtils/Error/Result.h"

// 定义一个可能失败的操作
TResult<FString, FText> LoadConfiguration(const FString& Path)
{
    // 模拟加载
    if (Path.IsEmpty())
    {
        // 返回错误
        return FText::FromString(TEXT("配置文件路径为空"));
    }
    
    // 加载成功，返回结果
    return TEXT("ConfigData");
}

void UseResult()
{
    TResult<FString, FText> Result = LoadConfiguration(TEXT("/Game/Config.json"));
    
    if (Result.IsValid())
    {
        // 使用 Result.GetResult() 获取结果
        UE_LOG(LogTemp, Log, TEXT("配置加载成功: %s"), *Result.GetResult());
    }
    else if (Result.IsError())
    {
        // 使用 Result.GetError() 获取错误信息
        UE_LOG(LogTemp, Error, TEXT("配置加载失败: %s"), *Result.GetError().ToString());
    }
}
```

### 进阶用法

**使用 `FAbortableAsyncTask` 执行可中止的后台任务**（来源：`Public/Async/Task.h`）
这个类封装了 UE 的异步任务系统，并添加了停止令牌（`FStopToken`），允许在任务运行时请求中止。

```cpp
#include "MetaHumanCaptureUtils/Async/Task.h"

// 定义一个耗时的后台任务函数
void LongRunningBackgroundWork(const FStopToken& StopToken)
{
    for (int32 i = 0; i < 1000000; ++i)
    {
        // 在循环中检查是否请求了停止
        if (StopToken.IsStopRequested())
        {
            UE_LOG(LogTemp, Warning, TEXT("任务被中止，已处理 %d 项"), i);
            return;
        }
        
        // ... 执行一些工作 ...
    }
    UE_LOG(LogTemp, Log, TEXT("后台任务完成"));
}

void StartAndPotentiallyAbortTask()
{
    // 创建一个可中止的异步任务
    TUniquePtr<FAbortableAsyncTask> AsyncTask = MakeUnique<FAbortableAsyncTask>(LongRunningBackgroundWork);
    
    // 启动后台任务
    AsyncTask->StartAsync();
    
    // 在某些条件下（例如用户取消操作），可以中止任务
    // AsyncTask->Abort();
    
    // 确保任务在销毁前完成或已中止
    // AsyncTask 会在其析构函数中自动处理， 但也可以手动调用
}
```

## Demo 示例

以下是一个最小可编译的 C++ 类示例，演示如何使用 `MetaHumanCaptureUtils` 模块中的核心工具。

**MetaHumanDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanCaptureUtils/Error/Result.h"
#include "MetaHumanCaptureUtils/Async/Task.h"
#include "MetaHumanDemoActor.generated.h"

UCLASS()
class MYPROJECT_API AMetaHumanDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMetaHumanDemoActor();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:	
	// 一个使用 TResult 的蓝图可调用函数
	UFUNCTION(BlueprintCallable, Category = "MetaHumanDemo")
	FString TryLoadAsset(bool bShouldSucceed);

private:
	// 后台任务
	TUniquePtr<FAbortableAsyncTask> BackgroundTask;

	// 后台任务函数
	static void ProcessDataInBackground(const FStopToken& StopToken);
};
```

**MetaHumanDemoActor.cpp**
```cpp
#include "MetaHumanDemoActor.h"

AMetaHumanDemoActor::AMetaHumanDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 启动一个后台处理任务
	BackgroundTask = MakeUnique<FAbortableAsyncTask>(ProcessDataInBackground);
	BackgroundTask->StartAsync();
}

void AMetaHumanDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	// 确保在 Actor 销毁时安全停止后台任务
	if (BackgroundTask.IsValid() && !BackgroundTask->IsDone())
	{
		BackgroundTask->Abort();
		// 析构函数会确保任务完成
	}

	Super::EndPlay(EndPlayReason);
}

FString AMetaHumanDemoActor::TryLoadAsset(bool bShouldSucceed)
{
	TResult<FString, FText> Result = bShouldSucceed
		? TResult<FString, FText>(TEXT("AssetData"))
		: TResult<FString, FText>(FText::FromString(TEXT("加载失败！")));

	if (Result.IsValid())
	{
		return Result.ClaimResult(); // 使用 ClaimResult 转移所有权
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("%s"), *Result.GetError().ToString());
		return TEXT("");
	}
}

void AMetaHumanDemoActor::ProcessDataInBackground(const FStopToken& StopToken)
{
	UE_LOG(LogTemp, Log, TEXT("开始后台数据处理..."));
	for (int i = 0; i < 1000; ++i)
	{
		if (StopToken.IsStopRequested())
		{
			UE_LOG(LogTemp, Warning, TEXT("后台处理已被取消"));
			return;
		}
		// 模拟工作
		FPlatformProcess::Sleep(0.001f);
	}
	UE_LOG(LogTemp, Log, TEXT("后台数据处理完成。"));
}
```

## 模块依赖

此插件拥有庞大的模块依赖网络。以下列出的是除了标准 Core/Engine/Slate 等之外，使用者（尤其是编写自定义解算器、处理器或扩展时）可能需要关注的独特依赖模块。实际依赖请查阅各子模块的 `.Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库， 包含面部解算、网格处理等底层算法。 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具函数。 |
| `ControlRigDeveloper` | 用于开发和控制 Control Rig（MetaHuman 面部动画基于此）。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器端功能， 用于资产创建和编辑。 |
| `MediaUtils` | 媒体工具， 用于处理视频/图像序列等捕获数据。 |
| `MeshTrackerInterface` | 网格追踪接口， 用于深度摄像头等设备的网格数据。 |
| `HTTP` | HTTP 模块， 可能用于在线资源获取或设备通信。 |
| `CaptureManagerCore` | **注意**： `MetaHumanCaptureUtils` 模块已在 5.7 版本标记为废弃，其功能已迁移至此模块。新项目应直接依赖 `CaptureManagerCore` 及其子模块 `CaptureUtils`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时， 禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

**积极维护**。
- **活跃度**：该插件在最近一周内有多次提交（截至提供的 git log），表明 Epic Games 的开发团队正在积极开发和维护。
- **内容**：更新内容包括新功能（身体追踪相关的导出与过滤）、重要 Bug 修复（渲染问题、缓存问题）以及功能改进（为现有网格导出动画），说明这是一个处于核心开发阶段的产品。
- **稳定性**：虽然部分底层模块（如 `MetaHumanCaptureUtils`）已标记为废弃并进行迁移，但这是正常的架构演进过程，不影响整体插件的可用性。
- **推荐度**：作为 Epic Games 官方提供的、功能完备且持续更新的 MetaHuman 创作工具链，**强烈推荐**用于任何涉及高保真 MetaHuman 角色动画的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/MetaHumans/InEngine/MetaHumanAnimator/) （虚幻引擎文档站）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) （位于插件源码内）