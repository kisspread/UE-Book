# Editor Telemetry

> Plugin that emits common telemetry events from the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器遥测 |
| 分类 | Telemetry |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorTelemetry` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-04-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorTelemetry) | |

## 用途

**Editor Telemetry** 是 UE5 编辑器内置的遥测插件，自动收集和报告编辑器中关键工作流的事件数据。它通过统一的 Analytics 接口，记录编辑器启动、地图加载、PIE（Play In Editor）启动/交互/关闭、内容烹饪、卡顿采样、Heartbeat 等常见操作的耗时和属性，帮助开发者评估编辑器性能与开发效率。该插件主要用于内部效率分析和用户行为统计，对最终开发者无直接功能干扰，但可通过禁用或修改配置来控制遥测数据的发送。

## 使用场景

- 你希望在编辑器使用过程中自动收集性能数据（如启动时间、加载时长、PIE 延迟等），用于分析团队开发效率。
- 你需要向 Epic 提供匿名使用数据以帮助改进 UE 编辑器（默认开启）。
- 你希望基于遥测数据自定义自己的分析管道，可通过 `FEditorTelemetry` 的 `RecordEvent_*` 接口手动上报事件。
- 你正在开发编辑器插件，并希望将自己的工作流事件纳入统一的遥测系统。

## 蓝图用法

该插件未暴露任何 `UFUNCTION` 或蓝图可访问的节点，所有 API 均为 C++ 编辑器模块接口。

## C++ 用法

### 头文件引入

```cpp
#include "EditorTelemetry.h"
```

### 基本用法

通过单例 `FEditorTelemetry::Get()` 访问，在编辑器模块中调用记录事件：

```cpp
// 记录一个烹饪事件（可附带自定义属性）
FEditorTelemetry::Get().RecordEvent_Cooking({ /* FAnalyticsEventAttribute 列表 */ });

// 记录一个加载事件，传入上下文和耗时（秒）
FEditorTelemetry::Get().RecordEvent_Loading(TEXT("LoadMap"), 2.5f);

// 记录一个核心系统事件
FEditorTelemetry::Get().RecordEvent_CoreSystems(TEXT("AssetRegistryScan"));

// 手动开始/结束遥测会话（通常在编辑器启动/关闭时自动调用）
FEditorTelemetry::Get().StartSession();
// ... 编辑器操作 ...
FEditorTelemetry::Get().EndSession();
```

### 进阶用法

插件内部自动注册了多个工作流委托（例如 PIE 启动、地图加载、烹饪），你可以在 `FTelemetryRouter` 中注册额外的事件收集器：

```cpp
#include "EditorTelemetry.h"
#include "TelemetryRouter.h" // 假设在内部实现

void MyCollector::Register(FTelemetryRouter& Router)
{
    // 通过 RegisterCollectionWorkflowDelegates 添加自定义收集
    FEditorTelemetry::Get().RegisterCollectionWorkflowDelegates(Router);
}
```

更多事件类型包括：
- `RecordEvent_DDCResource`（DDC 资源）
- `RecordEvent_DDCSummary`（DDC 汇总）
- `RecordEvent_Zen`（Zen 存储）
- `RecordEvent_VirtualAssets`（虚拟资产）
- `RecordEvent_MemoryLLM`（LLM 内存标记）

上述所有函数均接受一个可选的 `TArray<FAnalyticsEventAttribute>` 参数，用于传递自定义键值对。

## Demo 示例

以下是一个最小化的编辑器模块示例，在自定义 `StartupModule` 中通过 `FEditorTelemetry` 记录一次加载事件。

**MyTelemetryModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMyTelemetryModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyTelemetryModule.cpp**
```cpp
#include "MyTelemetryModule.h"
#include "EditorTelemetry.h"

void FMyTelemetryModule::StartupModule()
{
    // 调用遥测接口记录一个“自定义加载”事件，耗时 0.5 秒
    FEditorTelemetry::Get().RecordEvent_Loading(
        TEXT("MyCustomWorkflow"),
        0.5f,
        { FAnalyticsEventAttribute(TEXT("Source"), TEXT("Demo")) }
    );
}

void FMyTelemetryModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyTelemetryModule, MyTelemetryModule);
```

**注意**：示例需要你的项目模块依赖 `EditorTelemetry` 和 `Analytics`。

## 模块依赖

要在你的模块中使用 `EditorTelemetry`，需在 `Build.cs` 中添加以下依赖（`Public` 或 `Private` 均可，按需选择）：

| 模块 | 用途 |
|---|---|
| `EditorTelemetry` | 遥测插件主模块（必须） |
| `Analytics` | 提供 `IAnalyticsProvider` 接口和 `FAnalyticsEventAttribute` |
| `AnalyticsET` | （可选）如果使用默认的 Epic Telemetry 后端 |

除上述外，无需额外特殊依赖（标准 `Core`、`CoreUObject`、`Engine` 等已自动包含）。

## 维护状态

### 近期更新

```
- 2025-05-31 52e3dac1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types
- 2025-05-13 1521eda1 Rework on the UObjectClasses new TagSet for Insights to remove the necessity of adding `#if LLM_ALLO ...
- 2025-05-12 c87333f6 Rework on the UObjectClasses new TagSet for Insights ... （回退后重新提交）
- 2025-04-29 a873c04d Add a new set of LLM tags for the UObject scope ...
```

### 维护评价

- **创建时间**：2025-04-29，非常新的实验性插件。
- **更新频率**：创建后一个月内连续更新了 4 次，涉及头文件清理、LLM 标签调整等，表明团队正在积极开发。
- **活跃度**：最近一次更新在 2025-05-31，距现在不到半年，属于活跃维护。
- **推荐度**：该插件是编辑器默认启用的基础遥测组件，除非你明确禁用遥测，否则推荐保留开启。对于需要自定义编辑器分析的开发者，可以通过其 C++ 接口扩展。

> ⚠️ 由于插件处于早期实验阶段，API 和内部结构在后续版本中可能有变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorTelemetry)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/analytics-and-telemetry-in-unreal-engine/)（UE 通用遥测文档，非插件专属）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorTelemetry/Source/EditorTelemetry/Private)（插件源码内暂无独立测试文件）