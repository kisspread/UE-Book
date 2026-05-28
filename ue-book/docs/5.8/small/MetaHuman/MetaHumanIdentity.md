# MetaHuman Identity

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人身份 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数字人资产、蓝图逻辑、编辑器工具） |
| 模块 | `MetaHumanIdentity` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-05-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Identity 模块是 MetaHuman Animator 插件的核心运行时模块。它解决的核心问题是：**如何从真实的影像捕获数据（如 3D 扫描网格或视频素材）中创建出一个带有完整绑定的、可驱动的 MetaHuman 数字人资产**。

该模块不仅仅是一个简单的资产类型，它封装了创建 MetaHuman 的完整数据处理管线，包括：
1.  **特征追踪**：从捕获数据中检测和追踪人脸特征曲线（轮廓、关键点）。
2.  **模板网格拟合**：将一个具有标准 MetaHuman 拓扑的模板网格拟合到追踪到的特征曲线上，生成一个与输入数据相匹配的“符合形网格”。
3.  **自动绑定**：调用 Epic 的 AutoRig 云端服务，将符合形网格发送以生成一个带有标准 MetaHuman 骨架和绑定的 `USkeletalMesh`。
4.  **DNA 管理**：处理最终生成的 DNA（数字人动画）数据，包括牙齿拟合、混合形状权重生成、预测求解器训练等高级功能。
5.  **诊断与验证**：在处理流程的各个阶段提供诊断信息，帮助用户排查数据质量或处理错误。

简单来说，`UMetaHumanIdentity` 资产是创建可驱动 MetaHuman 的**起点和数据容器**。它是连接原始捕获数据、几何处理算法、云端绑定服务以及后续动画性能（Performance）资产的桥梁。

## 使用场景

- **创建数字替身**：你从电影级摄像机或移动设备拍摄了演员的面部表演，需要创建一个与之匹配的、可动画的 MetaHuman 数字替身。
- **从扫描数据制作角色**：你使用 3D 扫描设备获得了一个人脸的网格模型，希望将其转换为一个可交互、可驱动的 UE5 角色。
- **批量生产数字人**：你需要一个标准化的流程，将不同来源的捕获数据（网格或视频）批量转化为可用于游戏或虚拟制片的 MetaHuman 角色。
- **自定义绑定资产**：你希望对 MetaHuman 的绑定进行微调，例如调整预测求解器（Predictive Solver）来获得更符合预期的面部动画驱动效果。

## 蓝图用法

核心的 `UMetaHumanIdentity` 类提供了丰富的蓝图可调用函数，用于驱动整个处理流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindPartOfClass` / `GetOrCreatePartOfClass` | 在身份资产中查找或创建特定类型的组成部分（如 Face, Body）。 | `UMetaHumanIdentity` |
| `CanAddPartOfClass` / `CanAddPoseOfClass` | 检查是否可以向当前身份资产添加特定类型的部分或姿态。 | `UMetaHumanIdentity` |
| `StartFrameTrackingPipeline` | **启动核心处理流程**。输入图像数据和相关参数，对指定姿态和提升帧进行特征追踪。 | `UMetaHumanIdentity` |
| `IsFrameTrackingPipelineProcessing` | 查询当前是否有追踪处理正在运行。 | `UMetaHumanIdentity` |
| `SetBlockingProcessing` | 设置是否启用阻塞式处理。 | `UMetaHumanIdentity` |
| `LogInToAutoRigService` | 触发登录到 Epic 的 AutoRig 云端绑定服务。 | `UMetaHumanIdentity` |
| `IsLoggedInToService` | 检查是否已登录到 AutoRig 服务（仅检查本地会话）。 | `UMetaHumanIdentity` |
| `CreateDNAForIdentity` | **提交身份数据以生成 DNA**。这是最终将符合形网格发送到云端进行绑定的关键步骤。 | `UMetaHumanIdentity` |
| `IsAutoRiggingInProgress` | 查询当前是否有自动绑定任务正在进行。 | `UMetaHumanIdentity` |
| `HandleError` | （静态）处理身份处理过程中产生的错误码，记录日志并可选择是否向用户显示对话框。 | `UMetaHumanIdentity` |

### 使用示例（蓝图描述）

1.  **登录与检查状态**：
    *   创建一个 `UMetaHumanIdentity` 资产。
    *   首先调用 `LogInToAutoRigService` 节点，触发登录流程。
    *   使用 `IsLoggedInToService` 节点轮询，直到返回 `true`。

2.  **配置身份并处理捕获数据**：
    *   使用 `GetOrCreatePartOfClass` 获取 `UMetaHumanIdentityFace` 部分。
    *   为面部部分添加姿态（Neutral， Teeth），并为每个姿态设置 `UCaptureData`（可以是网格或视频片段数据）。
    *   为每个姿态添加“提升帧”（Promoted Frame），这些帧将被用于追踪。

3.  **启动追踪与生成 DNA**：
    *   当所有姿态和帧都准备好后，调用 `StartFrameTrackingPipeline` 节点，传入帧的图像数据、尺寸以及相关的深度数据路径。
    *   监听 `OnAutoRigServiceFinishedDynamicDelegate` 事件。
    *   当追踪完成后，检查面部部分是否 `CanSubmitToAutorigging`。
    *   如果可以，调用 `CreateDNAForIdentity` 节点。该节点成功返回后，一个带有绑定的 `USkeletalMesh` 将被附加到面部部分的 `RigComponent` 属性上。

4.  **导出与使用**：
    *   从面部部分的 `RigComponent` 获取生成的骨骼网格体，即可用于角色蓝图或动画系统。
    *   可以使用 `ExportDNADataToFiles` 节点将最终的 DNA 和眉毛数据导出为文件，以便在外部工具中使用或备份。

## C++ 用法

在 C++ 中，`MetaHumanIdentity` 模块提供了更底层和可编程的接口来控制整个流程。

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
```

### 基本用法

以下代码展示了如何以编程方式初始化一个 MetaHuman Identity 资产并启动部分处理流程。

```cpp
// 假设我们已经有了一个 UMetaHumanIdentity* Identity 对象（例如，从资产加载或新建）

// 1. 获取或创建面部部分
if (UMetaHumanIdentityFace* FacePart = Identity->GetOrCreatePartOfClass<UMetaHumanIdentityFace>())
{
    // 2. 为中性表情添加一个姿态
    if (UMetaHumanIdentityPose* NeutralPose = FacePart->FindPoseByType(EIdentityPoseType::Neutral))
    {
        // 设置捕获数据（示例）
        // NeutralPose->SetCaptureData(MyCaptureData);
        
        // 3. 为该姿态添加一个“提升帧”（以视频帧为例）
        int32 NewFrameIndex;
        if (UMetaHumanIdentityFootageFrame* FootageFrame = Cast<UMetaHumanIdentityFootageFrame>(NeutralPose->AddNewPromotedFrame(NewFrameIndex)))
        {
            FootageFrame->FrameNumber = 100; // 设置要处理的帧号
            FootageFrame->FrameName = FText::FromString(TEXT("Frontal"));
            FootageFrame->bIsFrontView = true; // 标记为正视图
            
            // 4. 初始化该帧的轮廓数据（通常由编辑器工具或配置自动完成）
            // UPromotedFrameUtils::InitializeContourDataForFootageFrame(NeutralPose, FootageFrame);
            
            // 5. 启动单帧追踪（实际项目中通常会为多帧调用）
            TArray<FColor> ImageData; // 需要从文件或视频中加载此帧的像素数据
            int32 Width = 1920, Height = 1080;
            FString DepthFramePath = TEXT("/Game/Path/To/Depth/Frame100.exr");
            
            // 注意：此函数是异步的
            Identity->StartFrameTrackingPipeline(
                ImageData, Width, Height, DepthFramePath,
                NeutralPose, FootageFrame, true /* bShowProgress */
            );
        }
    }
}
```

### 进阶用法

**监控处理状态与提交绑定：**

```cpp
// 在启动追踪前，绑定完成委托
Identity->OnAutoRigServiceFinishedDelegate.AddLambda([](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("AutoRigging process completed successfully!"));
        // 在此处获取生成的骨骼网格体
        // UMetaHumanIdentityFace* Face = ...;
        // USkeletalMeshComponent* RigComp = Face->RigComponent;
        // RigComp->GetSkeletalMeshAsset(); // 获取生成的网格资产
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("AutoRigging process failed."));
    }
});

// 启动异步追踪后，在合适的时机（例如所有必要的帧都已追踪完成）提交到AutoRig服务
// 通常在检查了 FacePart->CanSubmitToAutorigging() 之后调用
Identity->CreateDNAForIdentity(false /* bLogOnly */);
```

**管理 DNA 数据：**

```cpp
// 从面部部分获取原始 DNA 缓冲区
if (FacePart->HasRawDNABuffer())
{
    TArray<uint8> RawDNA = FacePart->GetRawDNABuffer();
    // 对 RawDNA 进行自定义处理或保存到文件...
}

// 应用一个新的 DNA 到绑定组件
TSharedPtr<IDNAReader> MyDNAReader = /* ... */;
EIdentityErrorCode ErrorCode = FacePart->ApplyDNAToRig(MyDNAReader, true, true);
if (ErrorCode == EIdentityErrorCode::Success)
{
    UE_LOG(LogTemp, Log, TEXT("DNA applied to rig successfully."));
}
```

## Demo 示例

一个完整的最小示例，展示如何在编辑器工具中创建并初始化一个 MetaHuman Identity。

**MyMetaHumanCreator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanCreator.generated.h"

class UMetaHumanIdentity;
class UMetaHumanIdentityFace;
class UMetaHumanIdentityPose;

UCLASS(BlueprintType)
class UMyMetaHumanCreator : public UObject
{
    GENERATED_BODY()

public:
    /** 创建并初始化一个基础的 MetaHuman Identity 资产 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Creator")
    UMetaHumanIdentity* CreateAndInitializeIdentity(const FString& AssetName, const FString& PackagePath);

private:
    /** 为面部部分添加默认姿态 */
    void AddDefaultPosesToFace(UMetaHumanIdentityFace* InFacePart);
};
```

**MyMetaHumanCreator.cpp**
```cpp
#include "MyMetaHumanCreator.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
#include "AssetToolsModule.h"
#include "IAssetTools.h"

UMetaHumanIdentity* UMyMetaHumanCreator::CreateAndInitializeIdentity(const FString& AssetName, const FString& PackagePath)
{
    // 使用资产工具创建一个新的 UMetaHumanIdentity 资产
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    UObject* NewAsset = AssetTools.CreateAsset(AssetName, PackagePath, UMetaHumanIdentity::StaticClass(), nullptr);
    
    UMetaHumanIdentity* NewIdentity = Cast<UMetaHumanIdentity>(NewAsset);
    if (!NewIdentity)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create MetaHuman Identity asset."));
        return nullptr;
    }

    // 获取或创建面部部分
    UMetaHumanIdentityFace* FacePart = NewIdentity->GetOrCreatePartOfClass<UMetaHumanIdentityFace>();
    if (FacePart)
    {
        AddDefaultPosesToFace(FacePart);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Identity created but failed to initialize Face part."));
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully created MetaHuman Identity: %s"), *NewIdentity->GetName());
    return NewIdentity;
}

void UMyMetaHumanCreator::AddDefaultPosesToFace(UMetaHumanIdentityFace* InFacePart)
{
    // 添加中性表情姿态
    if (!InFacePart->FindPoseByType(EIdentityPoseType::Neutral))
    {
        UMetaHumanIdentityPose* NeutralPose = NewObject<UMetaHumanIdentityPose>(InFacePart);
        NeutralPose->PoseType = EIdentityPoseType::Neutral;
        NeutralPose->PoseName = FText::FromString(TEXT("Neutral"));
        NeutralPose->bFitEyes = true; // 默认使用数据驱动的眼睛拟合
        InFacePart->AddPoseOfType(EIdentityPoseType::Neutral, NeutralPose);
    }

    // 添加牙齿姿态
    if (!InFacePart->FindPoseByType(EIdentityPoseType::Teeth))
    {
        UMetaHumanIdentityPose* TeethPose = NewObject<UMetaHumanIdentityPose>(InFacePart);
        TeethPose->PoseType = EIdentityPoseType::Teeth;
        TeethPose->PoseName = FText::FromString(TEXT("Teeth"));
        InFacePart->AddPoseOfType(EIdentityPoseType::Teeth, TeethPose);
    }
}
```

## 模块依赖

要使用 `MetaHumanIdentity` 模块，你的模块（例如，包含上述 `MyMetaHumanCreator` 的模块）需要在 `.Build.cs` 文件中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | 用于操作和应用 MetaHuman 的 Control Rig。 |
| `MetaHumanSDKEditor` | MetaHuman 编辑器 SDK，提供与 MetaHuman 创作工具集成的接口。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的实用工具函数。 |
| `MetaHumanCaptureDataEditor` | 提供对捕获数据资产的编辑器支持。 |

*注意：模块还依赖 `UnrealEd`, `Slate` 等，但这些属于编辑器和通用模块依赖，未在上表列出。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤掉不必要的可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有的 MetaHuman 网格导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 中的缓存问题。 |

### 维护评价

**活跃维护**。该模块作为 MetaHuman 工具链的核心，近期（2026年5月）有频繁的功能更新和 Bug 修复。更新内容集中在渲染质量改进、与身体追踪功能的集成、以及动画导出功能的增强。创建时间很新，且 Epic Games 作为创建者持续投入开发。模块功能稳定，是 MetaHuman 工作流中推荐使用的标准组件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Characters/MetaHuman/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentity/Tests)