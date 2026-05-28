# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-xx-xx |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

> **注意**：本文档聚焦于当前模块 `MetaHumanIdentityEditor`。MetaHuman Animator 是一个包含 28 个模块、544 个源文件的超大型插件，提供从面部捕捉数据导入、跟踪、拟合到 DNA 导出的完整 MetaHuman 创建管线。

## 用途

MetaHuman Identity Editor 模块是 MetaHuman Animator 插件的核心编辑器 UI 层。它为 MetaHuman Identity 资产提供完整的编辑器体验，包括：

1. **Identity 资产管理**：创建和编辑 MetaHuman Identity 资产，这是描述一个 MetaHuman 角色所有面部和身体数据的中枢资产
2. **部件与姿态管理**：以树形结构管理 Face（面部）、Body（身体）等部件，以及 Neutral（中性）、Teeth（牙齿）等姿态
3. **Promoted Frame（提升帧）系统**：从视频片段或网格体中选取关键帧，为每帧保存相机变换、跟踪轮廓数据和渲染状态
4. **面部轮廓跟踪**：在提升帧上运行面部轮廓跟踪器，提取面部关键点
5. **模板网格拟合**：将通用模板网格拟合到跟踪结果上
6. **自动绑定提交**：将拟合后的数据提交到 MetaHuman Auto-Rigging 服务生成 DNA
7. **DNA 导入/导出**：支持导入和导出 DNA 文件

**核心工作流**：Footage/Mesh → Promoted Frames → Track → Conform → Auto-Rig → DNA

## 使用场景

- 你有 iPhone 拍摄的面部视频素材 → 导入为 FootageCaptureData，选择关键帧作为 Promoted Frame，跟踪轮廓后拟合模板网格
- 你有扫描获得的面部网格体 → 导入为 MeshCaptureData，在网格上直接设置姿态并跟踪
- 你需要从已有数据生成 MetaHuman DNA → 完成跟踪和拟合后，提交到 Auto-Rigging 服务或直接导出 DNA
- 你正在开发 MetaHuman 相关工具 → 依赖此模块的资产定义、编辑器工具包和 UI 组件

## 蓝图用法

本模块为纯编辑器 UI 模块，所有核心逻辑封装在 C++ Slate 控件和编辑器工具包中，**不暴露 BlueprintCallable 函数**。交互通过编辑器 UI 完成。

### 核心编辑器命令

以下命令通过编辑器工具栏和菜单触发，对应 `FMetaHumanIdentityEditorCommands`：

| 命令 | 说明 |
|---|---|
| `ComponentsFromMesh` | 从网格体创建组件（CaptureData + Face + Neutral Pose） |
| `ComponentsFromFootage` | 从视频片段创建组件 |
| `TrackCurrent` | 跟踪当前选中的提升帧 |
| `TrackAll` | 跟踪所有提升帧 |
| `ActivateMarkersForCurrent` | 为当前帧激活标记点 |
| `ActivateMarkersForAll` | 为所有帧激活标记点 |
| `IdentitySolve` | 提交到 Auto-Rigging 服务 |
| `MeshToMetaHumanDNAOnly` | 仅导出 DNA（不创建完整 MetaHuman） |
| `ImportDNA` / `ExportDNA` | 导入/导出 DNA 文件 |
| `FitTeeth` | 拟合牙齿 |
| `PrepareForPerformance` | 准备用于表演捕捉 |
| `PromoteFrame` / `DemoteFrame` | 提升/取消提升帧 |

### 编辑器 UI 组件

| 组件 | 类 | 说明 |
|---|---|---|
| Identity Parts Editor | `SMetaHumanIdentityPartsEditor` | 树形视图，管理 Face/Body 部件和 Neutral/Teeth 姿态 |
| Promoted Frames Editor | `SMetaHumanIdentityPromotedFramesEditor` | 水平按钮列表，管理提升帧的添加/选择/删除 |
| Outliner | `SMetaHumanIdentityOutliner` | 轮廓曲线/组的大纲视图，控制可见性和跟踪激活 |
| Parts Class Combo | `SMetaHumanIdentityPartsClassCombo` | 下拉菜单，选择要添加的部件或姿态类型 |

## C++ 用法

### 头文件引入

```cpp
// 引入 Identity 资产相关类（来自 MetaHumanIdentity 模块）
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityFace.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityPromotedFrame.h"

// 编辑器相关（来自 MetaHumanIdentityEditor 模块）
#include "MetaHumanIdentityAssetEditorToolkit.h"
```

### 核心数据模型

从源码分析，Identity 资产的层级结构如下：

```cpp
UMetaHumanIdentity                    // 根资产
├── UMetaHumanIdentityPart            // 部件基类
│   ├── UMetaHumanIdentityFace        // 面部部件
│   └── UMetaHumanIdentityBody        // 身体部件
├── UMetaHumanIdentityPose            // 姿态基类
│   ├── Neutral Pose                  // 中性表情姿态
│   └── Teeth Pose                    // 牙齿姿态
│       └── UMetaHumanIdentityPromotedFrame  // 提升帧
│           ├── Camera Transform      // 相机变换（位置+旋转）
│           ├── Contour Data          // 跟踪轮廓数据
│           └── Tracking Mode         // 跟踪模式
└── Capture Data (Footage/Mesh)       // 捕获数据源
```

### 编辑器工具包 API

```cpp
// 编辑器工具包继承自 FMetaHumanToolkitBase
class FMetaHumanIdentityAssetEditorToolkit : public FMetaHumanToolkitBase
{
public:
    // 处理 Identity 树的选择变更
    void HandleIdentityTreeSelectionChanged(
        UObject* InObject, 
        EIdentityTreeNodeIdentifier InNodeIdentifier);

    // 处理新增提升帧
    void HandlePromotedFrameAdded(UMetaHumanIdentityPromotedFrame* InPromotedFrame);

    // 运行跟踪管线
    void HandleTrackCurrent();

    // 获取特定姿态的默认轮廓数据
    FFrameTrackingContourData GetPoseSpecificContourDataForPromotedFrame(
        UMetaHumanIdentityPromotedFrame* InPromotedFrame,
        TWeakObjectPtr<UMetaHumanIdentityPose> InPose,
        bool bInProjectFootage = false) const;

    // 获取 Parts Editor 控件
    const TSharedPtr<SMetaHumanIdentityPartsEditor> GetIdentityPartsEditor() const;
};
```

### 编辑器自定义（Property Customization）

```cpp
// 为 Promoted Frame 属性面板添加自定义显示
// 来源: MetaHumanIdentityPoseCustomizations.h
class FMetaHumanIdentityPromotedFramePropertyCustomization
    : public IPropertyTypeCustomization
{
public:
    // 控制相机变换的可编辑性（基于 NavigationLocked 属性）
    bool CanEditCameraTransform(
        TSharedRef<IPropertyHandle> InNavigationLockedHandle) const;
};
```

### 资产定义与缩略图

```cpp
// 资产定义 - 控制内容浏览器中的显示
// 来源: AssetDefinition_MetaHumanIdentity.h
class UAssetDefinition_MetaHumanIdentity : public UAssetDefinitionDefault
{
    virtual FText GetAssetDisplayName() const override;
    virtual FLinearColor GetAssetColor() const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& InOpenArgs) const;
};
```

## Demo 示例

以下展示如何通过代码创建一个 MetaHuman Identity 资产并设置基础结构：

```cpp
// MyMetaHumanTool.h
#pragma once

#include "CoreMinimal.h"

class FMyMetaHumanTool
{
public:
    /** 创建一个新的 MetaHuman Identity 资产 */
    static class UMetaHumanIdentity* CreateIdentityAsset(
        const FString& InAssetPath, 
        const FString& InAssetName);

    /** 为 Identity 添加面部部件 */
    static void AddFacePart(class UMetaHumanIdentity* InIdentity);
};
```

```cpp
// MyMetaHumanTool.cpp
#include "MyMetaHumanTool.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityFace.h"
#include "MetaHumanIdentityPose.h"
#include "AssetRegistry/AssetRegistryModule.h"

UMetaHumanIdentity* FMyMetaHumanTool::CreateIdentityAsset(
    const FString& InAssetPath, 
    const FString& InAssetName)
{
    // 通过工厂创建新资产
    UPackage* Package = CreatePackage(
        *FString::Printf(TEXT("%s/%s"), *InAssetPath, *InAssetName));
    
    UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>(
        Package, 
        UMetaHumanIdentity::StaticClass(),
        FName(*InAssetName),
        RF_Public | RF_Standalone);
    
    if (NewIdentity)
    {
        NewIdentity->MarkPackageDirty();
        FAssetRegistryModule::AssetCreated(NewIdentity);
    }
    
    return NewIdentity;
}

void FMyMetaHumanTool::AddFacePart(UMetaHumanIdentity* InIdentity)
{
    if (!InIdentity)
    {
        return;
    }
    
    // Identity 通常通过编辑器 UI 的 "Add Parts from Asset" 流程
    // 来创建 Face Part 并关联 Capture Data
    // 底层调用链: SMetaHumanIdentityPartsEditor::AddPartsFromAsset()
    //   -> 创建 UMetaHumanIdentityFace
    //   -> 创建 UMetaHumanIdentityPose (Neutral)
    //   -> 关联 FootageCaptureData 或 MeshCaptureData
}
```

## 模块依赖

从 `MetaHumanIdentityEditor` 模块的 Build.cs 分析，依赖了以下独特模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanIdentity` | Identity 资产的数据模型（Face/Body/Pose/PromotedFrame） |
| `MetaHumanToolkit` | 基础编辑器工具包框架（FMetaHumanToolkitBase） |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器支持 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器支持 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |
| `ControlRigDeveloper` | ControlRig 开发支持（用于骨骼控制） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体跟踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体跟踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持从已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：最近一周内有多次功能性更新和 Bug 修复，开发非常活跃
- **功能持续演进**：近期新增了身体跟踪相关的序列导出控制、动画序列导出等新功能
- **代码质量**：包含专门的测试模块（`MetaHumanControlsConversionTest`），有良好的测试覆盖
- **模块化设计**：28 个模块清晰分离职责，从捕捉协议栈到渲染管线各司其职
- **平台支持**：支持 Win64、Linux、Mac 三平台

**推荐使用**：作为 Epic 官方 MetaHuman 工具链的核心组件，此插件处于积极维护状态，是创建 MetaHuman 角色的标准方式。建议通过编辑器 UI 使用，避免直接依赖其内部 C++ API（大部分为 Private 实现）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)