# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman 工作流提供的官方工具集插件。它不仅仅是一个简单的组件，而是一个庞大的、模块化的生态系统，旨在将现实世界的演员表演（通过视频或深度相机捕捉）无缝地转移到 MetaHuman 虚拟角色的面部和身体上。其核心目的是解决从真实世界表演数据到高保真数字资产的自动化转换流程问题，涵盖了素材导入、面部追踪、动画求解、资产编辑和最终集成到 Sequencer 中进行影视制作或实时演示的完整管线。它让没有深厚技术背景的美术师和动画师也能高效地创建逼真的角色动画。

## 使用场景

-   **数字人创建**：你正在使用 MetaHuman Creator 创建一个高保真数字人角色，并需要将一段演员的面部表演视频赋予这个角色 → 使用 MetaHuman Animator 的 `MetaHumanIdentity` 和 `MetaHumanFaceFittingSolver` 模块来对齐和驱动角色。
-   **批量处理**：你有大量的面部表演视频片段需要批量转换为 MetaHuman 动画数据 → 使用 `MetaHumanBatchProcessor` 模块。
-   **表演捕捉**：你使用了 iPhone 的 LiDAR 或其他深度相机进行面部捕捉，并希望将这些深度数据与视频对齐以生成更精确的追踪点 → 使用 `MetaHumanDepthGenerator` 和 `MetaHumanCaptureUtils` 模块。
-   **自定义追踪区域**：默认的面部轮廓追踪点不能满足你对特定表情（如夸张的卡通表情）的精确控制需求 → 使用 `MetaHumanFaceContourTrackerEditor` 模块来创建和编辑自定义的追踪资产。
-   **语音驱动表情**：你只有音频素材，希望快速生成一个基础的唇形同步动画 → 使用 `MetaHumanSpeech2Face` 模块进行快速原型设计。
-   **影视集成**：你已完成动画制作，需要在 Unreal Sequencer 中精细调整动画曲线或与摄像机镜头同步 → 使用 `MetaHumanSequencer` 模块提供的 Sequencer 功能。

## 蓝图用法

由于 MetaHuman Animator 主要是编辑器工具和处理管线，其核心功能通常通过编辑器 UI（如专门的资产编辑器、右键菜单、处理面板）触发，而非直接的蓝图节点。用户主要交互的是资产（如 `UMetaHumanFaceContourTrackerAsset`）和流程（如在处理管线中拖拽节点）。

### 核心节点/交互

| 节点/交互 | 说明 | 所在类/资产 |
|---|---|---|
| **创建面部轮廓追踪资产** | 在内容浏览器中右键，选择“MetaHuman > Face Contour Tracker” 创建新资产 | `UMetaHumanFaceContourTrackerAssetFactoryNew` |
| **编辑追踪点** | 双击打开面部轮廓追踪资产，进入专用编辑器调整追踪点位置 | `UAssetDefinition_MetaHumanFaceContourTracker` |
| **在处理管线中使用** | 在 MetaHuman Pipeline 编辑器中，将“Face Contour Tracker”节点添加到数据处理流中 | `MetaHumanPipeline` 模块 |

### 使用示例（蓝图描述）

1.  **创建自定义追踪配置**：在内容浏览器空白处右键 -> “MetaHuman” -> “Face Contour Tracker”。这将通过 `UMetaHumanFaceContourTrackerAssetFactoryNew` 创建一个新的 `UMetaHumanFaceContourTrackerAsset`。
2.  **配置追踪点**：双击新创建的资产，在打开的专用编辑器（由 `UAssetDefinition_MetaHumanFaceContourTracker` 定义）中，你可以可视化地调整面部追踪点（Contour）的位置和权重，以适应你的特定角色网格或表演风格。
3.  **应用追踪配置**：在 MetaHuman Animator 的主处理流程中（例如，在设置一个新的 MetaHuman Identity 时），选择你自定义的追踪资产，替代默认配置，从而影响整个面部追踪和动画求解过程。

## C++ 用法

### 头文件引入

要编程方式创建或管理面部轮廓追踪资产，你需要包含相关模块的头文件。

```cpp
#include "MetaHumanFaceContourTrackerAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"
```

### 基本用法

以下代码演示了如何通过 C++ 代码创建一个新的 `UMetaHumanFaceContourTrackerAsset` 对象，其内部逻辑与 `UMetaHumanFaceContourTrackerAssetFactoryNew::FactoryCreateNew` 类似。

```cpp
// 创建一个新的面部轮廓追踪资产
UObject* NewTrackerAsset = NewObject<UMetaHumanFaceContourTrackerAsset>(
    GetTransientPackage(), // 或者指定一个具体的父包
    TEXT("MyCustomTracker"),
    RF_Transient | RF_Public
);

// 将资产注册到 Asset Registry (通常在保存到磁盘时由编辑器自动处理)
FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();
// ... 这里通常需要补充注册信息，如包路径、类型等
```

### 进阶用法

结合 `UAssetDefinition_MetaHumanFaceContourTracker` 的功能，你可以在编辑器中以编程方式打开资产进行编辑。

```cpp
// 假设你已经有一个 UMetaHumanFaceContourTrackerAsset* TrackerAsset
UAssetDefinition_MetaHumanFaceContourTracker* AssetDefinition = GetDefault<UAssetDefinition_MetaHumanFaceContourTracker>();

// 构造一个 FAssetOpenArgs
FAssetOpenArgs OpenArgs;
OpenArgs.Assets.Add(TrackerAsset);

// 调用 OpenAssets 方法来在编辑器中打开该资产进行编辑
AssetDefinition->OpenAssets(OpenArgs);
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在编辑器工具中创建一个简单的面部轮廓追踪资产并打印其基本信息。

```cpp
// MyFaceContourTrackerDemo.h
#pragma once

#include "CoreMinimal.h"

class FMyFaceContourTrackerDemo
{
public:
    static void CreateAndLogTrackerAsset();
};
```

```cpp
// MyFaceContourTrackerDemo.cpp
#include "MyFaceContourTrackerDemo.h"
#include "MetaHumanFaceContourTrackerAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "UObject/SavePackage.h"

void FMyFaceContourTrackerDemo::CreateAndLogTrackerAsset()
{
    // 1. 创建资产对象
    FString AssetName = TEXT("DemoFaceContourTracker");
    FString PackagePath = TEXT("/Game/MetaHuman/Demo/");
    FString FullPackageName = PackagePath + AssetName;

    UPackage* Package = CreatePackage(*FullPackageName);
    UMetaHumanFaceContourTrackerAsset* NewAsset = NewObject<UMetaHumanFaceContourTrackerAsset>(
        Package,
        *AssetName,
        RF_Public | RF_Standalone | RF_Transactional
    );

    // 2. (此处可添加自定义追踪点配置逻辑)
    // NewAsset->SetContourPoints(...);

    // 3. 标记资产为已修改并保存
    NewAsset->MarkPackageDirty();
    FAssetRegistryModule::AssetCreated(NewAsset);

    // 保存包到磁盘
    FString PackageFileName = FPackageName::LongPackageNameToFilename(FullPackageName, FPackageName::GetAssetPackageExtension());
    FSavePackageArgs SaveArgs;
    SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
    if (!Package->SavePackage(Package, nullptr, *PackageFileName, SaveArgs))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to save asset: %s"), *FullPackageName);
        return;
    }

    UE_LOG(LogTemp, Display, TEXT("Successfully created and saved MetaHuman Face Contour Tracker asset at: %s"), *FullPackageName);
}
```

## 模块依赖

`MetaHumanFaceContourTrackerEditor` 是一个运行时模块，但它依赖于核心的追踪模块和一个编辑器模块来提供完整的资产定义功能。

| 模块 | 用途 |
|---|---|
| `MetaHumanFaceContourTracker` | 提供面部轮廓追踪器资产 (`UMetaHumanFaceContourTrackerAsset`) 的核心数据结构和逻辑。 |
| `MetaHumanImageViewerEditor` | 提供图像查看器编辑器功能，可能用于在追踪资产编辑器中预览或关联面部图像/视频。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 缓存问题。 |

### 维护评价

MetaHuman Animator 是一个 **活跃维护** 的核心工具插件。从近期的 git 提交记录可以看出，开发团队正在持续进行功能增强（如身体追踪集成、动画序列导出）、bug 修复（渲染瑕疵、缓存问题）以及工作流优化。创建时间虽然未知，但插件版本号为 5.0.0，且包含大量深度功能模块，表明它是 UE5 时代推出的重要工具链的一部分，年龄较新。考虑到 Epic Games 对 MetaHuman 生态系统的战略投入，此插件预计将获得长期、稳定的更新和支持。**推荐在相关的 MetaHuman 数字人项目中使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (插件内未提供 DocsURL，需查阅 Epic Games 官网 MetaHuman 部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (包含特定模块的测试，但整个插件可能没有独立的集成测试目录)