# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 创作工具集的核心插件。它解决的核心问题是：**如何从视频素材（如 iPhone 深度摄像头拍摄的片段）创建高保真、可驱动的数字人角色**。

该插件并非一个单一功能，而是一个庞大的工具箱，包含了从素材导入、面部追踪、动画求解到最终资产生成的完整工作流。它使得在 Unreal Engine 内部完成从“拍摄”到“驱动”的全流程成为可能，是 MetaHuman 技术栈中连接原始捕捉数据与引擎内可交互角色的关键桥梁。

## 使用场景

- **制作虚拟主播/数字人**：你有一段演员的面部表演视频，希望将其驱动到一个 MetaHuman 角色上，用于直播或实时交互。
- **游戏开发**：为游戏中的 NPC 或主角创建基于真实演员表演的面部动画，提升角色表现力。
- **影视预览**：在虚拟制片流程中，快速将现场表演同步到数字替身上，进行实时预览。
- **批量处理**：需要处理大量捕捉数据，将其转换为可用的动画资产。

## 蓝图用法

由于 MetaHuman Animator 主要是一个编辑器和数据处理工具集，其核心功能大多通过编辑器 UI、资产操作和 C++ API 暴露，而非传统的蓝图节点。`MetaHumanCoreEditor` 模块主要提供编辑器扩展和设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetaHumanAssetCategoryPath` | 获取 MetaHuman 资产在编辑器内容浏览器中的分类路径 | `IMetaHumanCoreEditorModule` |
| `GetMetaHumanAdvancedAssetCategoryPath` | 获取 MetaHuman 高级资产的分类路径 | `IMetaHumanCoreEditorModule` |

### 使用示例（蓝图描述）

在蓝图中直接使用此插件的功能较少。主要的交互方式是：
1.  **通过编辑器 UI**：在内容浏览器中右键，使用“MetaHuman”相关菜单导入捕捉数据、创建 Identity 资产等。
2.  **通过资产操作**：创建和编辑 `UMetaHumanIdentity`、`UMetaHumanPerformance` 等资产。
3.  **通过 C++ 接口**：在自定义编辑器工具或自动化流程中调用其模块接口。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"
```

### 基本用法

获取 MetaHuman 编辑器模块接口，用于查询资产分类路径。
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCoreEditor/Public/MetaHumanCoreEditorModule.h`）

```cpp
// 获取模块接口
IMetaHumanCoreEditorModule& MetaHumanEditorModule = FModuleManager::GetModuleChecked<IMetaHumanCoreEditorModule>(TEXT("MetaHumanCoreEditor"));

// 获取资产分类路径，可用于自定义资产工厂或内容浏览器扩展
TConstArrayView<FAssetCategoryPath> AssetPaths = MetaHumanEditorModule.GetMetaHumanAssetCategoryPath();
```

### 进阶用法

访问和监听编辑器设置的变化。
（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCoreEditor/Public/MetaHumanEditorSettings.h`）

```cpp
// 获取编辑器设置对象（单例）
UMetaHumanEditorSettings* Settings = GetMutableDefault<UMetaHumanEditorSettings>();

// 读取设置
bool bForceSerial = Settings->bForceSerialIngestion;
int32 ABResolution = Settings->MaximumResolution;

// 监听设置变化
Settings->OnSettingsChanged.AddLambda([]()
{
    // 当用户在编辑器偏好设置中修改了 MetaHuman 相关选项时，此处会被调用
    UE_LOG(LogTemp, Log, TEXT("MetaHuman Editor Settings changed!"));
});
```

## Demo 示例

一个最小示例，展示如何在编辑器工具中获取 MetaHuman 模块接口并读取设置。

**MyMetaHumanTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyMetaHumanTool
{
public:
    void Initialize();
    void PrintSettings();
};
```

**MyMetaHumanTool.cpp**
```cpp
#include "MyMetaHumanTool.h"
#include "MetaHumanCoreEditorModule.h"
#include "MetaHumanEditorSettings.h"

void FMyMetaHumanTool::Initialize()
{
    // 确保 MetaHumanCoreEditor 模块已加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("MetaHumanCoreEditor")))
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHumanCoreEditor module is loaded."));
    }
}

void FMyMetaHumanTool::PrintSettings()
{
    const UMetaHumanEditorSettings* Settings = GetDefault<UMetaHumanEditorSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("Force Serial Ingestion: %s"), Settings->bForceSerialIngestion ? TEXT("True") : TEXT("False"));
        UE_LOG(LogTemp, Log, TEXT("A/B Split Max Resolution: %d"), Settings->MaximumResolution);
    }
}
```

## 模块依赖

`MetaHumanCoreEditor` 模块的依赖如下（从其 Build.cs 推断）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供底层算法和数据结构支持 |

## 维护状态

### 近期更新

```
- 2025-10-03 c43d0b06117 Make MH NNE models set the specific backend used and not to All #rb none
- 2025-09-15 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 2025-08-20 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
```

### 维护评价

- **创建时间**：2024年初，相对较新。
- **近期更新**：最近3次提交均在2025年内，内容涉及神经网络引擎后端优化和代码质量改进，表明插件仍在**积极维护和迭代**。
- **活跃度**：作为 Epic 官方旗舰级 MetaHuman 工具链的核心部分，其维护优先级很高。
- **已知限制**：插件默认未安装（`Installed: false`），需要用户手动启用。它依赖于特定的平台（Win64, Linux）和可能的外部服务（如用于云处理的 MetaHuman 服务）。
- **推荐使用**：**强烈推荐**给所有需要创建和驱动 MetaHuman 角色的项目。它是官方支持、功能完整且持续更新的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (暂无直接链接，请参考 Epic Games 官方 MetaHuman 文档)