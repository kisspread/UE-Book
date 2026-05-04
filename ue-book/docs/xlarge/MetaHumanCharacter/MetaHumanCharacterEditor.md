# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、数据表） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHuman Character 插件是 UE5 内置的 MetaHuman 角色创建与编辑系统。它提供了一套完整的角色资产工作流，涵盖：

- **角色创建**：通过 `UMetaHumanCharacterFactoryNew` 工厂类创建 MetaHuman 角色资产
- **面部编辑**：基于 `FMetaHumanCharacterIdentity` 的面部身份系统，支持雕刻、移动等操纵器操作
- **身体编辑**：基于 `FMetaHumanCharacterBodyIdentity` 的身体身份系统
- **纹理合成**：通过云端服务（`FFaceTextureSynthesisServiceRequest`）生成高分辨率面部/身体纹理
- **自动绑定**：通过云端自动绑定服务（`FAutoRigServiceRequest`）生成角色骨骼绑定
- **衣橱系统**：通过 `MetaHumanCharacterPalette` 模块管理服装、发型等可穿戴资产
- **几何体移除**：通过 `UE::MetaHuman::GeometryRemoval` 移除被衣物遮挡的身体几何体，优化性能
- **构建管线**：支持 Cinematic、Optimized、DCC、UEFN 等多种输出管线
- **动画预览**：通过 `AMetaHumanInvisibleDrivingActor` 在编辑器中预览面部/身体动画及 Live Link 驱动
- **验证系统**：通过 `UMetaHumanCharacterValidationContext` 验证角色资产的完整性

与旧版 MetaHuman Creator（纯云端工具）不同，此插件将角色编辑能力完全集成到 UE 编辑器中，支持离线编辑和本地构建。

## 使用场景

- 你需要在 UE 编辑器中从零创建一个 MetaHuman 角色 → 使用 MetaHuman Character Editor 面板
- 你需要为 MetaHuman 角色更换服装/发型 → 使用衣橱（Wardrobe）系统和调色板（Palette）
- 你需要将旧版 MetaHuman 迁移到新的角色资产格式 → 使用 `MetaHumanCharacterMigrationEditor` 模块
- 你需要将 MetaHuman 导出到 Maya/Blender 等 DCC 工具 → 使用 DCC 管线构建
- 你需要为 MetaHuman 生成高分辨率纹理 → 使用云端纹理合成服务
- 你需要优化 MetaHuman 的运行时性能 → 使用 Optimized 管线和几何体移除功能
- 你需要通过 Live Link 实时驱动 MetaHuman 面部动画 → 使用 `AMetaHumanInvisibleDrivingActor`

## 蓝图用法

> ⚠️ 本插件主要面向编辑器工作流，大部分功能通过编辑器 UI 面板暴露，纯蓝图 API 较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetHairVisibilityState` | 设置头发组件的可见性状态（显示/隐藏） | `AMetaHumanCharacterEditorActor` |
| `SetClothingVisibilityState` | 设置服装组件的可见性状态，可使用覆盖材质 | `AMetaHumanCharacterEditorActor` |
| `SetShowNormalsOnFace` | 在面部网格上显示法线调试可视化 | `AMetaHumanCharacterEditorActor` |
| `SetShowTangentsOnFace` | 在面部网格上显示切线调试可视化 | `AMetaHumanCharacterEditorActor` |

### 编辑器设置（蓝图可配置）

通过 **Project Settings → Plugins → MetaHumanCharacter** 可配置以下选项：

| 设置 | 说明 |
|---|---|
| `TextureSynthesisModelDir` | 纹理合成模型目录路径 |
| `TextureSynthesisThreadCount` | 纹理合成线程数（0 = 自动） |
| `SculptManipulatorMesh` | 雕刻操纵器使用的静态网格 |
| `MoveManipulatorMesh` | 移动操纵器使用的静态网格 |
| `bShowCompatibilityModeBodies` | 是否显示兼容模式身体类型 |
| `bEnableExperimentalWorkflows` | 是否启用实验性工作流 |
| `PresetsDirectories` | MetaHuman 预设搜索目录 |
| `TemplateAnimationDataTableAssets` | 模板动画数据表资产路径 |

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacterEditorSubsystem.h"
#include "MetaHumanCharacterEditorActor.h"
#include "MetaHumanCharacterBuild.h"
#include "MetaHumanGeometryRemoval.h"
#include "MetaHumanCharacterSkinMaterials.h"
#include "MetaHumanRigLogicUnpackLibrary.h"
```

### 基本用法 — 获取编辑器子系统

编辑器子系统 `UMetaHumanCharacterEditorSubsystem` 是访问所有角色编辑功能的入口点。

```cpp
// 来源: MetaHumanCharacterEditorSubsystem.h
UMetaHumanCharacterEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UMetaHumanCharacterEditorSubsystem>();
if (Subsystem)
{
    // 通过子系统访问角色编辑功能
    // 包括面部/身体身份编辑、纹理合成、自动绑定等
}
```

### 基本用法 — 构建参数配置

```cpp
// 来源: Subsystem/MetaHumanCharacterBuild.h
FMetaHumanCharacterEditorBuildParameters BuildParams;
BuildParams.PipelineType = EMetaHumanDefaultPipelineType::Cinematic;
BuildParams.PipelineQuality = EMetaHumanQualityLevel::Cinematic;
BuildParams.AnimationSystemName = FName("Default");
BuildParams.AbsoluteBuildPath = TEXT("/Game/MetaHumans/MyCharacter");
BuildParams.bEnableWardrobeItemValidation = true;
```

### 基本用法 — 几何体移除

```cpp
// 来源: MetaHumanGeometryRemoval.h
#include "MetaHumanGeometryRemoval.h"

// 将多个隐藏面贴图合并为一个
TArray<FHiddenFaceMapImage> SourceMaps;
// ... 填充 SourceMaps
FHiddenFaceMapImage DestinationMap;
FText FailureReason;
bool bSuccess = UE::MetaHuman::GeometryRemoval::TryCombineHiddenFaceMaps(SourceMaps, DestinationMap, FailureReason);

if (bSuccess)
{
    // 对骨骼网格的指定 LOD 执行几何体移除和收缩
    UE::MetaHuman::GeometryRemoval::RemoveAndShrinkGeometry(
        SkeletalMesh,
        /*LODIndex=*/ 0,
        DestinationMap,
        /*MaterialSlotsToProcess=*/ {});  // 空数组 = 处理所有材质槽
}
```

### 进阶用法 — 动画预览与 Live Link 驱动

```cpp
// 来源: MetaHumanInvisibleDrivingActor.h
AMetaHumanInvisibleDrivingActor* DrivingActor = /* 获取或生成 Actor */;

// 设置身体网格
DrivingActor->SetBodySkeletalMesh(BodySkeletalMesh);

// 设置面部和身体动画序列
DrivingActor->SetAnimation(FaceAnimSequence, BodyAnimSequence);

// 播放控制
DrivingActor->PlayAnimation();
DrivingActor->PauseAnimation();
DrivingActor->ScrubAnimation(0.5f);  // 跳到 50% 位置
DrivingActor->SetAnimationPlayRate(1.5f);  // 1.5 倍速

// 获取动画信息
float Length = DrivingActor->GetAnimationLength();
float CurrentTime = DrivingActor->GetCurrentPlayTime();
EMetaHumanCharacterAnimationPlayState State = DrivingActor->GetAnimationPlayState();

// 切换到 Live Link 驱动模式
DrivingActor->SetLiveLinkSubjectNameChanged(FName("iPhoneFace"));
```

### 进阶用法 — Rig Logic 解包

```cpp
// 来源: MetaHumanRigLogicUnpackLibrary.h
// 将 DNA 文件中的 RBF 逻辑解包到动画蓝图
TArray<uint16> HalfRotationSolvers;
TArray<FMetaHumanBodyRigLogicGeneratedAsset> GeneratedAssets;
bool bSuccess = UMetaHumanRigLogicUnpackLibrary::UnpackRBFEvaluation(
    AnimBlueprint,
    SkeletalMesh,
    GeneratedAssetOuter,
    /*bUnpackFingerRBFToHalfRotationControlRig=*/ true,
    HalfRotationSolvers,
    GeneratedAssets);

// 解包 SwingTwist 逻辑到 ControlRig
TObjectPtr<UControlRigBlueprint> ControlRig = UMetaHumanRigLogicUnpackLibrary::UnpackControlRigEvaluation(
    AnimBlueprint,
    SkeletalMesh,
    ExistingControlRig,
    GeneratedAssetOuter,
    /*bUnpackSwingTwistEvaluation=*/ true,
    HalfRotationSolvers);
```

### 进阶用法 — 云端服务请求

```cpp
// 来源: Subsystem/MetaHumanCharacterService.h
FMetaHumanCharacterEditorCloudRequests CloudRequests;

// 检查是否有活跃请求
if (CloudRequests.HasActiveRequest())
{
    // 等待完成...
}

// 纹理合成请求完成后
CloudRequests.TextureSynthesisRequestFinished();

// 从云端响应生成纹理
bool bTexturesUpdated = FMetaHumanCharacterEditorCloudRequests::GenerateTexturesFromResponse(
    HighFrequencyResponse,
    FaceTextureSynthesizer,
    CharacterData,
    MetaHumanCharacter);
```

### 进阶用法 — 验证系统

```cpp
// 来源: Verification/MetaHumanCharacterValidation.h
// 使用作用域报告自动管理生命周期
UMetaHumanCharacterValidationContext::FScopedReport Report(
    { .ObjectToValidate = CharacterAsset, .bSilent = false });

// 添加验证消息
TSharedRef<FTokenizedMessage> Msg = Report.Context->AddMessage(EMessageSeverity::Warning);
Msg->AddToken(FTextToken::Create(FText::FromString(TEXT("Some warning message"))));

// 验证衣橱物品
Report.Context->ValidateWardrobeItem(WardrobeItem);

// 如果需要取消报告
// Report.Cancel();

// 离开作用域时自动调用 EndReport() 并显示 Message Log
```

## Demo 示例

### 创建 MetaHuman 角色编辑器 Actor

```cpp
// MetaHumanCharacterDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MetaHumanCharacterDemo.generated.h"

class UMetaHumanCharacter;
class AMetaHumanCharacterEditorActor;

UCLASS()
class UMetaHumanCharacterDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 创建一个 MetaHuman 角色并设置编辑器预览 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void CreateDemoCharacter();

    /** 切换头发可见性 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void ToggleHairVisibility();

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanCharacter> DemoCharacter;

    UPROPERTY()
    TObjectPtr<AMetaHumanCharacterEditorActor> PreviewActor;

    bool bHairVisible = true;
};
```

```cpp
// MetaHumanCharacterDemo.cpp
#include "MetaHumanCharacterDemo.h"
#include "MetaHumanCharacterEditorSubsystem.h"
#include "MetaHumanCharacterEditorActor.h"
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterBuild.h"
#include "MetaHumanGeometryRemoval.h"

void UMetaHumanCharacterDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UMetaHumanCharacterDemoSubsystem::Deinitialize()
{
    DemoCharacter = nullptr;
    PreviewActor = nullptr;
    Super::Deinitialize();
}

void UMetaHumanCharacterDemoSubsystem::CreateDemoCharacter()
{
    // 获取编辑器子系统
    UMetaHumanCharacterEditorSubsystem* MHSubsystem =
        GEditor->GetEditorSubsystem<UMetaHumanCharacterEditorSubsystem>();
    if (!MHSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("MetaHumanCharacterEditorSubsystem not available"));
        return;
    }

    // 配置构建参数
    FMetaHumanCharacterEditorBuildParameters BuildParams;
    BuildParams.PipelineType = EMetaHumanDefaultPipelineType::Cinematic;
    BuildParams.PipelineQuality = EMetaHumanQualityLevel::Cinematic;
    BuildParams.AbsoluteBuildPath = TEXT("/Game/MetaHumans/DemoCharacter");
    BuildParams.bEnableWardrobeItemValidation = true;

    UE_LOG(LogTemp, Log, TEXT("MetaHuman Character demo configured with Cinematic pipeline"));
}

void UMetaHumanCharacterDemoSubsystem::ToggleHairVisibility()
{
    if (!PreviewActor)
    {
        UE_LOG(LogTemp, Warning, TEXT("No preview actor available"));
        return;
    }

    bHairVisible = !bHairVisible;
    PreviewActor->SetHairVisibilityState(
        bHairVisible
            ? EMetaHumanHairVisibilityState::Visible
            : EMetaHumanHairVisibilityState::Hidden);
}
```

## 模块依赖

本插件包含 7 个模块，以下是各模块的关键依赖（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTech` | MetaHuman 核心技术库（DNA 处理、身份系统） |
| `MetaHumanTextureSynthesis` | 面部/身体纹理合成 |
| `MetaHumanProjectUtilities` | MetaHuman 项目工具函数 |
| `ControlRig` | Control Rig 动画系统集成 |
| `RigLogicModule` | Rig Logic 面部绑定求解器 |
| `GeometryScript` | 几何体脚本工具（动态网格操作） |
| `GeometryFramework` | 几何体框架（UDynamicMesh） |
| `LiveLinkInterface` | Live Link 实时数据接口 |
| `SkeletalMeshDescription` | 骨骼网格描述数据 |
| `MeshDescription` | 网格描述数据 |
| `SkelMeshDNAUtils` | 骨骼网格 DNA 工具 |
| `MessageLog` | 消息日志（验证报告） |

## 维护状态

### 近期更新

```
- a7ffdedc5b23 [UEMHC] Release any live MID/MIC when replacing newly assembled MIs — 修复材质实例替换时的资源泄漏
- 22acb2339ad8 [UEMHC] Check for valid path before MHC assembly — 构建前增加路径有效性检查
- 25cf9ea2ebb8 [UEMHC] Set MHC editor exported face/body skel meshes to standalone — 导出的骨骼网格设置为独立资产
```

### 维护评价

- **创建时间**：2025-03-17，非常新的插件（约 4 个月）
- **实验性状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，明确标记为 Beta 阶段
- **更新频率**：近期有持续的 bug 修复和质量改进，开发活跃
- **代码规模**：583 个源文件，属于超大型插件，架构复杂
- **已知限制**：
  - Beta 版本，API 可能在后续版本中发生变化
  - 需要手动启用（`EnabledByDefault=false`）
  - 依赖 MetaHuman 核心内容包（可通过 `IsOptionalMetaHumanContentInstalled()` 检查）
  - 云端纹理合成和自动绑定需要网络连接和 Epic 账户
- **推荐程度**：如果你需要在 UE5 中创建和编辑 MetaHuman 角色，这是官方推荐的工具。虽然是 Beta 状态，但作为 Epic 官方插件，维护质量有保障。建议关注版本更新日志以跟踪 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]()（暂无）