# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MetaHumanIdentityEditor` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanSequencer` (Runtime) 等 29 个模块 |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的数字人（MetaHuman）创建与编辑工具套件。它并非一个简单的运行时组件，而是一个完整的 **工作流程平台**，核心解决的问题是：**如何将现实世界中的表演数据（视频/3D扫描）转化为可用于UE的高质量、可驱动的虚拟角色资产。**

这个插件通过 `MetaHumanIdentity` 资产系统，将整个流程标准化：从捕获数据（Footage/Mesh）导入、面部特征点追踪、模板拟合、到最终生成可驱动的 DNA 资产。`MetaHumanIdentityEditor` 模块正是这个核心编辑器的实现，它提供了用于创建、配置和执行这些复杂流程的图形化界面。

## 使用场景

- **创建高质量数字人**：你有一段人脸表演视频（如 iPhone 录制），希望快速生成一个长相相似、可进行面部动画的 MetaHuman 角色用于游戏或影视。
- **数字化已有3D角色**：你有一个现有的3D人物模型（静态网格体），希望将其转换为具有标准骨骼和控制器的 MetaHuman，以便使用 MetaHuman 的表情系统。
- **批量处理与管理**：你需要处理多个角色资产，`MetaHumanBatchProcessor` 模块可以帮助自动化部分流程。
- **预览与动画编辑**：使用 `MetaHumanPerformance` 和 `MetaHumanSequencer` 模块，你可以直接在编辑器中预览驱动结果，并将动画数据导出或用于序列器编辑。

## 蓝图用法

由于此插件主要提供编辑器工具和资产处理流程，其核心交互发生在编辑器UI中，而非蓝图节点。主要的蓝图/编辑器API集中于创建和操作 `MetaHumanIdentity` 资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddPartsFromAsset` | 从一个资产（网格体或视频数据）快速创建身份部件（Face, Body等）和姿态。 | `SMetaHumanIdentityPartsEditor` |
| `SetIdentityPose` | 为 PromotedFramesEditor 设置当前正在编辑的 Identity Pose。 | `SMetaHumanIdentityPromotedFramesEditor` |
| `HandleIdentityTreeSelectionChanged` | 当身份部件树状视图的选择发生变化时，更新详情面板和视口显示。 | `FMetaHumanIdentityAssetEditorToolkit` |
| `HandleTrackCurrent` | 触发当前选中的 Promoted Frame 的面部追踪流程。 | `FMetaHumanIdentityAssetEditorToolkit` |
| `HandleConform` | 执行“Conform”操作，将模板网格体拟合到追踪到的面部特征点上。 | `FMetaHumanIdentityAssetEditorToolkit` |

### 使用示例（蓝图描述）

1.  **创建身份资产**：在内容浏览器中右键，选择 `Animation -> MetaHuman Identity` 创建一个新的 `UMetaHumanIdentity` 资产。
2.  **打开编辑器**：双击该资产，将打开 `MetaHuman Identity Editor` 窗口。
3.  **导入源数据**：在 `Identity Parts Editor` 面板中，点击添加部件，选择 `Face`。然后，在 `Neutral` 姿态的属性中，指定你的 `Footage Capture Data` 或 `Mesh Capture Data` 资产。
4.  **提升关键帧**：在 `Promoted Frames` 面板中，通过播放视频或查看网格体，选择具有代表性的关键帧（如正面、侧面、张嘴等），点击“Promote Frame”将其提升。
5.  **追踪与拟合**：选择提升的帧，在工具栏点击“Track Current”进行面部特征点追踪。追踪完成后，点击“Conform”将模板拟合到你的面部数据上。
6.  **生成DNA**：完成所有姿态和关键帧的处理后，使用“Mesh To MetaHuman”或相关工具生成最终的 DNA 资产，用于驱动 MetaHuman 角色。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityAssetEditorToolkit.h"
```

### 基本用法

创建并初始化一个 `MetaHumanIdentity` 资产。
*（注意：以下为概念性代码，实际使用需遵循资产创建和编辑器初始化的正确流程）*
```cpp
// 假设你有一个有效的UPackage
UPackage* Package = CreatePackage(nullptr, TEXT("/Game/MyMetaHumanIdentity"));

// 创建一个新的 MetaHumanIdentity 资产
UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>(Package, UMetaHumanIdentity::StaticClass(), FName("MHI_NewCharacter"), RF_Public | RF_Standalone);

// 为其添加一个面部部件
UMetaHumanIdentityFace* FacePart = NewObject<UMetaHumanIdentityFace>(NewIdentity);
NewIdentity->AddIdentityPart(FacePart);

// 为面部部件添加一个中性姿态
UMetaHumanIdentityPose* NeutralPose = NewObject<UMetaHumanIdentityPose>(FacePart, UMetaHumanIdentityPose::StaticClass());
FacePart->AddIdentityPose(NeutralPose);

// 设置姿态的捕获数据源（假设你有相应的数据）
// NeutralPose->SetCaptureData(YourCaptureData);

// 标记资产已修改
NewIdentity->MarkPackageDirty();
```

### 进阶用法

通过编辑器工具包（Toolkit）以编程方式驱动编辑器的操作。
```cpp
// 获取或创建资产编辑器
UAssetEditor* AssetEditor = GEditor->GetEditorSubsystem<UAssetEditorSubsystem>()->FindEditorForAsset(NewIdentity, true);
if (AssetEditor)
{
    // 获取工具包指针
    TSharedPtr<FMetaHumanIdentityAssetEditorToolkit> Toolkit = StaticCastSharedPtr<FMetaHumanIdentityAssetEditorToolkit>(AssetEditor->GetToolkit());
    if (Toolkit.IsValid())
    {
        // 模拟用户在UI中的操作：为特定姿态添加一个提升帧
        UMetaHumanIdentityPose* Pose = ...; // 获取目标姿态
        UMetaHumanIdentityPromotedFrame* NewFrame = NewObject<UMetaHumanIdentityPromotedFrame>(Pose);
        Pose->AddPromotedFrame(NewFrame);
        
        // 通知工具包有新的提升帧被添加，以更新UI
        Toolkit->HandlePromotedFrameAdded(NewFrame);
        
        // 如果需要，可以立即对该帧执行追踪（需要有效的捕获数据和配置）
        // Toolkit->HandleTrackCurrent();
    }
}
```

## Demo 示例

以下是一个最小化的示例，展示如何以编程方式创建一个基本的 `MetaHumanIdentity` 结构。

**MyMetaHumanIdentityHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityFace.h"
#include "MetaHumanIdentityPose.h"

class UMyMetaHumanIdentityHelper
{
public:
    static UMetaHumanIdentity* CreateBasicIdentityInPackage(UPackage* InPackage, const FString& InAssetName);
};
```

**MyMetaHumanIdentityHelper.cpp**
```cpp
#include "MyMetaHumanIdentityHelper.h"

UMetaHumanIdentity* UMyMetaHumanIdentityHelper::CreateBasicIdentityInPackage(UPackage* InPackage, const FString& InAssetName)
{
    if (!InPackage)
    {
        return nullptr;
    }

    // 创建 MetaHumanIdentity 资产
    UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>(
        InPackage,
        UMetaHumanIdentity::StaticClass(),
        *InAssetName,
        RF_Public | RF_Standalone
    );

    if (NewIdentity)
    {
        // 添加一个面部部件
        UMetaHumanIdentityFace* FacePart = NewObject<UMetaHumanIdentityFace>(NewIdentity);
        NewIdentity->AddIdentityPart(FacePart);

        // 为面部部件添加一个中性姿态
        UMetaHumanIdentityPose* NeutralPose = NewObject<UMetaHumanIdentityPose>(
            FacePart,
            UMetaHumanIdentityPose::StaticClass()
        );
        FacePart->AddIdentityPose(NeutralPose);

        // 为中性姿态添加一个提升帧
        UMetaHumanIdentityPromotedFrame* PromotedFrame = NewObject<UMetaHumanIdentityPromotedFrame>(NeutralPose);
        NeutralPose->AddPromotedFrame(PromotedFrame);

        // 标记资产需要保存
        NewIdentity->MarkPackageDirty();
        InPackage->MarkPackageDirty();
    }

    return NewIdentity;
}
```

## 模块依赖

要使用 `MetaHumanIdentityEditor` 模块（或完整插件），你的项目模块需要链接以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanIdentity` | 核心数据资产模块，包含 `UMetaHumanIdentity` 等核心类。 |
| `MetaHumanCaptureDataEditor` | 提供捕获数据（视频/网格）相关的编辑器UI和工具。 |
| `MetaHumanImageViewerEditor` | 提供用于查看和标注捕获图像的编辑器组件。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供更底层的集成支持。 |
| `ControlRigDeveloper` | 用于处理与 MetaHuman 身体和面部控制绑定相关的开发工作。 |

*注意：该插件还隐含依赖许多其他模块，如 `MetaHumanCore`, `MetaHumanFaceFittingSolver` 等，但它们作为运行时依赖会被自动处理。上表列出的是你的 **编辑器模块** 在编写与 MetaHuman 资产交互代码时，通常需要显式依赖的独特模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复数字人（MH）身上的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤视口中的可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存相关问题。 |

### 维护评价

- **创建时间**：虽然确切创建时间未知，但根据 Epic 的发布历史和插件成熟度，可判定为**多年项目**。
- **活跃度**：从最近的 Git 提交记录看（2026年5月），插件仍在 **积极维护** 中。更新内容涉及功能修复（渲染、缓存）和新功能开发（身体追踪、导出增强）。
- **推荐程度**：**强烈推荐**。作为 Epic Games 官方维护的 MetaHuman 工具链核心，它提供了最权威、最完整的数字人创建与编辑工作流。虽然学习曲线较陡，且对捕获数据有要求，但它是创建影视级、可驱动数字人的行业标准解决方案。唯一的限制是它主要面向**内容创建**而非轻量级运行时功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentityEditor/Tests)（此路径可能不存在于公开仓库，测试通常在 Epic 内部或 `Engine/Tests` 中）