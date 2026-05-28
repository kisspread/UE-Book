# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数字人资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2024-01-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 数字人工具套件。它不仅仅是一个视频处理工具，而是一个完整的、面向流程的数字人资产创建与动画解决方案。其核心目的是将普通视频（特别是 iPhone 拍摄的 ActorCore 格式）或音频文件，转换为驱动 MetaHuman 角色进行逼真面部表演的动画数据。它涵盖了从视频导入、面部追踪、表情解算、性能录制到最终动画序列导出的完整管线。

## 使用场景

- **数字人内容创作**：你需要为一个写实风格的 MetaHuman 角色制作说话、表情丰富的动画，最高效的方式是使用 iPhone 拍摄真人演员的表演视频，通过此插件转换成角色动画。
- **虚拟主播/数字人直播**：你需要实时或准实时地驱动一个 MetaHuman 角色，可以配合 Live Link 和此插件的实时管线，将摄像头捕捉的面部表情映射到虚拟角色上。
- **影视预演/快速迭代**：在影视制作中，需要快速根据对话音频或简单视频生成面部动画，用于场景规划和预览。
- **游戏剧情制作**：为游戏中的 MetaHuman 角色批量制作基于表演的过场动画序列。

## 蓝图用法

由于此插件主要面向复杂的资产创建工作流和编辑器功能，其核心蓝图公开接口主要集中在 `MetaHumanPerformance` 等模块中。以下是从源码分析推断的核心节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load From Capture` | 从视频或图像序列文件加载面部捕获数据，创建用于后续处理的性能资产。 | `UMetaHumanPerformance` |
| `Run Solver` | 对已加载的捕获数据运行面部表情求解器，生成原始的控制曲线数据。 | `UMetaHumanPerformance` |
| `Export To Sequence` | 将求解后的动画数据导出为 UAnimSequence 资产，可直接在 Sequencer 中使用或绑定到 MetaHuman 角色上。 | `UMetaHumanPerformance` |
| `Set Body Tracking` | 启用或禁用身体姿态追踪（与面部追踪协同工作）。 | `UMetaHumanPerformance` |

### 使用示例（蓝图描述）

1.  **创建性能资产**：在 Content Browser 中右键，选择 `Animation > MetaHuman Performance`。在属性面板中设置 `Capture Type` 为视频文件，并指定视频路径。
2.  **执行流程**：
    - 在蓝图中获取到此 `UMetaHumanPerformance` 对象引用。
    - 调用 `Load From Capture` 节点，开始视频解析和面部关键点检测。
    - 进程完成后（可通过异步任务或事件监听），调用 `Run Solver` 节点，将追踪数据转换为 MetaHuman 面部控制参数。
    - 最后，调用 `Export To Sequence` 节点，并指定输出路径和资产名称，生成可用的动画序列。
3.  **应用动画**：将导出的 `UAnimSequence` 作为动画资产，在 MetaHuman 角色的动画蓝图或 Sequencer 轨道中使用。

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "MetaHumanPerformance.h"
// 资产定义（如果在编辑器模块中使用）
#include "AssetDefinition_MetaHumanFaceAnimationSolver.h"
```

### 基本用法

从 `MetaHumanFaceAnimationSolverEditor` 模块的工厂类推断，其 C++ 用法主要涉及编辑器扩展和自定义资产操作。更底层的 API 使用需要参考 `MetaHumanPerformance` 模块。

```cpp
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolverEditor/Private/MetaHumanFaceAnimationSolverFactoryNew.cpp
// 这是一个自定义工厂类，用于在编辑器中创建 MetaHumanFaceAnimationSolver 资产。
// 通常不需要直接调用，而是通过编辑器 UI 触发。
UMetaHumanFaceAnimationSolverFactoryNew::UMetaHumanFaceAnimationSolverFactoryNew()
{
    SupportedClass = UMetaHumanFaceAnimationSolver::StaticClass(); // 假设的资产类
    bCreateNew = true;
    bEditAfterNew = true;
}

UObject* UMetaHumanFaceAnimationSolverFactoryNew::FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* Context, FFeedbackContext* Warn)
{
    UMetaHumanFaceAnimationSolver* NewSolver = NewObject<UMetaHumanFaceAnimationSolver>(InParent, InClass, InName, InFlags);
    // 初始化新资产的默认值...
    return NewSolver;
}
```

### 进阶用法

结合 `MetaHumanPerformance` 模块和工厂模式，可以实现批量处理或自动化脚本。

```cpp
// 假设的批量处理流程 (概念性代码)
#include "MetaHumanPerformance.h"
#include "Factories/MetaHumanPerformanceFactory.h"

void BatchProcessVideos(const TArray<FString>& VideoPaths)
{
    UMetaHumanPerformanceFactory* Factory = NewObject<UMetaHumanPerformanceFactory>();
    for (const FString& Path : VideoPaths)
    {
        // 1. 创建性能资产
        UObject* Asset = Factory->FactoryCreateNew(UMetaHumanPerformance::StaticClass(), 
            GetTransientPackage(), 
            FName(*FPaths::GetBaseFilename(Path)), 
            RF_Public | RF_Standalone, 
            nullptr, GLog);

        if (UMetaHumanPerformance* PerformanceAsset = Cast<UMetaHumanPerformance>(Asset))
        {
            // 2. 设置输入
            PerformanceAsset->SetVideoPath(Path);
            // 3. 异步执行完整流程 (Load -> Solve -> Export)
            PerformanceAsset->ExecuteFullPipeline(FPerformanceExportSettings{});
        }
    }
}
```

## Demo 示例

以下是一个简化的、用于在编辑器工具中创建并触发一个 MetaHumanPerformance 处理流程的示例。

**头文件: MyMetaHumanTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyMetaHumanTool.generated.h"

class UMetaHumanPerformance;

UCLASS(BlueprintType)
class UMyMetaHumanTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "MetaHuman")
    FFilePath VideoInputPath;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "MetaHuman")
    FDirectoryPath OutputPath;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void StartProcessing();

private:
    UPROPERTY()
    UMetaHumanPerformance* CurrentPerformanceAsset;
};
```

**源文件: MyMetaHumanTool.cpp**
```cpp
#include "MyMetaHumanTool.h"
#include "MetaHumanPerformance.h"

void UMyMetaHumanTool::StartProcessing()
{
    if (VideoInputPath.FilePath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Video path is empty."));
        return;
    }

    // 1. 创建临时的 Performance 资产
    CurrentPerformanceAsset = NewObject<UMetaHumanPerformance>(GetTransientPackage(), NAME_None, RF_Transient);
    CurrentPerformanceAsset->SetVideoPath(VideoInputPath.FilePath);

    // 2. 绑定完成回调 (示例)
    FPerformanceCompleteDelegate OnComplete;
    OnComplete.BindLambda([this, OutputDir = OutputPath.Path](bool bSuccess)
    {
        if (bSuccess && CurrentPerformanceAsset)
        {
            // 3. 导出动画序列
            FString FinalPath = FPaths::Combine(OutputDir, TEXT("OutputAnim"));
            CurrentPerformanceAsset->ExportToAnimSequence(FinalPath);
        }
        CurrentPerformanceAsset = nullptr; // 清理
    });

    // 4. 启动异步处理链
    CurrentPerformanceAsset->RunFullPipelineAsync(OnComplete);
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，以下是此插件的**独特依赖**（已省略标准的 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含面部追踪、求解等核心算法。 |
| `SkeletalMeshUtilitiesCommon` | 用于骨骼网格体（MetaHuman 身体）的通用工具函数。 |
| `ControlRigDeveloper` | 用于 MetaHuman 控制绑定（Control Rig）的开发和编辑。 |
| `MetaHumanCaptureDataEditor` | 用于编辑和管理捕获数据（视频、图像）的编辑器模块。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器集成模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复了在启用身体追踪时，关卡序列导出功能不兼容的问题 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了在 MetaHuman 角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 优化了身体追踪时的可视化对象显示 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已存在的网格体新增了动画序列导出功能 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 相关的缓存问题 |

### 维护评价

基于以上信息，此插件的维护状态**活跃**。虽然创建时间未知，但近期内（2026年5月）有密集的功能更新和bug修复记录，表明 Epic 团队正在积极维护和改进此插件。作为一个官方的关键数字人工具，它处于持续迭代中。

**推荐使用**：对于任何涉及 MetaHuman 角色动画制作的项目，此插件是官方推荐且必要的工具，值得依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (可在官网搜索 MetaHuman)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (通常位于 Engine/Tests 目录下，需具体查找)