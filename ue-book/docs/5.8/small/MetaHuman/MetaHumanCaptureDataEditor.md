# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 角色动画工具链。它解决的核心问题是：**如何将真实演员的面部表演（通过 iPhone LiDAR、视频素材或音频）快速、高精度地驱动 MetaHuman 虚拟角色**。

整个插件包含 28 个模块，覆盖了完整的面部动画管线：

1. **采集层**（Capture）：从各种来源（iPhone 原深感摄像头、视频文件、Live Link 面捕设备）采集面部表演数据
2. **追踪层**（Tracking）：对面部轮廓、面部网格进行逐帧追踪
3. **拟合层**（Fitting）：将追踪结果拟合到 MetaHuman 面部骨骼控制器（ControlRig）
4. **求解层**（Solver）：面部动画求解器，将追踪数据转换为动画曲线
5. **深度生成**（Depth）：从单目视频生成深度信息
6. **语音驱动**（Speech2Face）：仅凭音频生成面部动画
7. **批量处理**（Batch）：大批量素材的自动化处理
8. **编排管线**（Pipeline）：各处理步骤的串联编排

## 使用场景

- 你有 iPhone 拍摄的面部表演录像 → 用 MetaHuman Capture Source + Face Contour Tracker + Face Fitting Solver 生成动画
- 你只有音频文件想驱动角色说话 → 用 MetaHuman Speech2Face 模块
- 你需要为大批量拍摄素材自动处理 → 用 MetaHuman Batch Processor
- 你要创建完整的 MetaHuman 角色身份 → 用 MetaHuman Identity 模块
- 你需要在 Sequencer 中编辑面部动画 → 用 MetaHuman Sequencer 模块
- 你想从视频提取深度信息用于追踪 → 用 MetaHuman Depth Generator

## 子模块概览

由于本插件包含 28 个模块（544+ 源文件），属于 **xlarge** 规模，以下按功能域分类说明：

| 功能域 | 模块 | 说明 |
|---|---|---|
| 核心基础 | `MetaHumanCore`, `MetaHumanCoreEditor` | 核心类型定义、编辑器基础设施 |
| 数据配置 | `MetaHumanConfig`, `MetaHumanConfigEditor` | 配置数据管理 |
| 素材采集 | `MetaHumanCaptureSource`, `MetaHumanCaptureUtils`, `MetaHumanCaptureProtocolStack` | 捕获数据导入与协议栈 |
| 素材编辑 | `MetaHumanCaptureDataEditor`, `MetaHumanImageViewerEditor` | 捕获数据的编辑器 UI |
| 素材导入 | `MetaHumanFootageIngest` | 影视素材导入流程 |
| 面部追踪 | `MetaHumanFaceContourTracker`, `MetaHumanFaceContourTrackerEditor` | 面部轮廓追踪 |
| 深度生成 | `MetaHumanDepthGenerator` | 单目深度估计 |
| 面部拟合 | `MetaHumanFaceFittingSolver`, `MetaHumanFaceFittingSolverEditor` | 面部网格拟合求解 |
| 动画求解 | `MetaHumanFaceAnimationSolver`, `MetaHumanFaceAnimationSolverEditor` | 追踪数据到动画曲线的转换 |
| 语音驱动 | `MetaHumanSpeech2Face` | 音频驱动面部动画 |
| 角色身份 | `MetaHumanIdentity`, `MetaHumanIdentityEditor` | MetaHuman 角色身份创建 |
| 性能动画 | `MetaHumanPerformance` | 表演数据管理 |
| 管线编排 | `MetaHumanPipeline` | 处理步骤串联编排 |
| 批量处理 | `MetaHumanBatchProcessor` | 大批量素材自动化处理 |
| Sequencer | `MetaHumanSequencer` | Sequencer 集成 |
| 网格追踪 | `MeshTrackerInterface` | 网格追踪接口抽象 |
| 平台支持 | `MetaHumanPlatform` | 平台相关适配 |
| 工具集 | `MetaHumanToolkit` | 通用工具函数 |
| 控制器转换测试 | `MetaHumanControlsConversionTest` | 控制器数据转换的自动化测试 |

---

## MetaHumanCaptureDataEditor 模块

> 当前聚焦模块 — 提供捕获数据（Capture Data）的编辑器界面和工具

### 用途

MetaHumanCaptureDataEditor 为捕获数据提供编辑器侧的 UI 控件和工具函数。它主要解决：

1. **摄像机选择**：当素材包含多个摄像机视角时，提供下拉选择控件
2. **预览组件创建**：为不同类型的捕获数据创建对应的 3D 预览组件
3. **数据变更响应**：当源素材（视频/音频）发生变化时，联动更新编辑器 UI

### 蓝图用法

本模块主要提供编辑器 Slate 控件，不直接暴露蓝图节点。核心功能通过 C++ 编辑器扩展使用。

### C++ 用法

#### 头文件引入

```cpp
#include "CaptureDataUtils.h"
```

#### 基本用法 — 创建预览组件

为任意 `UCaptureData` 类型的资产创建对应的 3D 预览组件：

```cpp
#include "CaptureDataUtils.h"
#include "Engine/World.h"

// 假设你有一个 UCaptureData 对象（如 UFootageCaptureData）
UCaptureData* CaptureData = /* ... */;

// 创建预览组件用于在编辑器视口中显示捕获数据
USceneComponent* PreviewComponent = MetaHumanCaptureDataUtils::CreatePreviewComponent(
    CaptureData,    // 捕获数据资产
    OuterObject     // Outer 对象（通常是编辑器工具实例）
);

if (PreviewComponent)
{
    // 预览组件已创建，可附加到编辑器 Actor 上显示
    PreviewComponent->RegisterComponent();
}
```

#### 摄像机选择控件

`SMetaHumanCameraCombo` 是一个 Slate 复合控件，用于在属性编辑器中提供摄像机下拉选择：

```cpp
#include "SMetaHumanCameraCombo.h"

// 创建摄像机选项列表
TArray<TSharedPtr<FString>> CameraOptions;
CameraOptions.Add(MakeShared<FString>(TEXT("CameraA")));
CameraOptions.Add(MakeShared<FString>(TEXT("CameraB")));

// 在 Slate 层级中构造控件
TSharedRef<SMetaHumanCameraCombo> CameraCombo = SNew(SMetaHumanCameraCombo)
    .InOptionsSource(&CameraOptions)
    .InCamera(&SelectedCamera)
    .InPropertyOwner(PropertyOwnerObject)
    .InProperty(PropertyHandle);
```

### Demo 示例

以下展示如何在编辑器工具中集成捕获数据预览：

```cpp
// MyCaptureDataTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyCaptureDataTool.generated.h"

class UCaptureData;
class USceneComponent;

UCLASS()
class UMyCaptureDataTool : public UObject
{
    GENERATED_BODY()

public:
    /** 设置要预览的捕获数据 */
    void SetCaptureData(UCaptureData* InCaptureData);

    /** 获取当前预览组件 */
    USceneComponent* GetPreviewComponent() const { return PreviewComponent; }

private:
    UPROPERTY()
    TObjectPtr<UCaptureData> CaptureData;

    UPROPERTY()
    TObjectPtr<USceneComponent> PreviewComponent;
};
```

```cpp
// MyCaptureDataTool.cpp
#include "MyCaptureDataTool.h"
#include "CaptureDataUtils.h"
#include "CaptureData/CaptureData.h"

void UMyCaptureDataTool::SetCaptureData(UCaptureData* InCaptureData)
{
    // 清理旧的预览组件
    if (PreviewComponent)
    {
        PreviewComponent->DestroyComponent();
        PreviewComponent = nullptr;
    }

    CaptureData = InCaptureData;

    // 为新的捕获数据创建预览组件
    if (CaptureData)
    {
        PreviewComponent = MetaHumanCaptureDataUtils::CreatePreviewComponent(
            CaptureData, this
        );
    }
}
```

## 模块依赖

以下是本插件独特的依赖模块（已省略 Core/Engine/Slate 等标准模块）：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | MetaHumanCaptureDataEditor 的直接依赖，提供图像查看器编辑器功能 |
| `MetaHumanCoreTechLib` | MetaHumanConfig 依赖，核心技术计算库 |
| `SkeletalMeshUtilitiesCommon` | MetaHumanIdentity 依赖，骨骼网格体通用工具 |
| `ControlRigDeveloper` | MetaHumanIdentity 依赖，ControlRig 开发者工具 |
| `MetaHumanSDKEditor` | MetaHumanIdentity 依赖，MetaHuman SDK 编辑器接口 |

**注意**：如果你只需要使用捕获数据编辑功能，只需依赖 `MetaHumanCaptureDataEditor` 及其传递依赖 `MetaHumanImageViewerEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **活跃维护**：最近更新集中在 2026 年 5 月，持续有功能更新和 Bug 修复
- **更新频率**：日级别更新，非常活跃
- **更新质量**：涵盖功能增强（动画序列导出）、Bug 修复（渲染瑕疵、缓存问题）、行为优化（追踪过滤）
- **整体规模**：28 个模块、544+ 源文件，是 UE5 中最大的功能插件之一
- **推荐度**：⭐⭐⭐⭐⭐ — Epic Games 官方维护的旗舰级工具链，如果你在做 MetaHuman 角色动画，这是必备插件

**注意**：此插件默认未安装（`Installed: false`），需要从 Epic Games 商业许可渠道获取或单独启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)（MetaHuman Animator 官方文档）