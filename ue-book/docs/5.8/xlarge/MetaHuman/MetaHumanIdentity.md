# MetaHuman Identity

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 身份资产 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置文件） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHumanIdentity` 是 MetaHuman Animator 插件的核心资产模块。它定义了从原始捕捉数据（三维扫描网格或视频素材）创建一个完整的、可驱动的 MetaHuman 数字人身份的完整工作流程。该资产是连接原始数据输入、面部特征追踪与拟合、自动绑定服务以及最终动画生成的关键枢纽。其主要目的是自动化地将一个真实人物的面部数据，转换为一个具有标准拓扑、完整绑定（骨骼、蒙皮、混合形状）且可在虚幻引擎中用于动画制作的高保真数字人。

## 使用场景

- 你正在开发一款需要高质量、逼真数字人角色的游戏或影视项目 → 使用 MetaHuman Identity 从扫描数据或视频创建角色。
- 你通过扫描设备（如结构光扫描仪）获取了演员的头部三维网格数据 → 将扫描数据导入为 `UCaptureData`，然后在 `MetaHumanIdentity` 中进行拟合和自动绑定，生成可用于动画的骨骼网格。
- 你拍摄了演员不同表情（中性、牙齿）的视频素材 → 在 MetaHuman Identity 中设置“姿态”，利用视频追踪面部特征，并结合深度信息（如果可用）进行高质量拟合，最终通过在线服务自动生成绑定。
- 你需要将已有的 MetaHuman DNA 文件（.dna）导入虚幻引擎，作为 `MetaHumanIdentity` 的基础 → 使用 `ImportDNA` 功能加载现有数据。

## 蓝图用法

`MetaHumanIdentity` 资产及其关联的部件、姿态和框架均暴露了丰富的蓝图 API，主要围绕身份创建、数据管理和处理流程控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindPartOfClass` | 在身份中查找指定类型的部件（如 `UMetaHumanIdentityFace`）。 | `UMetaHumanIdentity` |
| `GetOrCreatePartOfClass` | 查找或创建一个指定类型的部件并返回。 | `UMetaHumanIdentity` |
| `StartFrameTrackingPipeline` | 启动针对一帧图像数据的面部特征追踪流程。 | `UMetaHumanIdentity` |
| `Conform` | 对 `UMetaHumanIdentityFace` 执行拟合（Solve），将模板网格适配到追踪数据。 | `UMetaHumanIdentityFace` |
| `SetCaptureData` | 为 `UMetaHumanIdentityPose` 设置源捕捉数据（网格或视频）。 | `UMetaHumanIdentityPose` |
| `AddNewPromotedFrame` | 为当前姿态添加一个新的“推荐帧”（用于最终拟合的关键帧）。 | `UMetaHumanIdentityPose` |
| `CanTrack` | 检查当前推荐帧是否拥有足够的信息可以开始追踪。 | `UMetaHumanIdentityPromotedFrame` |
| `CreateDNAForIdentity` | 调用在线自动绑定服务，为当前身份生成最终的 DNA 和绑定。 | `UMetaHumanIdentity` |
| `LogInToAutoRigService` | 启动流程以登录到 MetaHuman 自动绑定服务。 | `UMetaHumanIdentity` |
| `ImportDNAFile` | 从指定路径的 `.dna` 文件初始化身份资产（需先有面部部件）。 | `UMetaHumanIdentity` |

### 使用示例（蓝图描述）

1.  **创建身份并设置数据**：
    - 创建一个 `MetaHumanIdentity` 资产（例如通过“右键 -> MetaHuman -> MetaHuman Identity”）。
    - 使用 `GetOrCreatePartOfClass` 节点获取或创建 `UMetaHumanIdentityFace` 部件。
    - 对于面部部件，获取其 `Neutral` 姿态 (`FindPoseByType`)。
    - 为中性姿态设置 `CaptureData`（例如，一个从扫描数据创建的 `MeshSequenceCaptureData`）。
    - 为该姿态添加一个 `PromotedFrame`，并为其设置追踪器和数据。

2.  **执行拟合与生成**：
    - 确保面部部件已设置好捕捉数据和追踪数据。
    - 调用面部部件的 `Conform` 节点（通常选择 `Solve` 类型）。
    - 拟合成功后，确保已登录服务 (`IsLoggedInToService`)。
    - 调用 `CreateDNAForIdentity` 节点发起自动绑定。
    - 通过 `OnAutoRigServiceFinishedDynamicDelegate` 监听完成事件，在成功回调中获取最终的骨骼网格。

## C++ 用法

该模块的 C++ 接口核心围绕 `UMetaHumanIdentity` 及其组合的部件（`UMetaHumanIdentityPart`）和姿态（`UMetaHumanIdentityPose`）展开。

### 头文件引入

```cpp
#include "MetaHumanIdentity/Public/MetaHumanIdentity.h"
#include "MetaHumanIdentity/Public/MetaHumanIdentityParts.h"
#include "MetaHumanIdentity/Public/MetaHumanIdentityPose.h"
```

### 基本用法

以下代码演示了如何以编程方式操作一个 `MetaHumanIdentity` 资产，包括创建、获取部件和添加姿态。

```cpp
// 假设已经获得了一个 UMetaHumanIdentity* IdentityAsset 对象（例如通过编辑器工具或资产查询）

// 1. 获取或创建面部部件
UMetaHumanIdentityFace* FacePart = IdentityAsset->GetOrCreatePartOfClass<UMetaHumanIdentityFace>();
if (FacePart)
{
    UE_LOG(LogTemp, Log, TEXT("成功获取或创建面部部件。"));
}

// 2. 为面部部件添加中性姿态
if (FacePart && FacePart->FindPoseByType(EIdentityPoseType::Neutral) == nullptr)
{
    UMetaHumanIdentityPose* NeutralPose = NewObject<UMetaHumanIdentityPose>(FacePart);
    NeutralPose->PoseType = EIdentityPoseType::Neutral;
    FacePart->AddPoseOfType(EIdentityPoseType::Neutral, NeutralPose);
    UE_LOG(LogTemp, Log, TEXT("为面部部件添加了中性姿态。"));
}
```

### 进阶用法

以下示例演示了拟合流程的核心步骤，这通常在一个更复杂的工具或插件中完成。

```cpp
// 前提：已有一个有效的 MetaHumanIdentity 资产，并且其面部部件已配置好捕捉数据和追踪数据。

// 1. 检查拟合条件
UMetaHumanIdentityFace* FacePart = IdentityAsset->FindPartOfClass<UMetaHumanIdentityFace>();
if (FacePart && FacePart->CanConform())
{
    // 2. 执行拟合（Solve）
    EIdentityErrorCode ErrorCode = FacePart->Conform(EConformType::Solve);
    if (ErrorCode == EIdentityErrorCode::None)
    {
        UE_LOG(LogTemp, Log, TEXT("面部网格拟合成功！"));
        
        // 3. 拟合成功后，通常可以准备自动绑定
        if (IdentityAsset->IsLoggedInToService())
        {
            // 4. 发起自动绑定请求
            IdentityAsset->CreateDNAForIdentity(false /* bInLogOnly */);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("尚未登录 MetaHuman 自动绑定服务。"));
        }
    }
    else
    {
        FText ErrorText;
        UMetaHumanIdentity::HandleError(ErrorCode, false); // 此函数会记录日志并可能显示对话框
    }
}
```

## Demo 示例

以下是一个控制台命令示例，用于演示最基本的 MetaHuman Identity 创建和操作流程。

```cpp
// MetaHumanIdentityDemo.h
#pragma once
#include "CoreMinimal.h"

class FMetaHumanIdentityDemo
{
public:
    static void RunDemo();
};
```

```cpp
// MetaHumanIdentityDemo.cpp
#include "MetaHumanIdentityDemo.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
#include "Engine/Engine.h"
#include "Misc/MessageDialog.h"

DEFINE_LOG_CATEGORY_STATIC(LogMHIdentityDemo, Log, All);

void FMetaHumanIdentityDemo::RunDemo()
{
    UE_LOG(LogMHIdentityDemo, Log, TEXT("=== MetaHuman Identity Demo 开始 ==="));
    
    // 1. 创建一个新的 MetaHumanIdentity 资产对象 (内存中，非持久化资产)
    UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>(GetTransientPackage(), FName("DemoIdentity"));
    if (!NewIdentity)
    {
        UE_LOG(LogMHIdentityDemo, Error, TEXT("创建 MetaHumanIdentity 失败。"));
        return;
    }
    UE_LOG(LogMHIdentityDemo, Log, TEXT("创建 MetaHumanIdentity 成功。"));

    // 2. 获取或创建其面部部件
    UMetaHumanIdentityFace* FacePart = NewIdentity->GetOrCreatePartOfClass<UMetaHumanIdentityFace>();
    if (FacePart)
    {
        UE_LOG(LogMHIdentityDemo, Log, TEXT("面部部件已就绪。"));
        
        // 3. 检查是否能添加中性姿态
        if (NewIdentity->CanAddPoseOfClass(UMetaHumanIdentityPose::StaticClass(), EIdentityPoseType::Neutral))
        {
            // 4. 创建并添加中性姿态
            UMetaHumanIdentityPose* NeutralPose = NewObject<UMetaHumanIdentityPose>(FacePart);
            NeutralPose->PoseType = EIdentityPoseType::Neutral;
            FacePart->AddPoseOfType(EIdentityPoseType::Neutral, NeutralPose);
            UE_LOG(LogMHIdentityDemo, Log, TEXT("已添加中性姿态。姿态数量: %d"), FacePart->GetPoses().Num());

            // 5. 演示查询姿态
            UMetaHumanIdentityPose* FoundPose = FacePart->FindPoseByType(EIdentityPoseType::Neutral);
            if (FoundPose)
            {
                UE_LOG(LogMHIdentityDemo, Log, TEXT("通过类型成功找到中性姿态。"));
            }
        }
        else
        {
            UE_LOG(LogMHIdentityDemo, Warning, TEXT("无法为当前面部部件添加中性姿态。"));
        }
    }

    // 注意：真实的拟合与自动绑定需要有效的追踪数据、登录服务等，此处仅为演示对象创建与关系设置。
    
    UE_LOG(LogMHIdentityDemo, Log, TEXT("=== MetaHuman Identity Demo 结束 ==="));
}

// 可以在模块启动时或通过控制台命令调用：
// FMetaHumanIdentityDemo::RunDemo();
```

## 模块依赖

要使用 `MetaHumanIdentity` 模块，你的模块需要依赖以下关键模块（来自其 Build.cs）：

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | 用于集成和操作 Control Rig，这是 MetaHuman 面部绑定的基础。 |
| `MetaHumanCaptureDataEditor` | 提供用于编辑和预览各种 MetaHuman 捕捉数据资产的编辑器功能。 |
| `MetaHumanSDKEditor` | 提供 MetaHuman SDK 相关的编辑器工具和集成。 |
| `SkeletalMeshUtilitiesCommon` | 提供处理骨骼网格（Skeletal Mesh）的通用工具函数。 |
| `MeshTrackerInterface` | 提供网格追踪器的抽象接口，用于面部特征追踪。 |
| `MetaHumanFaceFittingSolver` | 提供面部网格拟合的核心求解器算法。 |
| `MetaHumanPipeline` | 用于构建和执行数据处理流水线。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格添加导出动画序列功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了序列器的缓存问题。 |

### 维护评价

- **维护状态**：**活跃维护**。模块的更新非常频繁（最近数日内有多次提交），且更新内容涉及功能增强（如身体追踪集成、动画导出）、Bug 修复和渲染质量改进，表明 Epic Games 正在积极开发和维护此模块。
- **稳定性**：从最近的提交看，团队在不断修正问题，模块仍在快速迭代中。`MetaHumanIdentity` 作为 MetaHuman 工作流的核心，其稳定性和可靠性至关重要。
- **推荐使用**：**强烈推荐**用于需要创建和驱动高质量 MetaHuman 数字人的项目。它是官方提供的标准工具链的一部分，与 MetaHuman Creator、Quixel Bridge 等生态系统深度集成。但需注意，由于其复杂的处理流程（涉及在线服务、大量数据处理），对硬件和网络有一定要求，且工作流程相对专业。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-unreal-engine/)（MetaHuman 总体文档）