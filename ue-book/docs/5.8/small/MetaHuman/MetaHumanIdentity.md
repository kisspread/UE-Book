# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、配置） |
| 模块 | `MetaHumanIdentity` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanSpeech2Face` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-10-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
MetaHuman Animator 是一套完整的工具集，用于从面部捕捉数据（网格或视频片段）创建、编辑并驱动 MetaHuman 数字人角色的动画。它提供了一个端到端的解决方案：从导入和处理捕捉数据（如网格扫描或视频片段），到跟踪面部特征点、将模板网格适配到追踪曲线上，再到将结果网格发送到云端自动绑骨服务，最终生成可用于动画制作的骨骼网格体（SkeletalMesh）。此外，该插件还能将视频片段转化为面部动画序列（Performance），或用于在 MetaHuman Creator 中生成完整的 MetaHuman 角色。

## 使用场景
- 你拥有一组面部捕捉的视频片段（如 iPhone 的深感摄像头数据），想要为其创建一个逼真的数字人面部动画 → 使用 MetaHuman Animator 的 Footage to MetaHuman (F2MH) 工作流。
- 你已经有了一个 3D 扫描的头部网格模型，希望将其转化为一个完全绑好骨的 MetaHuman 角色 → 使用 MetaHuman Animator 的 Mesh to MetaHuman (M2MH) 工作流。
- 你想要为已有的 MetaHuman 角色，从一段新的表演视频中驱动出面部动画 → 使用 MetaHuman Performance 功能。
- 你需要根据音频文件自动生成对应的口型动画 → 使用 MetaHuman Speech2Face 功能。
- 你正在构建一个虚拟制片流程，需要快速将真实演员的表演捕捉数据应用到数字角色上。

## 蓝图用法
蓝图 API 主要集中在 `UMetaHumanIdentity` 和相关类上，用于控制身份创建和动画生成流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindPartOfClass` | 在身份资产中查找指定类型的部件（如 Face, Body）。 | `UMetaHumanIdentity` |
| `GetOrCreatePartOfClass` | 查找或创建指定类型的身份部件。 | `UMetaHumanIdentity` |
| `StartFrameTrackingPipeline` | 对提供的图像数据启动面部特征点跟踪流程。 | `UMetaHumanIdentity` |
| `LogInToAutoRigService` | 登录到 MetaHuman 自动绑骨服务。 | `UMetaHumanIdentity` |
| `IsLoggedInToService` | 检查当前是否已登录到服务（仅检查本地会话）。 | `UMetaHumanIdentity` |
| `CreateDNAForIdentity` | 为当前身份资产发起自动绑骨（DNA创建）请求。 | `UMetaHumanIdentity` |
| `Conform` | 对身份中的面部部件执行“适配”（Solve）或“复制”（Copy）操作，将输入数据与模板网格对齐。 | `UMetaHumanIdentityFace` |
| `FindPoseByType` | 根据类型（中性、牙齿、自定义）查找姿态。 | `UMetaHumanIdentityFace` |
| `AddPoseOfType` | 向面部部件添加指定类型的新姿态。 | `UMetaHumanIdentityFace` |
| `SetCaptureData` | 为姿态设置用于分析的捕捉数据（网格或视频）。 | `UMetaHumanIdentityPose` |
| `AddNewPromotedFrame` | 为当前姿态创建一个新的“提升帧”，用于关键帧选择和标记。 | `UMetaHumanIdentityPose` |
| `InitializeContourDataForFootageFrame` | 为视频帧初始化轮廓数据。 | `UPromotedFrameUtils` |
| `HandleError` | 处理身份处理过程中产生的错误代码，记录日志并可选择显示用户对话框。 | `UMetaHumanIdentity` |

### 使用示例（蓝图描述）
1.  **创建身份**：在内容浏览器中右键，选择 `Animation` -> `MetaHuman` -> `MetaHuman Identity` 创建资产。双击打开编辑器。
2.  **添加面部部件**：在编辑器详情面板中，点击 `Parts` 区域的 `+` 号，选择 `MetaHuman Identity Face` 并添加。
3.  **设置捕捉数据**：在 `Face` -> `Poses` -> `Neutral` 下的 `Target` 属性中，设置你的捕捉数据资产（`FootageCaptureData` 或 `MeshCaptureData`）。
4.  **选择提升帧**：在姿态的 `Promoted Frames` 中，添加或选择一个清晰的正面帧，用于后续处理。
5.  **跟踪与适配**：使用 `Start Frame Tracking Pipeline` 节点或编辑器工具栏按钮跟踪特征点，然后使用 `Conform` 节点将模板网格适配到跟踪结果。
6.  **自动绑骨**：确保已登录服务（`Log In To Auto Rig Service`），然后调用 `Create DNA For Identity` 发起自动绑骨请求。成功后，`RigComponent` 将包含可用的骨骼网格体。

## C++ 用法
核心的 C++ API 用于在编辑器工具或自动化流程中操作 MetaHuman Identity 资产。

### 头文件引入
```cpp
#include “MetaHumanIdentity/Public/MetaHumanIdentity.h”
#include “MetaHumanIdentity/Public/MetaHumanIdentityParts.h”
```

### 基本用法
以下代码演示如何以编程方式创建并操作一个 MetaHuman Identity。
（来源：基于 `Public/MetaHumanIdentity.h` 和 `Public/MetaHumanIdentityParts.h` 中的类定义）

```cpp
// 假设我们有一个 UMetaHumanIdentity* Identity 资产
if (Identity)
{
    // 1. 查找或创建面部部件
    UMetaHumanIdentityFace* FacePart = Identity->GetOrCreatePartOfClass<UMetaHumanIdentityFace>();
    if (FacePart)
    {
        // 2. 为中性姿态设置捕捉数据
        UMetaHumanIdentityPose* NeutralPose = FacePart->FindPoseByType(EIdentityPoseType::Neutral);
        if (NeutralPose)
        {
            // 假设 FootageData 是一个 UFootageCaptureData* 或 UMeshCaptureData*
            NeutralPose->SetCaptureData(MyCaptureData);
        }

        // 3. 执行适配操作
        EIdentityErrorCode ErrorCode = FacePart->Conform(EConformType::Solve);
        if (ErrorCode == EIdentityErrorCode::Success)
        {
            // 4. 检查是否可以提交给自动绑骨服务
            if (FacePart->CanSubmitToAutorigging())
            {
                // 5. 触发自动绑骨（需要在已登录服务的上下文中调用）
                Identity->CreateDNAForIdentity(false);
            }
        }
    }
}
```

### 进阶用法
监控自动绑骨流程的异步完成状态。
（来源：基于 `UMetaHumanIdentity` 中的委托声明）

```cpp
// 在某个 UObject 类中绑定委托
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    if (MyIdentityAsset)
    {
        // 绑定动态多播委托，用于蓝图通知
        MyIdentityAsset->OnAutoRigServiceFinishedDynamicDelegate.AddDynamic(this, &AMyActor::OnAutoRigFinished);
        // 绑定普通多播委托，用于 C++ 通知
        MyIdentityAsset->OnAutoRigServiceFinishedDelegate.AddUObject(this, &AMyActor::OnAutoRigFinishedNative);
    }
}

UFUNCTION()
void AMyActor::OnAutoRigFinished(bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT(“MetaHuman auto-rigging succeeded.”));
        // 可以在这里获取生成的骨骼网格体
        USkeletalMeshComponent* RigComp = /* 从 Identity 中获取 */;
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“MetaHuman auto-rigging failed.”));
    }
}

void AMyActor::OnAutoRigFinishedNative(bool bSuccess)
{
    // C++ 原生回调处理
    // ...
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MyIdentityAsset)
    {
        MyIdentityAsset->OnAutoRigServiceFinishedDynamicDelegate.RemoveDynamic(this, &AMyActor::OnAutoRigFinished);
        MyIdentityAsset->OnAutoRigServiceFinishedDelegate.RemoveAll(this);
    }
    Super::EndPlay(EndPlayReason);
}
```

## Demo 示例
一个最小化的示例，展示如何创建并初始化一个 MetaHuman Identity 资产。
```cpp
// MyMetaHumanGenerator.h
#pragma once
#include “CoreMinimal.h”
#include “UObject/NoExportTypes.h”
#include “MyMetaHumanGenerator.generated.h”

UCLASS(BlueprintType)
class MYPROJECT_API UMyMetaHumanGenerator : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = “MetaHuman”)
    static UMetaHumanIdentity* CreateAndInitializeIdentityFromDNA(const FString& InDNAPath);
};

// MyMetaHumanGenerator.cpp
#include “MyMetaHumanGenerator.h”
#include “MetaHumanIdentity.h”

UMetaHumanIdentity* UMyMetaHumanGenerator::CreateAndInitializeIdentityFromDNA(const FString& InDNAPath)
{
    // 1. 创建一个空的 MetaHuman Identity 资产
    UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>();

    // 2. 获取或创建面部部件
    UMetaHumanIdentityFace* FacePart = NewIdentity->GetOrCreatePartOfClass<UMetaHumanIdentityFace>();
    if (!FacePart) return nullptr;

    // 3. 确保中性姿态存在
    UMetaHumanIdentityPose* NeutralPose = FacePart->FindPoseByType(EIdentityPoseType::Neutral);
    if (!NeutralPose)
    {
        NeutralPose = NewObject<UMetaHumanIdentityPose>();
        NeutralPose->PoseType = EIdentityPoseType::Neutral;
        FacePart->AddPoseOfType(EIdentityPoseType::Neutral, NeutralPose);
    }

    // 4. 导入 DNA 文件（这是一个编辑器操作，需要 WITH_EDITOR）
#if WITH_EDITOR
    EIdentityErrorCode ErrorCode = NewIdentity->ImportDNAFile(InDNAPath, EDNADataLayer::LOD0, TEXT(“”));
    if (ErrorCode != EIdentityErrorCode::Success)
    {
        UMetaHumanIdentity::HandleError(ErrorCode);
        return nullptr;
    }
#endif

    return NewIdentity;
}
```

## 模块依赖
使用此插件（特别是 `MetaHumanIdentity` 模块）需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供核心的 MetaHuman 技术库，如面部适配器（FMetaHumanConformer）。 |
| `MetaHumanCaptureDataEditor` | 用于处理和编辑捕捉数据资产。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器工具。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |
| `ControlRigDeveloper` | 用于与 Control Rig（控制绑定）系统交互。 |
| `MeshTrackerInterface` | 面部网格追踪器的抽象接口。 |
| `MetaHumanFaceFittingSolver` | 面部网格适配求解器。 |
| `MetaHumanFaceContourTracker` | 面部轮廓特征点追踪器。 |
| `MetaHumanPipeline` | 处理数据流（Pipeline）的系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价
**活跃维护**。MetaHuman Animator 是 Epic Games 官方维护的核心数字人工具，从 2020 年创建至今持续获得重大更新和功能增强。近期的 git 历史（截至 2026 年 5 月）显示其更新频率非常高，几乎每天都有提交，内容涵盖新功能（如导出动画序列）、渲染质量改进（修复瑕疵）、与新系统（身体追踪）的集成以及稳定性修复（缓存问题）。该插件不存在已知的废弃风险，是构建高保真数字人角色的推荐官方方案。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/working-with-the-metahuman-animator-in-unreal-engine/) （注意：链接为通用指南，最新信息请参考引擎版本内置文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)