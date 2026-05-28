# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、模型资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-01-27 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个功能齐全的工具集，旨在支持从多种来源（如 iPhone 捕获、专业摄像设备、音频文件等）创建高保真度 MetaHuman 角色的完整工作流。它不仅仅是一个简单的导入工具，而是覆盖了捕获、追踪、求解、配置和最终导出的整个管线。其核心目标是简化从现实世界表演数据到可用于游戏或影视的实时数字人资产的创建过程，解决了专业级数字人制作中数据复杂、步骤繁多、技术门槛高的问题。

该插件是一个大型、模块化的架构，每个模块专注于管线中的一个特定阶段（如面部轮廓追踪、深度生成、动画求解等），并通过“管线” (`MetaHumanPipeline`) 模块进行编排。其中 `MetaHumanFootageIngest` 模块已经于 5.7 版本被标记为废弃，其功能已被整合到独立的 `CaptureManager` 模块中。

## 使用场景

-   **游戏开发**：为游戏创建基于真实演员表演的、具有电影级质感的主要角色。
-   **影视预览与虚拟制片**：快速生成用于预览的数字人替身，或用于虚拟制片中的实时数字人演员。
-   **虚拟直播与VTuber**：创建用于实时驱动的高保真虚拟形象。
-   **快速原型制作**：利用 iPhone 等消费级设备快速验证角色动画设计。

## 蓝图用法

由于该插件的大部分功能是通过编辑器工具和自定义资产（如 `UMetaHumanIdentity`）实现的，纯粹的运行时蓝图节点较少。其核心工作流主要在编辑器 UI 内完成。

### 核心资产与类

| 资产/类 | 说明 |
|---|---|
| `UMetaHumanIdentity` | 核心资产，用于存储一个 MetaHuman 角色从捕获数据到最终配置的整个创建过程数据。 |
| `UMetaHumanCaptureSource` | 代表一个捕获数据源（如特定的 iPhone 录制会话）。 |
| `UMetaHumanPerformance` | 存储单个表演录制的元数据，与 `UMetaHumanCaptureSource` 关联。 |
| `FCaptureManager` (已废弃) | 用于打开和控制捕获管理器的单例接口。 |

### 使用示例（蓝图描述）

虽然主要工作流在编辑器中，但可以在蓝图中触发特定动作：
1.  通过 `FCaptureManager::Get()->Show()` 蓝图节点，可以以编程方式打开捕获管理器窗口。
2.  可以使用 `FCaptureManager::Get()->ShowMonitoringTab(UMetaHumanCaptureSource*)` 节点，为指定的捕获源打开实时监控标签页。

## C++ 用法

该插件提供了丰富的 C++ API 用于程序化控制管线。以下示例基于公开的头文件和典型用法。

### 头文件引入

根据你要使用的具体功能，需要包含相应模块的头文件。例如，要操作核心身份资产：
```cpp
#include "MetaHumanIdentity/Public/MetaHumanIdentity.h"
```

### 基本用法（程序化创建身份）

以下代码展示了如何以编程方式创建一个新的 `UMetaHumanIdentity` 资产。
*（基于公开头文件和引擎资产创建惯例推断）*

```cpp
// 创建一个新的 MetaHuman 身份资产
UPackage* Package = CreatePackage(TEXT("/Game/MyMetaHumans/BP_NewCharacter"));
UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>(Package, TEXT("MHI_NewCharacter"), RF_Public | RF_Standalone);
// 然后可以调用 NewIdentity 的方法来导入捕获数据、配置头部、应用预设等
FAssetRegistryModule::AssetCreated(NewIdentity);
Package->FullyLoad();
Package->SetDirtyFlag(true);
```

### 进阶用法（操作捕获管理器 - 已废弃 API）

注意：以下 API 已在 5.7 废弃，仅供理解历史逻辑。
*（基于 `CaptureManager.h`）*

```cpp
#include "MetaHumanFootageIngest/Public/CaptureManager.h"

// 获取捕获管理器单例并显示窗口
if (FCaptureManager* CaptureManager = FCaptureManager::Get())
{
    CaptureManager->Show();
    
    // 假设我们有一个 UMetaHumanCaptureSource 对象指针 (MyCaptureSource)
    // 为它打开一个监控标签页
    if (UMetaHumanCaptureSource* MyCaptureSource = /* ... */)
    {
        TWeakPtr<SDockTab> MonitoringTab = CaptureManager->ShowMonitoringTab(MyCaptureSource);
    }
}
```

## Demo 示例

一个最小示例，演示如何检查 MetaHuman Animator 插件是否已加载，并尝试打开已废弃的捕获管理器（仅作演示，实际开发应使用新的 CaptureManager 模块）。
*`MetaHumanAnimatorDemo.h`*
```cpp
#pragma once
#include "CoreMinimal.h"

class FMetaHumanAnimatorDemo
{
public:
    static void TryOpenLegacyCaptureManager();
};
```
*`MetaHumanAnimatorDemo.cpp`*
```cpp
#include "MetaHumanAnimatorDemo.h"
#include "Modules/ModuleManager.h"

// 包含已废弃头文件，编译器会发出警告
PRAGMA_DISABLE_DEPRECATION_WARNINGS
#include "MetaHumanFootageIngest/Public/CaptureManager.h"
PRAGMA_ENABLE_DEPRECATION_WARNINGS

void FMetaHumanAnimatorDemo::TryOpenLegacyCaptureManager()
{
    // 检查插件模块是否加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("MetaHumanFootageIngest")))
    {
        UE_LOG(LogTemp, Warning, TEXT("MetaHumanFootageIngest module is loaded (deprecated). Opening legacy Capture Manager..."));
        if (FCaptureManager* CaptureMgr = FCaptureManager::Get())
        {
            CaptureMgr->Show();
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MetaHumanFootageIngest module is not loaded. Please check plugin installation."));
    }
}
```

## 模块依赖

MetaHuman Animator 是一个庞大的插件，依赖众多内部和外部模块。以下列出一些**独特且关键**的依赖，使用你的模块时可能需要引用。

| 模块 | 用途 |
|---|---|
| `MetaHumanSDK` / `MetaHumanSDKEditor` | 核心 MetaHuman SDK，提供基础类型和接口。 |
| `ControlRig` / `ControlRigDeveloper` | 用于驱动 MetaHuman 角色的控制系统。 |
| `MeshTrackerInterface` | 用于集成外部设备（如深度摄像头）的追踪接口。 |
| `MetaHumanCoreTechLib` | Epic 提供的底层面部拟合、求解等核心算法库。 |
| `HairStrands` | 用于处理 MetaHuman 的高精度头发系统。 |

*（注意：由于模块众多，且依赖关系复杂，实际使用特定功能时需参考其对应模块的 Build.cs 文件。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，可能为修复功能冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 启用身体追踪时过滤可视化对象，优化性能或显示。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 新增为现有网格体导出动画序列的功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存问题。 |

### 维护评价

-   **状态**：**活跃维护中**。插件于 2023 年初引入，近期更新（2026年）非常频繁，主要集中在功能增强（如身体追踪、序列导出）和 bug 修复。
-   **发展趋势**：插件正在积极演进，部分旧模块（如 `MetaHumanFootageIngest`）已被重构或废弃，新功能（如 `CaptureManager`）正在集成，表明其架构在持续优化。
-   **推荐度**：**强烈推荐**。作为 Epic 官方推出的 MetaHuman 创建工具链，它是 UE5 中制作高保真数字人的首选且最完整的解决方案。尽管部分 API 可能随版本更新而变动，但核心功能和工作流已趋于稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档（暂无特定URL，请参考 Epic 官方 MetaHuman 文档页面）
- 测试用例（插件内部分模块有 `Test` 后缀的模块，如 `MetaHumanControlsConversionTest`，通常位于各模块的 `Tests` 目录下）