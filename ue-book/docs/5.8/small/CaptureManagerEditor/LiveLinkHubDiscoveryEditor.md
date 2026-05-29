# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产与工具） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

CaptureManagerEditor 是一个功能丰富的编辑器插件，专为虚拟制片（Virtual Production）工作流设计。其核心用途是将来自外部设备（如 iPhone 上的 RealityCapture 应用）的捕获数据（包含图片、视频、点云等）作为存档文件导入到 Unreal Engine 或 Unreal Editor for Fortnite (UEFN) 中，并自动化创建一系列可用于进一步开发（如场景重建、资产导入）的基础资产。它本质上是连接外部捕获设备与 UE 内容创建流程的桥梁和管理工具。

**LiveLinkHubDiscoveryEditor 模块**的具体功能是：作为 LiveLink Hub 的一部分，它负责在局域网内响应来自外部设备（Capture Device）的发现请求。这使得运行在 Unreal Editor 中的 LiveLink Hub 能够被外部设备自动发现并建立连接，从而实现捕获数据的传输。它是整个插件网络发现机制的关键组件。

## 使用场景

- **虚拟制片现场**：你正在使用 iPhone 等设备捕获高清视频或扫描场景，需要将捕获的数据快速、自动地导入到正在运行的 UE5 虚拟制片项目中，用于实时场景构建或资产替换。
- **资产流水线**：你的团队有一个标准化的捕获工作流，需要将捕获的原始数据自动处理并导入 UE，作为动画、场景或数字孪生资产的一部分。
- **设备管理**：你需要在 UE 编辑器界面中查看、连接并管理连接到本地网络的所有捕获设备，并监控其数据传输状态。

## 蓝图用法

从提供的模块源码分析，`LiveLinkHubDiscoveryEditor` 模块本身没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它的核心功能（网络发现响应）在模块启动时自动初始化并在内部运行，不直接供蓝图调用。

其他模块（如 `CaptureManagerIngestBlueprint`、`CaptureManagerDeviceBlueprint`）很可能提供了相关的蓝图接口，用于控制导入流程或与设备交互，但这些不在当前文档的范围内。

## C++ 用法

由于该模块功能相对封闭，且没有提供公共接口，开发者通常**不会直接在其他 C++ 代码中调用 `LiveLinkHubDiscoveryEditor`**。它的作用是在插件内部自动工作。

以下代码展示了该模块的标准实现模式，对于理解其生命周期和作为依赖模块时的行为很有帮助。

### 头文件引入

该模块的头文件为私有，外部代码通常无需引入。

### 基本用法

这是一个模块实现的基本骨架，展示了它如何管理其核心组件 `FDiscoveryResponder`。
（来源文件：`Private/LiveLinkHubDiscoveryEditorModule.h`, `Private/LiveLinkHubDiscoveryEditorModule.cpp`）

```cpp
// LiveLinkHubDiscoveryEditorModule.cpp
#include "LiveLinkHubDiscoveryEditorModule.h"
#include "DiscoveryResponder.h" // 内部使用

void FLiveLinkHubDiscoveryEditor::StartupModule()
{
    // 在模块启动时创建并初始化发现响应器
    DiscoveryResponder = MakeUnique<UE::CaptureManager::FDiscoveryResponder>();
}

void FLiveLinkHubDiscoveryEditor::ShutdownModule()
{
    // 在模块关闭时销毁发现响应器，停止网络响应
    DiscoveryResponder.Reset();
}

IMPLEMENT_MODULE(FLiveLinkHubDiscoveryEditor, LiveLinkHubDiscoveryEditor)
```

### 进阶用法

虽然外部代码不直接使用此模块，但理解其依赖关系对于构建包含此功能的自定义插件或工具至关重要。如果你需要实现类似的设备发现功能，可以参考 `FDiscoveryResponder` 的设计，它使用了 UE 的消息总线系统。

## Demo 示例

一个完整的、可编译的最小模块示例框架。它展示了 `LiveLinkHubDiscoveryEditor` 模块作为标准 UE 模块的生命周期管理方式。此示例本身不包含业务逻辑，仅作为模块结构参考。

**LiveLinkHubDiscoveryEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

// 前置声明内部类，避免在头文件中暴露实现细节
namespace UE::CaptureManager
{
    class FDiscoveryResponder;
}

class FLiveLinkHubDiscoveryEditor : public IModuleInterface
{
public:
    /** IModuleInterface 实现 */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    /** 负责实际网络发现响应的实例，模块生命周期内有效 */
    TUniquePtr<UE::CaptureManager::FDiscoveryResponder> DiscoveryResponder;
};
```

**LiveLinkHubDiscoveryEditorModule.cpp**
```cpp
#include "LiveLinkHubDiscoveryEditorModule.h"

// 包含具体实现的头文件（此处仅为示例，实际实现在Private中）
// #include "Private/DiscoveryResponder.h" // 假设实现存在

void FLiveLinkHubDiscoveryEditor::StartupModule()
{
    // 此处创建并初始化 FDiscoveryResponder 实例
    // 例如: DiscoveryResponder = MakeUnique<UE::CaptureManager::FDiscoveryResponder>();
}

void FLiveLinkHubDiscoveryEditor::ShutdownModule()
{
    // 此处确保清理和释放资源
    if (DiscoveryResponder)
    {
        DiscoveryResponder.Reset();
    }
}

IMPLEMENT_MODULE(FLiveLinkHubDiscoveryEditor, LiveLinkHubDiscoveryEditor)
```

## 模块依赖

根据模块的典型职责和头文件依赖推断（`FDiscoveryResponder` 依赖 `FLiveLinkHubExportServer` 和 `FLiveLinkHubWorkerManager`）：

| 模块 | 用途 |
|---|---|
| `LiveLinkHubExportServer` | 获取本地导出服务器的信息，用于在发现响应中告知设备连接地址。 |
| `LiveLinkHubWorkerManager` | 管理与外部设备的工作连接，可能用于验证或管理设备状态。 |
| `Messaging` (核心消息系统) | 使用 `FMessageEndpoint` 进行网络通信，接收和处理设备的发现请求。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将 DeviceBlueprint 中的设备相关术语通用化。 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将同步阻塞的数据摄入蓝图API移至专门的子类别。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增了 CaptureManagerDeviceBlueprint 模块。 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回滚了之前的某个变更（CL53274396）。 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次尝试添加 CaptureManagerDeviceBlueprint 模块。 |

### 维护评价

该插件（及 `LiveLinkHubDiscoveryEditor` 模块）于 **2025年2月** 创建，目前约1年历史，属于相对较新的功能。从近期（2026年4月）的提交记录看，插件仍在被**活跃开发和维护**中，近期的改动主要集中在完善蓝图API和添加新模块（DeviceBlueprint），这表明 Epic 正在持续增强其功能。

**推荐使用**：对于虚拟制片工作流，特别是需要与外部 RealityCapture 设备集成的项目，此插件是官方推荐的选择。由于它处于默认禁用 (`EnabledByDefault: false`) 状态，说明它可能依赖特定的工作流或硬件环境，使用时需按需手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- (官方文档链接缺失，`.uplugin` 中 `DocsURL` 为空)