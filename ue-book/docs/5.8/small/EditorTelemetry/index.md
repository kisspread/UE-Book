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
| 创建时间 | 2024-06-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTelemetry) | |

## 用途

EditorTelemetry 插件从 `StudioTelemetry` 核心中解耦并独立出来，专注于收集 Unreal Editor 编辑器内部的通用遥测事件。它通过预定义的、结构化的分析事件和跨度（Span），帮助 Epic 内部或启用遥测的团队评估开发者在编辑器中最常见工作流的效率，例如编辑器启动、资源加载、PIE 运行、烹饪过程以及各种核心系统（如 DDC、资产注册表）的性能。它为性能优化和工作流改进提供了数据基础。

## 使用场景

- **团队效率分析**：收集编辑器启动时间、资源打开时长等数据，量化评估开发者的工作效率。
- **性能瓶颈诊断**：通过跟踪加载、烹饪、着色器编译等耗时操作，定位编辑器或项目中的性能热点。
- **PIE（Play In Editor）稳定性监控**：记录 PIE 启动、加载、交互和关闭各阶段的时长与事件。
- **资源处理流程监控**：跟踪资产注册表扫描、DDC（Derived Data Cache）命中/缺失、虚拟资产处理等流程。

## 蓝图用法

该插件的 API 主要面向 C++，提供的公开接口（如 `FEditorTelemetry` 类）均在 C++ 头文件中定义，**未发现 `BlueprintCallable` 或 `BlueprintReadWrite` 标记的函数/属性**。因此，蓝图无法直接使用此插件的功能。遥测数据的触发和收集由插件内部逻辑或通过 C++ 代码调用其静态接口完成。

## C++ 用法

### 头文件引入

```cpp
#include "EditorTelemetry.h"
```

### 基本用法

核心功能通过单例 `FEditorTelemetry` 访问，用于管理遥测会话和记录事件。

```cpp
// 来自 Source/Public/EditorTelemetry.h

// 1. 获取单例实例
FEditorTelemetry& Telemetry = FEditorTelemetry::Get();

// 2. 开始一个遥测会话（通常在编辑器启动时调用）
Telemetry.StartSession();

// 3. 记录一个烹饪（Cooking）事件，附加上下文和自定义属性
TArray<FAnalyticsEventAttribute> MyAttributes;
MyAttributes.Emplace(TEXT("Platform"), TEXT("Win64"));
MyAttributes.Emplace(TEXT("NumAssetsCooked"), 1024);
Telemetry.RecordEvent_Cooking(TEXT("Package for Distribution"), MyAttributes);

// 4. 记录一个加载事件，包括耗时
Telemetry.RecordEvent_Loading(TEXT("Open Level: MainGame"), 2.5);

// 5. 结束遥测会话（通常在编辑器关闭时调用）
Telemetry.EndSession();
```

### 进阶用法

插件内部使用了多个 `IAnalyticsSpan` 来详细追踪编辑器不同阶段的性能跨度。开发者可以参考其内部实现，在自定义模块中注册工作流委托来采集更精细的数据。

```cpp
// 假设你有一个自定义的 TelemetryRouter
FTelemetryRouter MyRouter;

// 注册到编辑器遥测系统，以便接收工作流委托
// （此函数在插件内部被调用以注册默认的编辑器事件）
FEditorTelemetry::Get().RegisterCollectionWorkflowDelegates(MyRouter);
```

插件内部追踪的跨度（Span）包括但不限于：
- `Editor.Boot`：编辑器启动。
- `Editor.Initialize`：编辑器初始化。
- `Editor.Interact`：用户与编辑器交互。
- `Editor.LoadMap`：加载关卡。
- `PIE`、`PIE.Startup`、`PIE.LoadMap`：Play In Editor 的各个阶段。
- `Cooking`：烹饪过程。
- `Editor.AssetRegistryScan`：资产注册表扫描。

## Demo 示例

一个展示如何使用 `FEditorTelemetry` 基础接口的简单示例。

```cpp
// MyEditorUtils.h
#pragma once

#include "CoreMinimal.h"

class FMyEditorUtils
{
public:
    static void InitializeEditorTelemetry();
    static void ShutdownEditorTelemetry();
    static void ReportAssetOpenTime(const FString& AssetPath, double DurationSeconds);
};
```

```cpp
// MyEditorUtils.cpp
#include "MyEditorUtils.h"
#include "EditorTelemetry.h"
#include "Interfaces/IAnalyticsProvider.h"

void FMyEditorUtils::InitializeEditorTelemetry()
{
    // 初始化遥测会话
    FEditorTelemetry::Get().StartSession();
    UE_LOG(LogTemp, Log, TEXT("Editor Telemetry session started."));
}

void FMyEditorUtils::ShutdownEditorTelemetry()
{
    // 结束遥测会话
    FEditorTelemetry::Get().EndSession();
    UE_LOG(LogTemp, Log, TEXT("Editor Telemetry session ended."));
}

void FMyEditorUtils::ReportAssetOpenTime(const FString& AssetPath, double DurationSeconds)
{
    // 记录一个自定义的“加载”事件，携带资产路径和耗时
    FEditorTelemetry::Get().RecordEvent_Loading(
        FString::Printf(TEXT("Open Asset: %s"), *AssetPath),
        DurationSeconds
    );
}
```

## 模块依赖

待补充（需分析 `EditorTelemetry.Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames`）。

| 模块 | 用途 |
|---|---|
| `Analytics` | 提供 `IAnalyticsProvider`、`IAnalyticsSpan` 等核心遥测接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数时产生的编译器警告。 |
| 2026-04-21 | `837e0aa4` | Updated validation stats analytics to be an embedded JSON array, rather than N separate named events | 将验证统计的遥测数据改为嵌入式JSON数组格式，替代之前多个独立的命名事件。 |
| 2026-04-16 | `ed49b260` | Updated validation stats analytics to be an embedded JSON blob, rather than N separate named events | 将验证统计的遥测数据改为嵌入式JSON对象格式。 |
| 2026-04-16 | `9870b120` | Declare that several Developer modules only support desktop platforms | 声明多个开发者模块仅支持桌面平台。 |
| 2026-01-28 | `a5dc63a6` | Fixed missing Shader Stats from Cook Event | 修复了烹饪事件中缺少着色器统计数据的问题。 |

### 维护评价

- **活跃维护**：最后一次提交距今约6个月，期间有多次功能性改进（如JSON数据格式优化）和错误修复。
- **稳定演进**：作为实验性插件，从创建至今保持活跃，代码结构清晰，专注于核心遥测功能。
- **推荐使用**：适用于需要深度分析编辑器性能和工作流的团队。由于是实验性插件（位于`Experimental`目录下），在主要版本更新时可能会有接口变动，建议关注更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTelemetry)
- [测试用例](待补充)