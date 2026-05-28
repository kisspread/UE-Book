# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、UI 组件、缩略图渲染器、配置文件） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 角色创建与面部动画工具链。它解决的核心问题是：**如何将真人面部数据（视频片段或 3D 扫描）转换为可驱动的 MetaHuman 虚拟角色**。

整个插件围绕 **MetaHuman Identity**（角色身份资产）构建了一个完整的面部数字化流水线：

1. **数据捕获**：支持从视频片段（Footage）或静态网格体（Mesh）两种输入源创建角色
2. **面部追踪**：通过面部轮廓追踪器（Face Contour Tracker）在视频帧中自动检测面部特征点
3. **轮廓匹配**：通过 Promoted Frame 机制，让用户选定关键帧并手动/自动调整面部轮廓曲线
4. **面部拟合**：通过面部拟合求解器（Face Fitting Solver）将追踪数据适配到模板网格体上
5. **DNA 导出**：将拟合结果转换为 MetaHuman DNA 格式，用于驱动 MetaHuman 角色的骨骼动画
6. **动画性能**：通过 Speech2Face、Performance 等模块实现从音频到面部动画的转换

这个插件是 MetaHuman Creator 在 Unreal Engine 内的本地化替代方案，让开发者无需云端服务即可在编辑器内完成角色创建。

## 使用场景

- 你有一段人物正面视频，想快速创建一个可动画驱动的 MetaHuman 角色 → 使用 Footage 捕获流程
- 你有一个已有的人物面部 3D 模型，想转换为 MetaHuman → 使用 Mesh 捕获流程
- 你想从音频自动生成面部动画 → 使用 Speech2Face 功能
- 你需要批量处理多个角色资产 → 使用 MetaHumanBatchProcessor 模块
- 你想将 MetaHuman DNA 导入/导出到其他 DCC 工具 → 使用 ImportDNA / ExportDNA 命令

## 蓝图用法

### 核心资产

本插件的核心资产类型是 `UMetaHumanIdentity`，它代表一个 MetaHuman 角色的完整身份定义，包含面部（Face）、牙齿（Teeth）、身体（Body）等部分。

### 编辑器操作节点

本插件的主要功能集中在编辑器扩展中，通过工具栏命令暴露：

| 节点/命令 | 说明 | 所在类 |
|---|---|---|
| `ComponentsFromMesh` | 从静态网格体创建身份组件 | `FMetaHumanIdentityEditorCommands` |
| `ComponentsFromFootage` | 从视频片段创建身份组件 | `FMetaHumanIdentityEditorCommands` |
| `TrackCurrent` | 追踪当前选定的关键帧 | `FMetaHumanIdentityEditorCommands` |
| `TrackAll` | 追踪所有关键帧 | `FMetaHumanIdentityEditorCommands` |
| `ActivateMarkersForCurrent` | 为当前帧激活特征标记点 | `FMetaHumanIdentityEditorCommands` |
| `ActivateMarkersForAll` | 为所有帧激活特征标记点 | `FMetaHumanIdentityEditorCommands` |
| `IdentitySolve` | 执行身份求解（面部拟合） | `FMetaHumanIdentityEditorCommands` |
| `MeshToMetaHumanDNAOnly` | 仅导出 DNA（不含完整 MetaHuman） | `FMetaHumanIdentityEditorCommands` |
| `ImportDNA` | 导入 DNA 文件 | `FMetaHumanIdentityEditorCommands` |
| `ExportDNA` | 导出 DNA 文件 | `FMetaHumanIdentityEditorCommands` |
| `FitTeeth` | 拟合牙齿 | `FMetaHumanIdentityEditorCommands` |
| `PrepareForPerformance` | 准备性能动画 | `FMetaHumanIdentityEditorCommands` |
| `PromoteFrame` | 提升当前帧为关键帧 | `FMetaHumanIdentityEditorCommands` |
| `DemoteFrame` | 取消关键帧提升 | `FMetaHumanIdentityEditorCommands` |
| `ToggleConformalMesh` | 切换共形网格体显示 | `FMetaHumanIdentityEditorCommands` |
| `ToggleRig` | 切换骨骼显示 | `FMetaHumanIdentityEditorCommands` |
| `TogglePlayback` | 切换时间轴播放 | `FMetaHumanIdentityEditorCommands` |
| `ExportTemplateMesh` | 导出模板网格体 | `FMetaHumanIdentityEditorCommands` |

### 使用流程（蓝图/编辑器描述）

1. **创建 Identity 资产**：在 Content Browser 中右键 → Animation → MetaHuman Identity
2. **导入数据**：
   - 方式 A：拖入静态网格体 → 自动创建 Face 部件和 Neutral Pose
   - 方式 B：拖入 FootageCaptureData 资产 → 自动创建 Face 部件和 Neutral Pose
3. **配置捕获数据**：在 Pose 的 Details 面板中设置 CaptureData 来源、时间码对齐方式、摄像机
4. **提升关键帧**：在时间轴上浏览视频帧，点击 "Promote Frame" 将关键帧提升为 Promoted Frame
5. **调整轮廓**：在 Outliner 面板中选择轮廓曲线组，在视口中拖动控制点调整面部特征位置
6. **追踪**：点击 "Track Current" 或 "Track All" 运行面部追踪管线
7. **拟合求解**：点击 "Identity Solve" 将追踪结果拟合到模板网格体
8. **导出 DNA**：点击 "Export DNA" 或 "Mesh to MetaHuman" 完成角色创建

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityPromotedFrame.h"
```

### 基本用法 - 创建和管理 Identity

```cpp
// 创建一个新的 MetaHuman Identity 资产
UMetaHumanIdentityFactoryNew* Factory = NewObject<UMetaHumanIdentityFactoryNew>();
UMetaHumanIdentity* NewIdentity = Cast<UMetaHumanIdentity>(
    Factory->FactoryCreateNew(UMetaHumanIdentity::StaticClass(), 
                              GetTransientPackage(), 
                              FName("MyIdentity"), 
                              RF_Transient, nullptr, GWarn);

// 获取 Identity 的各个部分（Face, Body 等）
TArray<UMetaHumanIdentityPart*> Parts = NewIdentity->GetIdentityParts();
```

### 基本用法 - 处理 Promoted Frame

```cpp
// 从源码 FMetaHumanIdentityAssetEditorToolkit 推断的用法
// Promoted Frame 代表用户选定的关键帧，用于面部追踪

// 获取当前选定的 Pose
UMetaHumanIdentityPose* SelectedPose = /* 从编辑器获取 */;

// 提升一个帧为 Promoted Frame
UMetaHumanIdentityPromotedFrame* PromotedFrame = SelectedPose->AddPromotedFrame(/* frame number */);

// 获取特定 Pose 的轮廓数据
FFrameTrackingContourData ContourData = EditorToolkit->GetPoseSpecificContourDataForPromotedFrame(
    PromotedFrame, SelectedPose, /* bProjectFootage */ false);

// 追踪一个 Promoted Frame
EditorToolkit->HandleTrackCurrent();
```

### 基本用法 - 编辑器工具包扩展

```cpp
// 源自 FMetaHumanIdentityAssetEditorToolkit
// 自定义编辑器工具包用于管理 Identity 资产的编辑

class FMyCustomToolkit : public FMetaHumanIdentityAssetEditorToolkit
{
public:
    FMyCustomToolkit(UAssetEditor* InOwningAssetEditor)
        : FMetaHumanIdentityAssetEditorToolkit(InOwningAssetEditor) {}

    // 重写选择变更处理
    virtual void HandleIdentityTreeSelectionChanged(
        UObject* InObject, EIdentityTreeNodeIdentifier InNodeIdentifier) override
    {
        // 自定义选择处理逻辑
    }
};
```

### 进阶用法 - 自定义 UI 树节点

```cpp
// 源自 SMetaHumanIdentityPartsEditor.h
// FIdentityTreeNode 表示 Identity 部件树中的一个节点

// 创建 Identity 的根节点树
FIdentityTreeNode RootNode(Identity, IdentityActor);

// 创建 Part 节点
FIdentityTreeNode FaceNode(FacePart, IdentityActor, NAME_None, nullptr,
    EIdentityTreeNodeIdentifier::Face);

// 设置预览场景组件
FaceNode.SetupPreviewSceneComponentInstance(IdentityActor);

// 检查节点是否可删除
bool bCanDelete = FaceNode.CanDelete();

// 获取显示文本
FText DisplayText = FaceNode.GetDisplayText();

// 获取关联对象
UObject* AssociatedObject = FaceNode.GetObject();
```

### 进阶用法 - Promoted Frames 编辑器

```cpp
// 源自 SMetaHumanIdentityPromotedFramesEditor.h
// 管理 Promoted Frame 的 UI 和交互

// 设置要编辑的 Pose
PromotedFramesEditor->SetIdentityPose(InPose);

// 获取当前选定的 Promoted Frame
UMetaHumanIdentityPromotedFrame* SelectedFrame = 
    PromotedFramesEditor->GetSelectedPromotedFrame();

// 检查是否可以添加新的 Promoted Frame
bool bCanAdd = PromotedFramesEditor->CanAddPromotedFrame();

// 处理撤销/重做事务
PromotedFramesEditor->HandleUndoOrRedoTransaction(InTransaction);
```

### 进阶用法 - Outliner 曲线管理

```cpp
// 源自 SMetaHumanIdentityOutliner.h
// FIdentityOutlinerTreeNode 用于在 Outliner 中显示轮廓曲线组

// 创建 Outliner 节点用于 Promoted Frame
FIdentityOutlinerTreeNode FrameNode;
FrameNode.PromotedFrame = PromotedFrame;
FrameNode.FrameIndex = InFrameIndex;

// 递归获取所有曲线名称
TArray<FString> CurveNames;
FrameNode.GetCurveNamesRecursive(CurveNames);

// 检查可见性状态
ECheckBoxState VisibleState = FrameNode.IsVisibleCheckState();

// 设置 Outliner 显示的 Promoted Frame
Outliner->SetPromotedFrame(PromotedFrame, FrameIndex, SelectedPoseType);
```

## Demo 示例

### 最小 Identity 编辑器工具包扩展

```cpp
// MyIdentityEditorToolkit.h
#pragma once

#include "MetaHumanIdentityAssetEditorToolkit.h"

class FMyIdentityEditorToolkit : public FMetaHumanIdentityAssetEditorToolkit
{
public:
    FMyIdentityEditorToolkit(UAssetEditor* InOwningAssetEditor);
    
    virtual FName GetToolkitFName() const override;
    virtual FText GetBaseToolkitName() const override;
    
    // 自定义追踪后处理
    void PostTrackProcessing(UMetaHumanIdentityPromotedFrame* InFrame);

private:
    // 引用基类中可以访问的 Identity
    // TObjectPtr<UMetaHumanIdentity> Identity; -- 来自基类
};
```

```cpp
// MyIdentityEditorToolkit.cpp
#include "MyIdentityEditorToolkit.h"

FMyIdentityEditorToolkit::FMyIdentityEditorToolkit(
    UAssetEditor* InOwningAssetEditor)
    : FMetaHumanIdentityAssetEditorToolkit(InOwningAssetEditor)
{
}

FName FMyIdentityEditorToolkit::GetToolkitFName() const
{
    return TEXT("MyIdentityEditorToolkit");
}

FText FMyIdentityEditorToolkit::GetBaseToolkitName() const
{
    return NSLOCTEXT("MyIdentity", "ToolkitName", "My Identity Editor");
}

void FMyIdentityEditorToolkit::PostTrackProcessing(
    UMetaHumanIdentityPromotedFrame* InFrame)
{
    if (!InFrame)
    {
        return;
    }
    
    // 追踪完成后执行自定义逻辑
    // 例如：自动更新轮廓数据、记录追踪结果等
    
    FFrameTrackingContourData ContourData = 
        GetPoseSpecificContourDataForPromotedFrame(InFrame, SelectedIdentityPose, false);
    
    UE_LOG(LogTemp, Log, TEXT("PostTrackProcessing completed for frame"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | MetaHuman Identity 集成 ControlRig 骨骼控制 |
| `MetaHumanCaptureDataEditor` | 捕获数据的编辑器 UI 和资产处理 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器扩展接口 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术算法库（配置模块依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 禁用身体追踪模式下的关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHuman Animator 是 Epic Games 的**旗舰级产品工具**，处于**活跃维护**状态。

- **创建时间**：2022 年 4 月，随 MetaHuman 系统同步推出
- **更新频率**：非常活跃，最近一周内有多次功能性更新和 Bug 修复
- **维护团队**：由 Epic Games 专职团队维护，有持续的功能迭代
- **代码规模**：544 个源文件，28 个模块，属于大型企业级插件
- **已知限制**：
  - 依赖特定的 RHI 支持（部分追踪功能需要特定 GPU）
  - 身体追踪功能仍在迭代中，与关卡序列导出存在兼容性问题
  - `Installed: false` 表示该插件需要手动启用（或通过项目设置启用）
- **推荐程度**：**强烈推荐**用于任何涉及 MetaHuman 角色创建的项目。作为 Epic 官方工具，它是创建高保真数字人类的首选方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)