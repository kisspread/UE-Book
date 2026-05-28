# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、配置、工具） |
| 模块 | `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
MetaHuman Animator 是一套完整的、官方的 MetaHuman 角色动画制作工具链。它解决了将真实演员的面部表演（通常通过 iPhone、立体相机或专业动捕设备录制）转化为高质量 MetaHuman 数字角色动画的核心问题。该插件提供了一条从原始视频或深度数据捕获、跟踪、求解、到最终在 UE 中生成可驱动骨骼动画序列的完整工作流，是 Epic 官方推荐的 MetaHuman 角色“开箱即用”动画解决方案。

## 使用场景
- 你是一位影视或游戏开发者，需要将真实演员的面部表演无缝地转移到数字 MetaHuman 角色上。
- 你正在为一部数字人电影或高质量游戏过场动画制作内容，需要高保真且高效的面部动捕流水线。
- 你拥有使用 iPhone 的 FaceID 传感器或深度相机捕获的视频素材，希望快速生成可用于游戏引擎中的角色动画。
- 你需要集成自定义的面部追踪器或动画求解器到 MetaHuman 工作流中。
- 你正在开发一个实时虚拟主播或数字人驱动应用，并希望利用 MetaHuman 的资产和动画系统。

## 蓝图用法
基于 `MetaHumanCoreEditor` 模块的源码分析，此插件主要提供编辑器扩展和底层处理功能，其核心类并非直接面向蓝图的可调用节点，而是通过编辑器工具（如工具栏按钮、资产编辑器）和资产导入工厂来使用。不过，它暴露了一些可在蓝图中读取的设置属性。

### 核心节点 (基于 UMetaHumanEditorSettings)
该插件通过 `UMetaHumanEditorSettings` 类暴露了可在“项目设置”中编辑的配置项，这些属性可以通过蓝图函数 `GetDefault<UMetaHumanEditorSettings>()` 访问（需在编辑器环境下）。

| 属性 (在蓝图中读取) | 说明 | 所在类 |
|---|---|---|
| `SampleCount` | 控制 A/B 分割窗口的采样数，影响质量和内存占用。 | `UMetaHumanEditorSettings` |
| `MaximumResolution` | 设置 A/B 分割窗口的最大有效分辨率。 | `UMetaHumanEditorSettings` |
| `bForceSerialIngestion` | 是否强制让摄取过程串行运行。 | `UMetaHumanEditorSettings` |
| `bShowDevelopersContent` | 是否在捕获管理器中显示开发者内容文件夹下的捕获源。 | `UMetaHumanEditorSettings` |
| `bLoadTrackersOnStartup` | 是否在打开 Identity 时加载追踪器。 | `UMetaHumanEditorSettings` |
| `PerformanceViewSetupSlot1` ~ `Slot4` | 存储 Performance 编辑器视图设置的槽位。 | `UMetaHumanEditorSettings` |

### 使用示例（蓝图描述）
你无法直接将 MetaHuman Animator 的核心处理流程用蓝图节点串联。主要的交互方式是：
1.  **配置设置**：在“编辑”->“项目设置”->“插件”->“MetaHuman Animator”类别下，调整 `UMetaHumanEditorSettings` 中的参数。
2.  **使用工具**：通过插件提供的编辑器 UI（如资产编辑器、工具栏菜单）进行工作流操作。例如，通过“捕获源”资产摄取视频，通过“Identity”资产进行拟合，通过“Performance”资产驱动最终动画。
3.  **编程访问设置**：在编辑器工具蓝图中，可以使用 C++ 函数库或通过类默认对象获取设置值。一个简化的蓝图描述可能是：创建一个编辑器工具，该工具在运行时获取 `UMetaHumanEditorSettings` 的默认对象，然后读取其 `bShowDevelopersContent` 属性来决定是否在 UI 列表中显示某些捕获源。

## C++ 用法
此插件的复杂性主要体现在其庞大的模块体系和编辑器工具中，直接面向开发者的 C++ API 相对内部。以下示例基于 `MetaHumanCoreEditor` 模块的公开头文件。

### 头文件引入
```cpp
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"
```

### 基本用法
获取 MetaHuman 插件模块接口，用于查询其提供的资产类别路径。这对于在自定义编辑器中组织 MetaHuman 相关资产很有用。
*来源: `Public/MetaHumanCoreEditorModule.h`*

```cpp
// 在编辑器模块中获取 MetaHuman Core Editor 模块接口
if (IMetaHumanCoreEditorModule* MetaHumanCoreEditorModule = FModuleManager::GetModulePtr<IMetaHumanCoreEditorModule>(TEXT("MetaHumanCoreEditor")))
{
    // 获取 MetaHuman 标准资产类别路径
    TConstArrayView<FAssetCategoryPath> Categories = MetaHumanCoreEditorModule->GetMetaHumanAssetCategoryPath();
    for (const FAssetCategoryPath& Category : Categories)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Asset Category: %s"), *Category.ToString());
    }

    // 获取 MetaHuman 高级资产类别路径
    TConstArrayView<FAssetCategoryPath> AdvancedCategories = MetaHumanCoreEditorModule->GetMetaHumanAdvancedAssetCategoryPath();
    // ... 可用于在内容浏览器中创建资产过滤菜单等
}
```

### 进阶用法
直接修改编辑器设置并响应设置变更。这可用于创建自定义的设置面板或工具。
*来源: `Public/MetaHumanEditorSettings.h`*

```cpp
// 获取可修改的编辑器设置实例
UMetaHumanEditorSettings* EditorSettings = GetMutableDefault<UMetaHumanEditorSettings>();

// 检查并修改一个设置
if (EditorSettings && !EditorSettings->bShowDevelopersContent)
{
    EditorSettings->bShowDevelopersContent = true;
    // 保存设置
    EditorSettings->SaveConfig();
    UE_LOG(LogTemp, Warning, TEXT("Enabled showing developer content in MetaHuman Capture Manager."));
}

// 监听设置变更
EditorSettings->OnSettingsChanged.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("MetaHuman Editor Settings were changed!"));
    // 执行相应逻辑，例如刷新UI
});
```

## Demo 示例
一个最小化的编辑器工具类，演示如何集成 MetaHuman Core Editor 模块并读取其设置。
*注意：这是一个编辑器工具，需要创建在编辑器模块中（例如 .Build.cs 中 `Type = Editor`）。*

**MetaHumanDemoTool.h**
```cpp
// MetaHumanDemoTool.h
#pragma once
#include "CoreMinimal.h"

class FMetaHumanDemoTool
{
public:
    static void Run();
};
```

**MetaHumanDemoTool.cpp**
```cpp
// MetaHumanDemoTool.cpp
#include "MetaHumanDemoTool.h"
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"

void FMetaHumanDemoTool::Run()
{
    // 1. 查询模块信息
    if (IMetaHumanCoreEditorModule* Module = FModuleManager::GetModulePtr<IMetaHumanCoreEditorModule>(TEXT("MetaHumanCoreEditor")))
    {
        const auto& Categories = Module->GetMetaHumanAssetCategoryPath();
        if (Categories.Num() > 0)
        {
            UE_LOG(LogTemp, Display, TEXT("Found MetaHuman asset category: %s"), *Categories[0].ToString());
        }
    }

    // 2. 读取和展示设置
    const UMetaHumanEditorSettings* Settings = GetDefault<UMetaHumanEditorSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Display, TEXT("MetaHuman Settings - Serial Ingestion: %s, Show Dev Content: %s"),
            Settings->bForceSerialIngestion ? TEXT("true") : TEXT("false"),
            Settings->bShowDevelopersContent ? TEXT("true") : TEXT("false"));
    }

    UE_LOG(LogTemp, Display, TEXT("MetaHuman Demo Tool Executed."));
}
```

## 模块依赖
此插件包含大量内部模块，对外部开发者的依赖主要体现在数据类型和核心框架上。根据模块命名和常见实践，典型的依赖如下（需在你的模块 `.Build.cs` 中添加）：

| 模块 | 用途 |
|---|---|
| `MetaHumanIdentity` | 如果需要与 MetaHuman 角色身份资产交互 |
| `MetaHumanPerformance` | 如果需要与 MetaHuman 表演资产交互 |
| `ControlRig` | 核心动画控制和驱动系统 |
| `SkeletalMesh` | 处理骨骼网格体数据 |
| `MediaAssets` | 处理视频/音频媒体资产（用于捕获源） |
| `ImageWrapper` | 处理图像格式（用于导入捕获数据） |
| `MovieScene` / `LevelSequence` | 序列器和过场动画系统（用于输出动画序列） |
| `CameraCalibrationCore` | 如果涉及相机标定数据 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用体部跟踪时禁用关卡序列导出，避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在体部跟踪时过滤可视化对象，优化显示 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列，功能增强 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存导致的问题 |

### 维护评价
MetaHuman Animator 插件**处于活跃维护状态**。从 git 提交历史可以看出，它在近期（2026年5月）仍有密集的功能性更新和 bug 修复，包括新功能（如对现有网格体导出动画）、重要问题修复（渲染伪影、缓存问题）以及对新工作流（体部跟踪）的支持优化。作为 Epic Games 官方的 MetaHuman 核心工具，其维护优先级很高，是构建高质量数字人项目的**强烈推荐**使用的插件。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档链接未在 .uplugin 中提供，建议查阅 Unreal Engine 官方文档站的 MetaHuman 相关部分。
- 测试用例路径未在提供信息中明确，通常位于插件内部的 `Tests` 目录或引擎的 `Tests/Plugins` 目录下。