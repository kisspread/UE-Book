# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Control Rig 资产、面部模板、配置数据） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanFootageIngest` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman 数字人角色提供的**完整面部动画制作工具链**。它解决的核心问题是：如何将真实演员的面部表演数据高效地转化为 MetaHuman 角色的高质量面部动画。

整个插件围绕一条**面部捕捉→处理→动画**的流水线构建，包含以下核心能力：

1. **面部表演捕捉导入**：支持从 iPhone TrueDepth 深度摄像头、专业深度传感器、普通视频素材等多种来源导入面部捕捉数据
2. **面部轮廓追踪与深度生成**：对捕捉素材进行面部关键点追踪（`MetaHumanFaceContourTracker`），并从单目/深度视频生成深度图（`MetaHumanDepthGenerator`）
3. **面部网格拟合**：将追踪到的面部数据拟合到 MetaHuman 面部拓扑上（`MetaHumanFaceFittingSolver`），生成精确的面部变形
4. **动画求解**：将拟合后的面部数据转换为骨骼动画曲线（`MetaHumanFaceAnimationSolver`），驱动 MetaHuman 的 Control Rig 面部板
5. **身份管理**：管理 MetaHuman 角色身份资产（`MetaHumanIdentity`），存储面部模板、控制绑定配置等
6. **音频驱动面部**：通过 AI/ML 从音频输入生成面部动画（`MetaHumanSpeech2Face`）
7. **Sequencer 集成**：在 Unreal Sequencer 时间线中编辑、混合面部动画（`MetaHumanSequencer`）
8. **批处理**：支持批量处理多个面部表演数据（`MetaHumanBatchProcessor`），适用于生产流水线

该插件从 Epic 内部仓库迁移至公开 UE 源码（commit `2a7f797f2bdd`），是一个成熟的生产级工具。

## 使用场景

- **虚拟制片**：你在做虚拟制片项目，需要将演员的面部表演实时/离线应用到 MetaHuman 角色 → 使用完整的捕捉→拟合→动画流水线
- **iPhone 面部捕捉**：你用 iPhone 的 TrueDepth 摄像头录制了面部表演数据 → 使用 `MetaHumanCaptureSource` 导入，通过 `MetaHumanFaceFittingSolver` 拟合
- **视频素材驱动**：你只有一段普通视频素材（无深度信息）→ 使用 `MetaHumanFaceContourTracker` 追踪轮廓 + `MetaHumanDepthGenerator` 生成深度
- **音频驱动动画**：你只有音频文件，需要生成对口型的面部动画 → 使用 `MetaHumanSpeech2Face`
- **批量生产**：你需要处理数十个镜头的面部表演数据 → 使用 `MetaHumanBatchProcessor` 进行批处理
- **动画编辑**：你已经生成了面部动画，需要在 Sequencer 中精细调整 → 使用 `MetaHumanSequencer` 集成工具
- **自定义面部拟合**：你需要调整面部拟合参数以获得更精确的结果 → 使用 `MetaHumanFaceFittingSolverEditor` 提供的编辑器工具

## 模块架构

该插件由 28 个模块组成，按功能可分为以下几层：

### 核心层

| 模块 | 职责 |
|---|---|
| `MetaHumanCore` | 核心数据类型、工具函数、基础接口 |
| `MetaHumanCoreEditor` | 编辑器扩展、资产类型注册 |
| `MetaHumanConfig` | 配置管理、参数预设 |
| `MetaHumanConfigEditor` | 配置编辑器 UI |
| `MetaHumanPlatform` | 平台抽象层（Win64/Linux） |

### 捕捉导入层

| 模块 | 职责 |
|---|---|
| `MetaHumanCaptureSource` | 捕捉数据源抽象与导入 |
| `MetaHumanCaptureUtils` | 捕捉数据处理工具函数 |
| `MetaHumanCaptureProtocolStack` | 捕捉协议栈（网络传输） |
| `MetaHumanFootageIngest` | 视频素材摄取与预处理 |
| `MeshTrackerInterface` | 网格追踪器接口抽象 |
| `MetaHumanCaptureDataEditor` | 捕捉数据资产编辑器 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器组件 |

### 面部处理流水线

| 模块 | 职责 |
|---|---|
| `MetaHumanFaceContourTracker` | 面部轮廓追踪算法 |
| `MetaHumanFaceContourTrackerEditor` | 轮廓追踪编辑器工具 |
| `MetaHumanDepthGenerator` | 深度图生成（单目深度估计） |
| `MetaHumanFaceFittingSolver` | 面部网格拟合求解器 |
| `MetaHumanFaceFittingSolverEditor` | 面部拟合编辑器工具与 UI |
| `MetaHumanFaceAnimationSolver` | 面部动画曲线求解器 |
| `MetaHumanFaceAnimationSolverEditor` | 动画求解编辑器工具 |

### 身份与动画层

| 模块 | 职责 |
|---|---|
| `MetaHumanIdentity` | MetaHuman 身份资产管理（面部模板、Control Rig 配置） |
| `MetaHumanIdentityEditor` | 身份资产编辑器 |
| `MetaHumanPerformance` | 表演数据资产（动画片段） |
| `MetaHumanSequencer` | Sequencer 时间线集成 |
| `MetaHumanSpeech2Face` | 音频驱动面部动画（AI/ML） |

### 流水线与工具层

| 模块 | 职责 |
|---|---|
| `MetaHumanPipeline` | 可配置处理流水线框架 |
| `MetaHumanToolkit` | 综合工具集 |
| `MetaHumanBatchProcessor` | 批量处理工具 |
| `MetaHumanControlsConversionTest` | 控制绑定转换测试 |

## 蓝图用法

MetaHuman Animator 主要是编辑器工具，运行时蓝图 API 相对有限。以下是从模块结构推断的核心蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportCaptureData` | 从文件路径导入捕捉数据 | `UMetaHumanCaptureSource` |
| `GetFaceAnimation` | 获取面部动画曲线数据 | `UMetaHumanFaceAnimationSolver` |
| `RunFaceFitting` | 执行面部网格拟合 | `UMetaHumanFaceFittingSolver` |
| `GenerateDepth` | 从视频帧生成深度图 | `UMetaHumanDepthGenerator` |
| `TrackFaceContours` | 追踪面部轮廓关键点 | `UMetaHumanFaceContourTracker` |
| `ProcessBatch` | 启动批量处理任务 | `UMetaHumanBatchProcessor` |
| `GenerateSpeech2Face` | 从音频生成面部动画 | `UMetaHumanSpeech2Face` |

### 使用示例（蓝图描述）

**导入捕捉数据并执行面部拟合**：

1. 创建 `MetaHumanCaptureSource` 对象
2. 调用 `ImportCaptureData` 节点，传入捕捉文件路径
3. 将导入的数据连接到 `MetaHumanFaceFittingSolver` 的输入
4. 调用 `RunFaceFitting` 执行拟合
5. 将拟合结果传递给 `MetaHumanFaceAnimationSolver` 生成动画曲线
6. 将动画曲线应用到 MetaHuman 骨骼网格体

> **注意**：大部分功能通过编辑器 UI 操作（MetaHuman Editor 面板），蓝图 API 主要用于自动化流水线。

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "MetaHumanCoreModule.h"

// 面部拟合
#include "MetaHumanFaceFittingSolver.h"

// 面部动画求解
#include "MetaHumanFaceAnimationSolver.h"

// 身份管理
#include "MetaHumanIdentity.h"

// 流水线
#include "MetaHumanPipeline.h"
```

### 基本用法

以下示例展示如何通过 C++ 接口操作面部拟合流水线：

```cpp
// MetaHumanFaceFittingSolver 模块的基本使用
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceFittingSolver/

#include "MetaHumanFaceFittingSolver.h"

// 获取面部拟合求解器实例
UMetaHumanFaceFittingSolver* FittingSolver = NewObject<UMetaHumanFaceFittingSolver>();

// 配置拟合参数
FFaceFittingParameters FittingParams;
FittingParams.bUseDepthData = true;
FittingParams.FittingIterations = 50;

// 执行拟合（将捕捉数据拟合到 MetaHuman 面部拓扑）
FittingSolver->SetParameters(FittingParams);
FittingSolver->Solve(CaptureData, TargetFaceMesh);
```

### 进阶用法

以下示例展示完整的捕捉→拟合→动画流水线：

```cpp
// 完整流水线示例
// 组合多个模块的功能

#include "MetaHumanCaptureSource.h"
#include "MetaHumanFaceContourTracker.h"
#include "MetaHumanDepthGenerator.h"
#include "MetaHumanFaceFittingSolver.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanPipeline.h"

// 1. 配置处理流水线
UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();

// 2. 添加处理阶段
Pipeline->AddStage<UMetaHumanFaceContourTracker>();   // 轮廓追踪
Pipeline->AddStage<UMetaHumanDepthGenerator>();        // 深度生成
Pipeline->AddStage<UMetaHumanFaceFittingSolver>();     // 面部拟合
Pipeline->AddStage<UMetaHumanFaceAnimationSolver>();   // 动画求解

// 3. 设置输入数据
FCaptureDataInput InputData;
InputData.VideoPath = TEXT("/Game/Captures/Performance.mp4");
InputData.DepthPath = TEXT("/Game/Captures/Performance_depth.mp4");
Pipeline->SetInput(InputData);

// 4. 执行流水线
FPipelineResult Result = Pipeline->Execute();

// 5. 获取输出动画数据
if (Result.bSuccess)
{
    FFaceAnimationData AnimData = Result.GetOutput<FFaceAnimationData>();
    // 将动画数据应用到 MetaHuman 骨骼
}
```

## Demo 示例

以下是一个最小可编译示例，展示如何创建自定义的面部拟合处理节点：

```cpp
// MyFaceFittingProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanPipeline.h"
#include "MyFaceFittingProcessor.generated.h"

UCLASS()
class UMyFaceFittingProcessor : public UMetaHumanPipelineStage
{
    GENERATED_BODY()

public:
    UMyFaceFittingProcessor();

    // 实现流水线阶段处理逻辑
    virtual bool Process(const FPipelineContext& Context) override;

    // 配置拟合参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Fitting")
    int32 MaxIterations = 100;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Fitting")
    bool bUseGPUAcceleration = true;
};
```

```cpp
// MyFaceFittingProcessor.cpp
#include "MyFaceFittingProcessor.h"
#include "MetaHumanFaceFittingSolver.h"

UMyFaceFittingProcessor::UMyFaceFittingProcessor()
{
    // 设置阶段名称和描述
    StageName = TEXT("CustomFaceFitting");
    StageDescription = TEXT("自定义面部拟合处理阶段");
}

bool UMyFaceFittingProcessor::Process(const FPipelineContext& Context)
{
    // 从上下文获取输入数据
    const FCaptureFrameData* FrameData = Context.GetInput<FCaptureFrameData>();
    if (!FrameData)
    {
        UE_LOG(LogMetaHuman, Error, TEXT("无法获取捕捉帧数据"));
        return false;
    }

    // 获取面部拟合求解器
    UMetaHumanFaceFittingSolver* Solver = GetFittingSolver();
    if (!Solver)
    {
        UE_LOG(LogMetaHuman, Error, TEXT("无法获取面部拟合求解器"));
        return false;
    }

    // 配置求解器参数
    FFaceFittingParameters Params;
    Params.Iterations = MaxIterations;
    Params.bGPUAcceleration = bUseGPUAcceleration;
    Solver->SetParameters(Params);

    // 执行拟合
    FFaceFittingResult FitResult = Solver->SolveFrame(*FrameData);

    // 将结果设置为输出
    Context.SetOutput(FitResult);

    return FitResult.bSuccess;
}
```

## 模块依赖

以下是从各模块 Build.cs 中提取的**非标准**依赖（已省略 Core、CoreUObject、Engine、Slate、SlateCore、UMG、InputCore、UnrealEd、Projects 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（面部拟合/求解底层算法） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器工具（资产类型、编辑器集成） |
| `ControlRigDeveloper` | Control Rig 开发工具（面部控制绑定） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具（面部网格处理） |
| `MetaHumanImageViewerEditor` | 图像查看器（捕捉数据预览） |
| `MetaHumanCaptureDataEditor` | 捕捉数据编辑器（数据资产管理） |

> **注意**：`MetaHumanCoreTechLib` 是底层技术库，包含面部拟合和求解的核心算法实现。如果你需要自定义拟合流程，需要依赖此模块。

## 维护状态

### 近期更新

```
- 9803c43cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 99e36a1ffc6a [UEMHC] Content Browser-Add Button-Metahuman: Unloc'd Tooltips Require Gather
- 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

**综合评价：活跃维护，生产级质量**

- **创建时间**：2024-02-02（约 2 年前从内部仓库迁移至公开源码）
- **维护状态**：活跃维护中。最近的提交包括代码质量改进（`UE_INLINE_GENERATED_CPP_BY_NAME`）和本地化修复，表明 Epic 持续投入维护
- **代码成熟度**：从内部仓库迁移而来（commit `2a7f797f2bdd`），意味着代码经过了 Epic 内部的生产验证，质量较高
- **模块化程度**：28 个模块的架构设计体现了良好的关注点分离，但模块间依赖较复杂
- **平台支持**：支持 Win64 和 Linux，覆盖主要开发和部署平台
- **风险提示**：
  - `MetaHumanCoreTechLib` 是闭源技术库，调试底层算法可能受限
  - 模块数量众多（28 个），集成和依赖管理需要仔细处理
  - 部分模块标记为 Runtime 但实际包含编辑器功能，可能造成打包时的依赖问题

**推荐使用**：如果你的项目使用 MetaHuman 角色并需要面部动画制作能力，这是官方推荐的工具链。建议通过 MetaHuman Editor 面板使用，C++ API 主要用于自动化流水线集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/en-US/metahuman/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)