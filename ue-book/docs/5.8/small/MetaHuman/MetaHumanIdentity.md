# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、配置文件） |
| 模块 | `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 待确定 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHuman Animator` 是 Epic Games 提供的官方高级工具集，旨在**创建高质量、可动画的数字人类（MetaHuman）**。它远不止是一个简单的 API，而是一个端到端的工作流程。

其核心流程是：通过分析来自扫描设备、摄像头或现有资产的**捕获数据**（Mesh 或 Footage），使用面部轮廓追踪、网格拟合等技术，自动将一个标准化的 MetaHuman 模板网格体变形为目标人物的相貌。最终，将此网格体提交至 **AutoRig 服务**，服务返回一个带有完整骨骼绑定和变形目标的 SkeletalMesh。这个结果可以直接用于 MetaHuman Performance 资产，从视频片段生成面部动画序列。

简单来说，它解决了 **“如何从真人影像或模型，快速生成一个媲美真实、可驱动、可动画的数字人类”** 的核心问题。

## 使用场景

-   你在制作一部电影或游戏，需要为演员创建一个高质量的数字替身（Digital Double）进行预演或最终渲染。
-   你在开发一款虚拟主播或 VTuber 应用，需要从摄像头实时或离线驱动一个逼真的人脸模型。
-   你拥有角色的 3D 扫描数据或照片，希望将其转换为可在 Unreal Engine 中自由动画的 MetaHuman。
-   你需要批量处理大量面部表演数据，用于训练 AI 或创建大规模动画内容。

## 蓝图用法

MetaHuman Identity 模块提供了核心的资产和处理逻辑，其蓝图节点主要围绕 **身份创建、部件管理、捕获数据处理和 AutoRig 服务调用** 展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindPartOfClass` | 根据类类型查找 Identity 中已有的 Part（如 Face, Body） | `UMetaHumanIdentity` |
| `GetOrCreatePartOfClass` | 根据类类型查找或创建 Part | `UMetaHumanIdentity` |
| `StartFrameTrackingPipeline` | 启动针对一帧图像数据的面部轮廓追踪流水线 | `UMetaHumanIdentity` |
| `CreateDNAForIdentity` | 调用 AutoRig 服务，为当前 Identity 生成 DNA 数据和最终的骨骼网格体 | `UMetaHumanIdentity` |
| `IsAutoRiggingInProgress` | 检查 AutoRig 服务是否正在运行 | `UMetaHumanIdentity` |
| `SetCaptureData` | 为某个 Pose（如中性表情、牙齿）设置捕获数据（网格体或视频序列） | `UMetaHumanIdentityPose` |
| `AddNewPromotedFrame` | 为 Pose 添加一个新的“晋升帧”，用于保存关键帧的追踪结果和视角 | `UMetaHumanIdentityPose` |
| `Conform` | 对 Face Part 执行“拟合”操作，将模板网格体匹配到捕获数据 | `UMetaHumanIdentityFace` |
| `HandleError` | 统一的错误处理函数，可记录日志并弹出用户提示 | `UMetaHumanIdentity` (静态函数) |

### 使用示例（蓝图描述）

1.  **创建 Identity 并添加 Face Part**:
    在内容浏览器创建 `MetaHuman Identity` 资产。打开其编辑器，在“Parts”部分点击添加，选择 `MetaHuman Identity Face`。这将创建一个包含中性表情和牙齿姿态的初始设置。

2.  **为中性姿态设置捕获数据**:
    选中 Face Part 下的 `Neutral` Pose。在详细面板中找到 `Capture Data` 属性，将其指定为你的网格体资产或影片序列资产。

3.  **追踪与拟合**:
    在视口中预览捕获数据。对每个 Promoted Frame（晋升帧），可以手动调整或使用 `Start Frame Tracking Pipeline` 节点自动追踪面部轮廓。准备好后，调用 `Conform` 节点开始将模板网格体拟合到追踪结果上。

4.  **生成最终骨骼**:
    当拟合完成后且通过诊断检查，调用 `Create DNA For Identity` 节点。这会将数据发送到 AutoRig 服务。通过 `On Auto Rig Service Finished` 动态委托监听完成事件，成功后即可在资产中找到生成的 SkeletalMesh 和相关 DNA 数据。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
```

### 基本用法：管理 Identity 和 Parts

以下代码展示了如何以编程方式创建和管理 MetaHuman Identity 及其组成部分。

```cpp
// 假设在某个 UObject 或 Actor 中
UMetaHumanIdentity* MyIdentity = NewObject<UMetaHumanIdentity>();

// 查找或创建 Face Part
UMetaHumanIdentityFace* FacePart = MyIdentity->GetOrCreatePartOfClass<UMetaHumanIdentityFace>();

// 为中性表情姿态设置捕获数据
UMetaHumanIdentityPose* NeutralPose = FacePart->FindPoseByType(EIdentityPoseType::Neutral);
if (NeutralPose)
{
    UCaptureData* MyScanData = LoadObject<UCaptureData>(nullptr, TEXT("/Game/MyAssets/HeadScan"));
    NeutralPose->SetCaptureData(MyScanData);
}

// 初始化 Face Part (加载默认模板等)
FacePart->Initialize();
```
*来源: 推断自 `UMetaHumanIdentity`, `UMetaHumanIdentityFace`, `UMetaHumanIdentityPose` 的公共接口。*

### 进阶用法：执行完整的 AutoRig 流程

以下代码片段模拟了从调用拟合到请求 AutoRig 的简化流程，展示了对异步任务和错误处理的使用。

```cpp
// 1. 准备拟合
EIdentityErrorCode ErrorCode = FacePart->Conform(EConformType::Solve);
if (ErrorCode != EIdentityErrorCode::None)
{
    // 使用统一的错误处理器，记录日志并可能弹出对话框
    UMetaHumanIdentity::HandleError(ErrorCode, false);
    return;
}

// 2. 绑定完成委托，监听 AutoRig 服务结果
FDelegateHandle AutoRigHandle;
AutoRigHandle = MyIdentity->OnAutoRigServiceFinishedDelegate.AddLambda([WeakIdentity = MakeWeakObjectPtr(MyIdentity), AutoRigHandle](bool bSuccess)
{
    if (UMetaHumanIdentity* ValidIdentity = WeakIdentity.Get())
    {
        if (bSuccess)
        {
            UE_LOG(LogMetaHumanIdentity, Log, TEXT("AutoRig 成功完成！"));
            // 在此处获取生成的 SkeletalMesh 和 DNA 数据
        }
        else
        {
            UE_LOG(LogMetaHumanIdentity, Error, TEXT("AutoRig 失败。"));
        }
        // 完成后记得解绑委托
        ValidIdentity->OnAutoRigServiceFinishedDelegate.Remove(AutoRigHandle);
    }
});

// 3. 检查状态并发起请求
if (FacePart->CanSubmitToAutorigging() && !MyIdentity->IsAutoRiggingInProgress())
{
    // `false` 表示不只记录日志，还要处理错误（如弹窗）
    MyIdentity->CreateDNAForIdentity(false);
}
else
{
    UE_LOG(LogMetaHumanIdentity, Warning, TEXT("Identity 尚未就绪，无法进行 AutoRig。"));
}
```
*来源: `UMetaHumanIdentity::CreateDNAForIdentity`, `UMetaHumanIdentityFace::Conform`, `UMetaHumanIdentityFace::CanSubmitToAutorigging`。*

## Demo 示例

一个最小的 C++ 示例，展示如何从代码创建并初始化一个 MetaHuman Identity。

```cpp
// MetaHumanIdentityDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanIdentityDemo.generated.h"

class UMetaHumanIdentity;
class UMetaHumanIdentityFace;

UCLASS()
class AMyMetaHumanDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanDemoActor();

    UPROPERTY(EditAnywhere, Category="MetaHuman")
    TObjectPtr<UCaptureData> ScanDataAsset;

    UFUNCTION(BlueprintCallable, Category="MetaHuman")
    void GenerateMetaHuman();

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanIdentity> CreatedIdentity;
};

// MetaHumanIdentityDemo.cpp
#include "MetaHumanIdentityDemo.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
#include "CaptureData.h" // 假设包含此类

AMyMetaHumanDemoActor::AMyMetaHumanDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanDemoActor::GenerateMetaHuman()
{
    if (!ScanDataAsset)
    {
        UE_LOG(LogTemp, Error, TEXT("请先指定 ScanDataAsset。"));
        return;
    }

    // 1. 创建新的 Identity 对象
    CreatedIdentity = NewObject<UMetaHumanIdentity>(GetTransientPackage(), NAME_None, RF_Transient);

    // 2. 获取或创建 Face Part 并初始化
    UMetaHumanIdentityFace* Face = CreatedIdentity->GetOrCreatePartOfClass<UMetaHumanIdentityFace>();
    Face->Initialize();

    // 3. 为中性表情设置捕获数据
    if (UMetaHumanIdentityPose* NeutralPose = Face->FindPoseByType(EIdentityPoseType::Neutral))
    {
        NeutralPose->SetCaptureData(ScanDataAsset);
        UE_LOG(LogTemp, Log, TEXT("已为中性表情设置扫描数据。"));
    }

    // 4. (可选) 绑定一个简单的完成委托来接收 AutoRig 结果
    CreatedIdentity->OnAutoRigServiceFinishedDelegate.AddLambda([](bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("MetaHuman 生成成功！"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("MetaHuman 生成失败。"));
        }
    });

    // 此时，`CreatedIdentity` 已经创建好并设置了输入数据。
    // 后续的追踪、拟合、AutoRig 步骤可以通过蓝图或进一步的 C++ 调用来触发。
    // 例如：Face->Conform() 然后 CreatedIdentity->CreateDNAForIdentity(false);
}
```

## 模块依赖

要在你的项目或插件中使用 `MetaHumanIdentity` 模块的核心功能，需要在你的 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 底层技术库（如网格体变形、拟合算法） |
| `MetaHumanSDKEditor` | 与 MetaHuman Creator 和 Quixel Bridge 交互的编辑器 SDK |
| `MetaHumanCaptureDataEditor` | 编辑器中用于预览和操作捕获数据的工具 |
| `ControlRigDeveloper` | 用于生成和处理骨骼绑定数据（DNA 转 Control Rig） |

*注意：`MetaHumanIdentity` 模块本身还依赖 `UnrealEd`, `SkeletalMeshUtilitiesCommon` 等，但这些属于常见引擎模块，不再单独列出。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤掉可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | (MetaHuman Animator) 支持为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与序列器相关的缓存问题。 |

### 维护评价

`MetaHuman Animator` 是 **Epic Games 当前的重点维护项目**，处于**活跃开发**状态。
- **更新频率**：非常频繁，仅在最近几天内就有多个涉及功能、渲染和稳定性的提交。
- **内容相关**：更新内容涵盖新功能（如身体追踪集成）、重要 Bug 修复和用户体验优化。
- **维护状态**：属于 **“活跃维护”** 级别。
- **推荐使用**：对于追求顶级数字人类质量和工作流的项目，**强烈推荐使用**。但请注意，由于其功能复杂且深度依赖 Epic 的在线服务（AutoRig），需要稳定的网络环境，并可能涉及服务条款和费用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/meta-human-animator-in-unreal-engine/) (待确认具体链接，但 Epic 官方文档是主要资源)
- [测试用例] (路径需在源码树中查找，通常位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentity/Tests/` 下)