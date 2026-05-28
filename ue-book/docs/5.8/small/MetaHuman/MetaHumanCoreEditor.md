# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工具、资产、材质等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-14 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具包，其核心目的是**从视频捕捉数据中创建和驱动逼真的 MetaHuman 面部动画**。它不仅仅是一个资产库，更是一套完整的工作流解决方案，解决了将真实演员的面部表演转化为虚拟角色动画的复杂过程。

它存在的意义在于：
1.  **标准化流程**：提供从数据捕捉（视频、深度等）、面部轮廓追踪、面部动画求解、到最终动画输出的标准化管道。
2.  **高质量求解**：集成复杂的面部解剖学模型和求解器（`MetaHumanFaceAnimationSolver`, `MetaHumanFaceFittingSolver`），能够生成保真度极高的面部变形和动画。
3.  **工作流集成**：与 Unreal Engine 的 Sequencer（`MetaHumanSequencer`）、Control Rig 等系统深度集成，方便后期编辑和混合。
4.  **规模化处理**：通过 `MetaHumanBatchProcessor` 模块支持批量处理，提高制作效率。

## 使用场景

-   **影视与虚拟制片**：需要将演员的实时或预录制表演无缝转移到数字人角色上。
-   **游戏过场动画**：为游戏角色生成基于真人表演的、高质量的口型同步和面部表情动画。
-   **虚拟主播/数字人**：驱动实时或离线的数字人形象。
-   **面部动画研究与开发**：作为面部动作捕捉和求解技术的官方参考实现和测试平台。

## 蓝图用法

由于 MetaHuman Animator 主要是一个面向工作流的工具集，其许多高级功能通过编辑器 UI 和资产操作暴露，而不是简单的蓝图节点。以下是从提供的公共头文件中提取的核心概念和 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetaHumanAssetCategoryPath` | 获取 MetaHuman 资产在编辑器中的分类路径 | `IMetaHumanCoreEditorModule` |
| `GetMetaHumanAdvancedAssetCategoryPath` | 获取 MetaHuman 高级资产在编辑器中的分类路径 | `IMetaHumanCoreEditorModule` |

### 使用示例（蓝图描述）

1.  **访问设置**：在项目设置（Project Settings）中，可以找到 `MetaHuman Editor Settings`（对应 `UMetaHumanEditorSettings` 类）。你可以通过蓝图或C++代码读取和修改这些设置，例如 A/B 对比窗口的采样数（`SampleCount`）、最大分辨率（`MaximumResolution`）以及是否强制顺序摄取（`bForceSerialIngestion`）。
2.  **资产导入**：`UMetaHumanCameraCalibrationImporterFactory` 是一个资产工厂，支持导入和重新导入相机标定文件。在编辑器中，你可以直接将相机标定文件拖放到内容浏览器中，它会由该工厂自动处理。

## C++ 用法

此插件的主要功能是通过编辑器模块和资产类型系统工作的，开发者通常会扩展或集成其模块，而不是直接调用底层 API。以下基于提供的头文件展示基本的模块和设置访问。

### 头文件引入

```cpp
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"
```

### 基本用法

**获取 MetaHuman 资产分类路径**
这是实现自定义资产浏览器或与 MetaHuman 资产类型交互的常见需求。
```cpp
// 获取MetaHuman核心编辑器模块
IMetaHumanCoreEditorModule& MetaHumanEditorModule = FModuleManager::GetModuleChecked<IMetaHumanCoreEditorModule>(TEXT("MetaHumanCoreEditor"));

// 获取标准的MetaHuman资产分类路径（用于资产创建菜单等）
TConstArrayView<FAssetCategoryPath> AssetPaths = MetaHumanEditorModule.GetMetaHumanAssetCategoryPath();

// 获取高级MetaHuman资产分类路径
TConstArrayView<FAssetCategoryPath> AdvancedAssetPaths = MetaHumanEditorModule.GetMetaHumanAdvancedAssetCategoryPath();
```
*来源文件: `Public/MetaHumanCoreEditorModule.h`*

**访问和修改编辑器设置**
MetaHuman Animator 的许多全局行为由 `UMetaHumanEditorSettings` 控制。
```cpp
// 获取默认的设置对象
UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();

if (Settings)
{
    // 修改设置（例如，强制串行处理以减少内存压力）
    Settings->bForceSerialIngestion = true;
    
    // 监听设置变化
    Settings->OnSettingsChanged.AddLambda([]()
    {
        // 处理设置变化逻辑
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Editor settings changed."));
    });
}
```
*来源文件: `Public/MetaHumanEditorSettings.h`*

### 进阶用法

**实现自定义相机标定文件处理器**
`UMetaHumanCameraCalibrationImporterFactory` 展示了如何处理自定义文件类型的导入和重新导入。你可以参考其实现，为 MetaHuman 工作流添加自定义数据格式的支持。
```cpp
// 这通常涉及继承 UFactory 和 FReimportHandler
// 关键是实现 FactoryCanImport, FactoryCreateFile 和 Reimport 方法
// 详见 MetaHumanCameraCalibrationImporterFactory.h 中的接口定义
```
*来源文件: `Public/MetaHumanCameraCalibrationImporterFactory.h`*

## Demo 示例

由于 MetaHuman Animator 是一个庞大的工具集，没有一个单一的“最小示例”。一个基础的集成示例是监听其编辑器设置的变化。

```cpp
// MyMetaHumanSettingsListener.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanSettingsListener.generated.h"

UCLASS()
class UMyMetaHumanSettingsListener : public UObject
{
    GENERATED_BODY()
public:
    void StartListening();
    void StopListening();

private:
    void OnMetaHumanSettingsChanged();
};
```

```cpp
// MyMetaHumanSettingsListener.cpp
#include "MyMetaHumanSettingsListener.h"
#include "MetaHumanEditorSettings.h"

void UMyMetaHumanSettingsListener::StartListening()
{
    UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
    if (Settings)
    {
        Settings->OnSettingsChanged.AddDynamic(this, &UMyMetaHumanSettingsListener::OnMetaHumanSettingsChanged);
    }
}

void UMyMetaHumanSettingsListener::StopListening()
{
    UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();
    if (Settings)
    {
        Settings->OnSettingsChanged.RemoveDynamic(this, &UMyMetaHumanSettingsListener::OnMetaHumanSettingsChanged);
    }
}

void UMyMetaHumanSettingsListener::OnMetaHumanSettingsChanged()
{
    // 响应MetaHuman编辑器设置变化，例如更新UI或重新配置流程
    UE_LOG(LogTemp, Warning, TEXT("MetaHuman settings have been updated!"));
}
```

## 模块依赖

此插件由多个模块组成，具有复杂的内部依赖关系。以下是为使用其核心功能，你的项目模块可能需要依赖的**独特（非标准）模块**：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心运行时模块，包含基础数据结构和功能。 |
| `MetaHumanCoreEditor` | MetaHuman 编辑器核心，提供资产分类和编辑器设置等基础功能。 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器，负责将追踪数据转换为动画。 |
| `MetaHumanFaceFittingSolver` | 面部拟合求解器，负责将通用网格拟合到特定面部。 |
| `MetaHumanCaptureSource` | 处理来自不同捕捉源（如视频、深度）的数据。 |
| `MetaHumanPerformance` | 处理和管理捕捉到的表演数据（Performance）。 |
| `MetaHumanPipeline` | 定义和管理从数据输入到动画输出的处理管道。 |
| `MetaHumanIdentity` | 管理 MetaHuman 身份资产，关联源数据、模板和求解结果。 |
| `MetaHumanSequencer` | 与 Sequencer 系统的集成，用于动画的编辑和播放。 |

*注：实际依赖关系请参考你具体集成的子模块的 `Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤掉不必要的可视化对象，优化性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 新增为已有网格体导出动画序列的功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存相关的问题。 |

### 维护评价

MetaHuman Animator 作为 Epic Games 的官方旗舰工具之一，处于**非常活跃的维护状态**。
-   **创建时间**：约 4 年，相对于 UE 插件生态系统来说较新。
-   **近期更新**：最近的提交（截至 2026 年 5 月）显示持续在进行功能改进（如导出动画序列）、Bug 修复（渲染瑕疵、缓存问题）和工作流优化（身体追踪集成）。
-   **维护状态**：**活跃维护中**。更新频率高，且内容涉及核心功能，表明 Epic 持续投入资源。
-   **推荐使用**：**强烈推荐**。如果你的项目涉及基于真人表演的 MetaHuman 面部动画，这是必选的官方工具。需要注意的是，它可能对硬件（特别是内存）和 UE 版本有特定要求。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Human/AnimationAndSolving/MetaHumanAnimatorOverview/) (通常可在 Epic 官方文档站找到)
-   测试用例：此插件的测试代码通常分散在其各个子模块（如 `MetaHumanControlsConversionTest`）中，路径可能为 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests/` 或各模块内的 `Tests/` 目录。