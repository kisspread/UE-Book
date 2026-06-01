# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置、数据摄入工具） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

本插件是虚幻引擎中用于处理**捕获数据**的核心工具链。它解决的核心问题是：如何将外部设备（如移动扫描设备、摄影测量设备等）捕获的原始数据（称为“捕获档案”）自动化地导入到 UE 或 UEFN 中，并转换为引擎可用的标准资产（如静态网格体、纹理、材质等）。

插件通过蓝图和编辑器设置提供了可定制的数据摄入（Ingest）管线，集成了 LiveLink 功能用于设备发现和实时数据流，并管理后台工作线程以优化处理性能。它简化了从物理世界到数字资产创建的完整工作流程。

## 使用场景

- 你有一个使用摄影测量技术制作的 3D 扫描模型（如一个雕塑、一个房间），希望将其导入 UE 中作为游戏场景或虚拟制片的资产。**→ 使用此插件处理捕获档案**。
- 你的团队正在使用移动扫描设备（如手机App）批量捕获物体，并希望有一个标准化的流程将它们批量转换为 UE 资产。**→ 配置此插件的导入设置，实现自动化处理**。
- 你需要连接并管理通过 LiveLink 发现的捕获设备，并在编辑器中实时查看或导出其数据流。**→ 使用 LiveLink 集成模块**。

## 蓝图用法

本插件的核心蓝图功能分布在多个模块中，主要提供设备交互、数据导入和设置管理的能力。

### 核心节点

| 节点 | 说明 | 所在类/模块 |
|---|---|---|
| （设备蓝图相关） | 用于在蓝图中创建和管理捕获设备的抽象表示。 | `CaptureManagerDeviceBlueprint` |
| （摄入蓝图相关） | 提供阻塞和非阻塞的蓝图节点，用于执行数据摄入（导入）流程。 | `CaptureManagerIngestBlueprint` |
| （设置相关） | 在蓝图中读取或配置 CaptureManager 的编辑器和项目设置。 | `CaptureManagerEditorSettings` |

### 使用示例（蓝图描述）

典型的蓝图工作流可能如下：
1.  **设备连接**：使用 `LiveLinkHubDiscoveryEditor` 模块相关的蓝图函数来扫描并发现可用的捕获设备。
2.  **启动摄入**：在游戏逻辑或编辑器工具中，调用 `CaptureManagerIngestBlueprint` 模块提供的“开始摄入”函数，传入捕获档案的路径。
3.  **监控进度**：通过蓝图事件监听摄入过程的进度和完成状态。
4.  **资产生成**：插件在后台自动生成资产，完成后可以在 Content Browser 中找到。

## C++ 用法

对于高级用法或扩展插件功能，可以在 C++ 中直接使用其底层模块。

### 头文件引入

```cpp
// 根据需要引入具体模块的头文件
#include "DataIngestCoreEditor/DataIngestCoreEditor.h"
#include "LiveLinkHubWorkerManager/LiveLinkHubWorkerManager.h"
```

### 基本用法

C++ 层面主要用于扩展数据摄入管线或自定义工作线程逻辑。开发者通常不直接调用，而是通过插件提供的蓝图接口或编辑器UI进行操作。若要自定义数据处理流程，可能需要继承或修改 `DataIngestCoreEditor` 模块中的核心类。

### 进阶用法

与 LiveLink 系统深度集成。例如，通过 `LiveLinkHubWorkerManager` 模块管理自定义的导出服务器工作线程，实现特定格式的数据实时传输。这需要深入了解 LiveLink 协议和 Unreal 的多线程任务系统。

## Demo 示例

由于本插件是一个复杂的编辑器工具集，其“最小示例”是通过其编辑器UI操作一个示例捕获档案。一个典型的可编程集成示例如下：

**MyCustomIngestHandler.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyCustomIngestHandler.generated.h"

UCLASS()
class MYPROJECT_API UMyCustomIngestHandler : public UObject
{
    GENERATED_BODY()
public:
    // 可能用于自定义数据处理步骤的函数声明
    UFUNCTION(BlueprintCallable, Category = "Custom Ingest")
    void PostProcessAssets(const FString& AssetPath);
};
```

**MyCustomIngestHandler.cpp**
```cpp
#include "MyCustomIngestHandler.h"
// 需要包含相应模块的头文件来访问其内部类型和函数
// #include "DataIngestCoreEditor/IngestPipeline.h"

void UMyCustomIngestHandler::PostProcessAssets(const FString& AssetPath)
{
    // 调用插件的核心数据处理函数，或对已导入的资产进行自定义后处理
    // UE_LOG(LogTemp, Log, TEXT("Post-processing assets at: %s"), *AssetPath);
}
```

## 模块依赖

使用本插件时，你的模块需要依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `CaptureManagerIngestBlueprint` | 使用其提供的蓝图函数节点来触发导入流程。 |
| `LiveLink` / `LiveLinkInterface` | 与 LiveLink 设备发现和数据流功能进行交互。 |
| `AssetTools` | 涉及资产创建和导入的底层操作。 |
| `DesktopPlatform` | 处理文件对话框（如选择捕获档案）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 统一设备蓝图中的术语，使其更具通用性。 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式的摄入蓝图API移至专门的子类别，优化蓝图节点组织。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增设备蓝图模块，用于在蓝图中抽象表示捕获设备。 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回滚了某个提交，可能涉及不稳定的改动。 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 再次添加设备蓝图模块（可能修复了上一次回滚的问题）。 |

### 维护评价

**活跃维护中**。
- **创建时间**：约 1 年前（2025年2月），是一个相对新的插件。
- **近期活跃度**：在 2026年4月底有**密集的、实质性的功能更新**（新增设备蓝图模块、API重构），表明其正在积极开发和完善。
- **状态**：插件仍在功能迭代期，属于 **Virtual Production（虚拟制片）** 领域的关键工具。虽然默认未启用，但已具备完整的模块结构。
- **推荐**：**推荐关注和尝试**。对于从事虚拟制片、摄影测量资产处理的工作流，这是一个官方提供的重要工具链。由于其处于活跃开发期，使用时需关注版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档]() （.uplugin 中未提供 DocsURL）
- [测试用例]() （具体测试文件路径需进一步查找，通常位于 `Engine/Tests/` 或插件内部的 `Tests/` 目录）