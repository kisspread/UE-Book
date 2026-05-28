# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数字人资产、配置模板等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个用于创建、定制和动画化逼真 MetaHuman 数字角色的综合性工具包。它不仅仅是模型导入工具，而是一个端到端的工作流系统，核心功能是将真人表演（来自 iPhone 深度摄像头或其他动捕设备）转换为高质量的 MetaHuman 面部动画。它解决了从真人表演到数字角色驱动过程中的技术难题，包括面部追踪、表情解算、骨骼适配（Conforming）、动画生成等，让开发者能够在 Unreal Engine 内高效地制作影视级别的数字人内容。

## 使用场景

- **游戏开发**：你需要为游戏角色创建逼真的面部动画，例如使用 iPhone 捕捉演员表演并驱动游戏内的 MetaHuman 角色。
- **虚拟制片**：你在制作影视作品，需要将演员的实时或录制表演无缝地映射到数字替身上。
- **语音驱动动画**：你希望仅通过音频文件就能生成对应的口型和面部动画，用于快速原型或本地化工作。
- **数字人定制**：你需要从现有的 3D 模型或照片扫描数据创建自定义的 MetaHuman 角色，并确保其具有可动画化的骨骼绑定。

## 蓝图用法

本插件的编辑器功能主要通过编辑器工具栏和资产编辑器访问，蓝图可直接调用的节点较少。主要交互通过 `UMetaHumanIdentity`、`UMetaHumanPerformance` 等资产对象和相关的编辑器工具链完成。

### 核心资产操作

在蓝图中，你主要操作的是 `UMetaHumanIdentity` 资产。创建、修改和提交到自动绑骨服务等操作，通常在专门的 `MetaHuman Identity Editor` 编辑器界面中完成，该界面提供了丰富的交互式工具。

### 数据导入

你可以通过 C++ 或编辑器 UI，将 `UCaptureData`（捕捉数据，如深度视频或静态网格体）设置到 `UMetaHumanIdentityPose` 上，这是驱动后续流程的基础。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityPromotedFrame.h"
```

### 基本用法 (编程式身份创建)

在 C++ 中，你可以通过 `UMetaHumanIdentityFactoryNew` 工厂类来创建一个新的身份资产。

```cpp
// 引用自：Private/MetaHumanIdentityFactoryNew.h
UCLASS(MinimalAPI, hidecategories = Object)
class UMetaHumanIdentityFactoryNew : public UFactory
{
    GENERATED_BODY()
public:
    UMetaHumanIdentityFactoryNew();
    virtual UObject* FactoryCreateNew(UClass* InClass, UObject* InParent, FName InName, EObjectFlags InFlags, UObject* Context, FFeedbackContext* Warn) override;
    virtual FText GetToolTip() const override;
};
```

### 进阶用法 (访问编辑器工具)

当需要在编辑器工具上下文中操作身份时，可以使用 `UMetaHumanIdentityAssetEditorContext`。

```cpp
// 引用自：Private/MetaHumanIdentityAssetEditorContext.h
UCLASS()
class UMetaHumanIdentityAssetEditorContext : public UObject
{
    GENERATED_BODY()
public:
    TWeakPtr<FMetaHumanIdentityAssetEditorToolkit> MetaHumanIdentityAssetEditor;
};
```
这个上下文对象在编辑器扩展中可以被获取，用于与正在编辑的身份资产进行交互。

## Demo 示例

以下示例展示了如何通过 C++ 代码创建一个新的 `UMetaHumanIdentity` 对象。这通常在编辑器工具或资产工厂内部使用。

```cpp
// MyMetaHumanIdentityHelper.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanIdentityHelper.generated.h"

UCLASS()
class UMyMetaHumanIdentityHelper : public UObject
{
    GENERATED_BODY()

public:
    /** 创建一个新的MetaHuman身份对象 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    static UMetaHumanIdentity* CreateNewIdentityObject(UObject* InOuter, FName InName);

    /** 将网格体资产设置到身份的中性姿态上 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    static bool SetMeshAssetToNeutralPose(UMetaHumanIdentity* InIdentity, UStaticMesh* InMesh);
};
```

```cpp
// MyMetaHumanIdentityHelper.cpp
#include "MyMetaHumanIdentityHelper.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityFactoryNew.h"
#include "Engine/StaticMesh.h"

UMetaHumanIdentity* UMyMetaHumanIdentityHelper::CreateNewIdentityObject(UObject* InOuter, FName InName)
{
    if (!InOuter) return nullptr;
    
    // 使用引擎提供的工厂类来创建资产，这会正确处理事务和资产注册
    UMetaHumanIdentityFactoryNew* Factory = NewObject<UMetaHumanIdentityFactoryNew>();
    return Cast<UMetaHumanIdentity>(Factory->FactoryCreateNew(UMetaHumanIdentity::StaticClass(), InOuter, InName, RF_NoFlags, nullptr, GWarn));
}

bool UMyMetaHumanIdentityHelper::SetMeshAssetToNeutralPose(UMetaHumanIdentity* InIdentity, UStaticMesh* InMesh)
{
    if (!InIdentity || !InMesh) return false;

    // 获取或创建身份的面部部分（Part），然后获取其中性姿态
    // 注意：实际代码中需要处理更复杂的部件（Part）和姿态（Pose）层级关系
    UMetaHumanIdentityFace* FacePart = InIdentity->FindPart<UMetaHumanIdentityFace>();
    if (!FacePart)
    {
        // 创建一个新的面部部件
        FacePart = NewObject<UMetaHumanIdentityFace>(InIdentity);
        InIdentity->AddPart(FacePart);
    }

    UMetaHumanIdentityPose* NeutralPose = FacePart->FindPose(EIdentityPoseType::Neutral);
    if (!NeutralPose)
    {
        // 创建一个新的中性姿态
        NeutralPose = NewObject<UMetaHumanIdentityPose>(FacePart, UMetaHumanIdentityPose::StaticClass(), NAME_None, RF_NoFlags);
        NeutralPose->SetPoseType(EIdentityPoseType::Neutral);
        FacePart->AddPose(NeutralPose);
    }

    // 将静态网格体资产设置为该姿态的捕捉数据源
    UStaticMeshCaptureData* CaptureData = NewObject<UStaticMeshCaptureData>(NeutralPose);
    CaptureData->StaticMesh = InMesh;
    NeutralPose->SetCaptureData(CaptureData);

    return true;
}
```

## 模块依赖

本插件包含大量模块，彼此依赖关系复杂。对于你的项目模块，如果仅需使用核心的身份资产和基本功能，主要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanIdentity` | 核心的身份（Identity）数据资产及其子部件（Face, Body等）的定义 |
| `MetaHumanCore` | MetaHuman 核心库，提供基础数据结构、工具和蓝图库 |
| `MetaHumanToolkit` | 共享的编辑器工具包基础类和UI组件 |
| `MetaHumanCaptureDataEditor` | 捕捉数据（如镜头、网格体）的编辑器支持 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器集成（用于自动绑骨等服务） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具，用于骨骼适配和蒙皮 |
| `ControlRigDeveloper` | Control Rig 开发支持，用于面部动画解算器 |

**注意**：根据你的具体工作流（如使用面部动画解算、身体追踪、语音驱动等），可能需要额外的模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染瑕疵问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时，过滤可视化的辅助对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存问题 |

### 维护评价

**活跃维护**。
- **创建时间**：约 4 年前（2022年），作为 Epic 官方数字人技术的核心套件，属于较新的旗舰功能。
- **近期更新**：最近一周内有多次提交，内容涉及功能增强（动画序列导出）、问题修复（渲染瑕疵、Sequencer缓存）和体验优化（追踪时过滤对象），表明该插件处于**非常活跃的开发和维护**阶段。
- **状态**：作为 Epic 主推的 MetaHuman 工作流核心，预计将持续获得长期投入。
- **推荐**：**强烈推荐**用于任何涉及创建和动画化 MetaHuman 角色的项目。它是官方解决方案，工作流成熟，并且仍在快速迭代中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/) (Epic 官方文档站点)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/MetaHuman) (相关测试可能位于引擎测试目录)