# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 动画资产、配置模板） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色面部动画制作工具包。它解决的核心问题是：**如何从原始视频素材、音频录音等输入源，自动生成高质量的 MetaHuman 面部动画数据**。

该插件提供了一条完整的处理管线（Pipeline），涵盖以下关键环节：

1. **素材采集与导入**：从视频片段（Footage）和音频文件中提取面部数据
2. **面部轮廓追踪**：通过计算机视觉算法从视频帧中检测和追踪面部特征点与轮廓
3. **面部网格拟合**：将追踪到的 2D/3D 特征点拟合到 MetaHuman 面部骨骼网格上
4. **面部动画求解**：从拟合结果中计算出最终的面部控制参数（Blend Shapes / Control Rigs）
5. **深度图生成**：从单目视频生成深度信息以提升追踪精度
6. **语音驱动面部动画（Speech2Face）**：仅从音频输入生成合理的面部动画
7. **身份管理**：管理 MetaHuman 角色的身份资产，关联面部模板与追踪数据
8. **批量处理**：对多个素材进行自动化批量处理
9. **Sequencer 集成**：将生成的动画数据直接导入 Sequencer 时间线

简而言之，这个插件让开发者能够**用一段手机拍摄的面部视频，驱动一个高保真的 MetaHuman 角色做出完全匹配的表情和口型动画**。

## 使用场景

- 你有一段演员的面部表演视频，想驱动 MetaHuman 角色 → 使用 **MetaHumanCaptureSource** 导入素材，通过 **FaceContourTracker** + **FaceFittingSolver** + **FaceAnimationSolver** 管线处理
- 你只有音频录音，想生成合理的口型动画 → 使用 **MetaHumanSpeech2Face** 模块
- 你需要为多个镜头批量生成面部动画 → 使用 **MetaHumanBatchProcessor** 进行自动化处理
- 你正在搭建自定义的面部追踪管线 → 使用 **MetaHumanPipeline** 框架组合各处理节点
- 你需要在 Sequencer 中编辑和微调生成的面部动画 → 使用 **MetaHumanSequencer** 集成模块
- 你需要管理多个 MetaHuman 角色的身份和面部模板 → 使用 **MetaHumanIdentity** 资产管理

## 模块概览

本插件包含 28 个模块，按功能可分为以下几组：

### 核心基础

| 模块 | 说明 |
|---|---|
| `MetaHumanCore` | 核心运行时功能，基础数据类型和工具 |
| `MetaHumanCoreEditor` | 核心编辑器扩展 |
| `MetaHumanConfig` | 配置管理，依赖 MetaHumanCoreTechLib |
| `MetaHumanConfigEditor` | 配置编辑器 UI |
| `MetaHumanPlatform` | 平台抽象层，处理跨平台差异 |

### 素材采集与导入

| 模块 | 说明 |
|---|---|
| `MetaHumanCaptureSource` | 捕获数据源管理，支持多种输入格式 |
| `MetaHumanCaptureUtils` | 捕获相关工具函数 |
| `MetaHumanCaptureProtocolStack` | 捕获协议栈，处理设备通信 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器，提供预览和相机选择 UI |
| `MetaHumanFootageIngest` | 视频素材导入处理 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器组件 |

### 面部追踪与拟合

| 模块 | 说明 |
|---|---|
| `MetaHumanFaceContourTracker` | 面部轮廓追踪算法 |
| `MetaHumanFaceContourTrackerEditor` | 面部轮廓追踪编辑器扩展 |
| `MeshTrackerInterface` | 网格追踪接口抽象 |
| `MetaHumanFaceFittingSolver` | 面部网格拟合求解器 |
| `MetaHumanFaceFittingSolverEditor` | 面部拟合求解器编辑器扩展 |
| `MetaHumanDepthGenerator` | 从单目视频生成深度图 |

### 动画求解

| 模块 | 说明 |
|---|---|
| `MetaHumanFaceAnimationSolver` | 面部动画求解器，将拟合结果转为动画数据 |
| `MetaHumanFaceAnimationSolverEditor` | 动画求解器编辑器扩展 |
| `MetaHumanSpeech2Face` | 语音驱动面部动画生成 |

### 身份与管线

| 模块 | 说明 |
|---|---|
| `MetaHumanIdentity` | MetaHuman 身份资产管理 |
| `MetaHumanIdentityEditor` | 身份资产编辑器 |
| `MetaHumanPipeline` | 处理管线框架，组合各处理节点 |
| `MetaHumanBatchProcessor` | 批量处理引擎 |

### 集成与工具

| 模块 | 说明 |
|---|---|
| `MetaHumanPerformance` | 表演数据管理 |
| `MetaHumanSequencer` | Sequencer 时间线集成 |
| `MetaHumanToolkit` | 综合工具集 |

### 测试

| 模块 | 说明 |
|---|---|
| `MetaHumanControlsConversionTest` | 控制参数转换测试 |

## 蓝图用法

> **注意**：MetaHuman Animator 主要是一个 C++ / 编辑器工具链插件，大部分功能通过编辑器 UI 面板操作，而非蓝图节点。以下列出可在蓝图中使用的有限 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePreviewComponent` | 为捕获数据创建预览场景组件 | `MetaHumanCaptureDataUtils` |

### 使用示例

MetaHuman Animator 的主要工作流通过编辑器面板完成：

1. 在 Content Browser 中右键创建 **MetaHuman Identity** 资产
2. 导入面部视频素材到 Identity 资产中
3. 通过编辑器面板依次执行：追踪 → 拟合 → 动画求解
4. 将结果输出到 Sequencer 或导出动画数据

## C++ 用法

### 头文件引入

```cpp
// 捕获数据工具
#include "CaptureDataUtils.h"

// 相机选择 UI 组件
#include "SMetaHumanCameraCombo.h"
```

### 基本用法

以下示例展示如何为捕获数据创建预览组件：

```cpp
// 来源: MetaHumanCaptureDataEditor/Public/CaptureDataUtils.h

#include "CaptureDataUtils.h"
#include "CaptureData.h"

// 为指定的捕获数据创建预览场景组件
UCaptureData* CaptureData = /* 获取捕获数据资产 */;
UObject* Owner = /* 拥有者对象，通常是编辑器中的资产 */;

USceneComponent* PreviewComponent = MetaHumanCaptureDataUtils::CreatePreviewComponent(
    CaptureData, 
    Owner
);

if (PreviewComponent)
{
    // 预览组件已创建，可以添加到场景中
    PreviewComponent->RegisterComponent();
}
```

### 进阶用法

使用 `SMetaHumanCameraCombo` 在自定义编辑器面板中创建相机选择下拉框：

```cpp
// 来源: MetaHumanCaptureDataEditor/Public/SMetaHumanCameraCombo.h

#include "SMetaHumanCameraCombo.h"

// 准备相机选项列表
TArray<TSharedPtr<FString>> CameraOptions;
CameraOptions.Add(MakeShared<FString>(TEXT("Camera_0")));
CameraOptions.Add(MakeShared<FString>(TEXT("Camera_1")));

FString SelectedCamera = TEXT("Camera_0");

// 创建相机选择下拉框
TSharedRef<SMetaHumanCameraCombo> CameraCombo = SNew(SMetaHumanCameraCombo);

// 初始化组件，绑定属性
CameraCombo->Construct(
    FArguments(),
    &CameraOptions,
    &SelectedCamera,
    PropertyOwner,          // TObjectPtr<UObject> 属性所有者
    PropertyHandle          // TSharedPtr<IPropertyHandle> 属性句柄
);

// 当源数据变化时更新下拉框
CameraCombo->HandleSourceDataChanged(FootageCaptureData, SoundWave, true);

// 当不需要音频时
CameraCombo->HandleSourceDataChanged(true);  // bInResetRanges
```

## Demo 示例

以下是一个最小化的编辑器工具示例，展示如何集成 MetaHuman Capture Data 编辑功能：

```cpp
// MyMetaHumanTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CaptureDataUtils.h"
#include "SMetaHumanCameraCombo.h"

class UCaptureData;
class UFootageCaptureData;

class FMyMetaHumanTool
{
public:
    /** 为捕获数据创建预览 */
    static USceneComponent* PreviewCaptureData(UCaptureData* InCaptureData, UObject* InOwner);

    /** 构建相机选择 UI */
    static TSharedRef<SMetaHumanCameraCombo> CreateCameraSelector(
        const TArray<TSharedPtr<FString>>& InCameras,
        const FString& InCurrentCamera,
        UObject* InPropertyOwner,
        TSharedPtr<IPropertyHandle> InProperty
    );
};
```

```cpp
// MyMetaHumanTool.cpp
#include "MyMetaHumanTool.h"

USceneComponent* FMyMetaHumanTool::PreviewCaptureData(
    UCaptureData* InCaptureData, 
    UObject* InOwner)
{
    if (!InCaptureData || !InOwner)
    {
        return nullptr;
    }

    return MetaHumanCaptureDataUtils::CreatePreviewComponent(InCaptureData, InOwner);
}

TSharedRef<SMetaHumanCameraCombo> FMyMetaHumanTool::CreateCameraSelector(
    const TArray<TSharedPtr<FString>>& InCameras,
    const FString& InCurrentCamera,
    UObject* InPropertyOwner,
    TSharedPtr<IPropertyHandle> InProperty)
{
    TSharedRef<SMetaHumanCameraCombo> Combo = SNew(SMetaHumanCameraCombo);
    Combo->Construct(
        FArguments(),
        &InCameras,
        &InCurrentCamera,
        InPropertyOwner,
        InProperty
    );
    return Combo;
}
```

## 模块依赖

以下为本插件各模块的**独特依赖**（非常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供底层算法支持 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器接口 |
| `ControlRigDeveloper` | Control Rig 开发者工具，用于面部骨骼控制 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格通用工具，用于面部网格处理 |
| `MetaHumanImageViewerEditor` | 图像查看器，被多个编辑器模块依赖 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器，被 Identity 模块依赖 |

> **注意**：由于本插件包含 28 个模块，各模块之间存在大量内部依赖。使用特定功能时，需在你的 `.Build.cs` 中引用对应的模块。

## 维护状态

### 近期更新

```
- 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
- 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

- **创建时间**：2024-02-02，约 1 年前从 Epic 内部仓库迁移至公开源码
- **迁移状态**：该插件于 2024 年从 Epic 的 restricted（受限）仓库迁移至公开 UE 源码，公开 git 历史较短是正常的
- **活跃程度**：作为 Epic Games 官方 MetaHuman 工具链的核心组件，该插件在 Epic 内部持续活跃开发。公开仓库中的更新主要是代码规范化（如 dllstorage 修复）
- **平台支持**：仅支持 Win64 和 Linux，不支持 macOS/主机平台
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐。这是 Epic 官方的 MetaHuman 面部动画解决方案，是目前 UE5 中最权威的面部动捕工具链。如果你的项目使用 MetaHuman 角色并需要从视频生成面部动画，这是唯一官方且推荐的方案

> ⚠️ **注意**：该插件默认未启用（`Installed: false`），需要在项目设置中手动启用。部分功能可能需要额外的 MetaHuman 技术库支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/)
- [MetaHuman Creator](https://metahuman.unrealengine.com/)