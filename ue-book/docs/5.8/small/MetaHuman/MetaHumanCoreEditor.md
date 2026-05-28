# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、模板、动画数据） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🏛️ 文物 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的工具包，用于将真实演员的面部表演动画捕捉到数字人（MetaHuman）角色上。它解决的核心问题是：**如何将视频（或深度图像）中演员的面部动作，自动化地转移并驱动高保真度的 MetaHuman 虚拟角色**。该插件整合了从摄像机标定、面部追踪、动画求解、到最终驱动的全套流程，是 Epic 官方提供的数字人动捕核心解决方案。

## 使用场景

- **影视制作**：你正在制作一部使用数字人演员的短片，需要将真人演员的细腻表情实时（或离线）录制到 MetaHuman 角色中。
- **游戏过场动画**：你的游戏包含大量高质量的过场动画，需要高效地从面部捕捉数据生成角色动画序列。
- **虚拟主播/数字人直播**：你运营一个虚拟主播频道，需要通过摄像头实时驱动虚拟形象的面部表情。
- **研究与开发**：你正在研究计算机视觉、面部动画或实时渲染，需要一套包含数据采集、处理和可视化的完整工具链。

## 蓝图用法

### 编辑器设置与配置

由于该插件的核心是复杂的处理管线，大部分直接操作在专用编辑器中进行，但可以通过蓝图或 C++ 访问其全局设置。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Default` | 获取 MetaHuman Animator 的全局编辑器设置实例，用于查询或修改配置。 | `UMetaHumanEditorSettings` |

### 使用示例（蓝图描述）

在编辑器工具蓝图或编辑器 Utility Widget 中，可以访问并修改动画器的全局设置。
1. 添加一个 `Get MetaHumanEditorSettings` 节点（通过 `Get Default` 节点和 `UMetaHumanEditorSettings` 类实现）。
2. 你可以读取或设置 `bForceSerialIngestion` 属性，控制数据导入是串行还是并行。
3. 你可以调整 `PerformanceViewSetupSlot` 属性，为不同的查看模式保存和加载预设。
4. 设置变更会通过 `OnSettingsChanged` 委托广播。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"
#include "MetaHumanCameraCalibrationImporterFactory.h"
```

### 基本用法 - 读取编辑器设置

以下代码展示了如何访问全局的 MetaHuman Animator 编辑器设置。
（来源：`Public/MetaHumanEditorSettings.h` 及一般 UObject 用法）

```cpp
// 获取 MetaHuman Animator 编辑器设置的默认对象
UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
if (Settings)
{
    // 检查是否强制串行导入
    bool bSerial = Settings->bForceSerialIngestion;
    
    // 修改一个设置
    Settings->bShowDevelopersContent = true;
    // 保存设置（取决于具体配置，可能需要调用 SaveConfig）
}
```

### 进阶用法 - 使用模块接口注册资产分类

`IMetaHumanCoreEditorModule` 接口允许其他插件或模块将其资产注册到 MetaHuman 的资产浏览器分类中。
（来源：`Public/MetaHumanCoreEditorModule.h`）

```cpp
#include "Modules/ModuleManager.h"
#include "MetaHumanCoreEditorModule.h"

void RegisterMyAssets()
{
    // 获取 MetaHuman 编辑器模块
    IMetaHumanCoreEditorModule& MetaHumanCoreEditorModule = FModuleManager::GetModuleChecked<IMetaHumanCoreEditorModule>("MetaHumanCoreEditor");
    
    // 获取标准和高级资产分类路径
    TConstArrayView<FAssetCategoryPath> StandardPaths = MetaHumanCoreEditorModule.GetMetaHumanAssetCategoryPath();
    TConstArrayView<FAssetCategoryPath> AdvancedPaths = MetaHumanCoreEditorModule.GetMetaHumanAdvancedAssetCategoryPath();
    
    // 你可以在此使用这些路径来分类你自己的资产...
}
```

## Demo 示例

一个简单的 C++ 类，展示如何在编辑器中访问 MetaHuman Animator 设置。
`.h` 文件：
```cpp
// MyMetaHumanSettingsAccessor.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanSettingsAccessor.generated.h"

UCLASS()
class MYPROJECT_API UMyMetaHumanSettingsAccessor : public UObject
{
	GENERATED_BODY()

public:
	/** 获取当前是否应该显示开发者内容目录 */
	UFUNCTION(BlueprintCallable, Category = "MetaHuman Settings")
	bool ShouldShowDevelopersContent() const;
};
```
`.cpp` 文件：
```cpp
// MyMetaHumanSettingsAccessor.cpp
#include "MyMetaHumanSettingsAccessor.h"
#include "MetaHumanEditorSettings.h"

bool UMyMetaHumanSettingsAccessor::ShouldShowDevelopersContent() const
{
    const UMetaHumanEditorSettings* Settings = GetDefault<UMetaHumanEditorSettings>();
    return Settings ? Settings->bShowDevelopersContent : false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 系统的基础运行时核心功能。 |
| `MetaHumanCaptureSource` | 提供摄像头/视频数据源管理功能。 |
| `MetaHumanFaceContourTracker` | 面部轮廓关键点追踪核心算法。 |
| `MetaHumanFaceFittingSolver` | 将追踪数据拟合到 MetaHuman 面部模型的求解器。 |
| `MetaHumanFaceAnimationSolver` | 从拟合数据生成最终面部动画曲线的求解器。 |
| `MetaHumanIdentity` | 管理 MetaHuman 数字人身份资产。 |
| `MetaHumanPerformance` | 管理和编辑捕捉的表演数据（Performance）。 |
| `MetaHumanSequencer` | 将动画数据集成到 Sequencer 中播放。 |
| `MetaHumanPipeline` | 构建和执行数据处理管线。 |
| `ControlRigDeveloper` | 用于驱动 MetaHuman 的 Control Rig 开发支持。 |
| `SkeletalMeshUtilitiesCommon` | 处理骨骼网格体的通用工具。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供对外接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复了在启用身体追踪时可能导致关卡序列导出的问题。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 优化了身体追踪模式下的可视化对象过滤。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的网格体导出动画序列，增强了工作流灵活性。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 中的缓存问题，提升了播放稳定性。 |

### 维护评价

MetaHuman Animator 作为 Epic 官方数字人动捕的核心工具，处于 **活跃维护** 状态。从 git 历史看，近期（2026年5月）连续有多个提交，内容涉及功能增强（为已有网格导出动画）、Bug 修复（渲染瑕疵、缓存问题）以及体验优化（可视化过滤）。这表明该插件仍在持续开发和改进中，是可靠且推荐用于生产级数字人动画项目的工具。建议始终使用最新版本以获得最佳稳定性和功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （.uplugin 未提供）
- [测试用例]() （测试模块 `MetaHumanControlsConversionTest` 可在源码中查看）