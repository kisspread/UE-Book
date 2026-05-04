# World Metrics

> Provides access to the world metrics system

| 属性 | 值 |
|---|---|
| 分类 | Profiling |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WorldMetricsCore` (Runtime), `WorldMetricsTest` (Runtime), `CsvMetrics` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/WorldMetrics) | |

## 用途

WorldMetrics 是一个用于收集和管理世界级别运行时指标（metrics）的框架。它解决的核心问题是：**如何以可扩展、解耦的方式追踪游戏世界中的统计数据**（如 Actor 数量、内存使用等），并将这些数据输出到 CSV 性能分析工具。

该插件的设计模式是 "Subsystem + Metric + Extension" 三层架构：
- **Subsystem**（`UWorldMetricsSubsystem`）：世界子系统，负责管理所有 metric 和 extension 的生命周期，通过 ticker 定期调用 metric 的 `Update()` 方法
- **Metric**（`UWorldMetricInterface`）：具体的指标实现，如 Actor 计数、内存统计等。每个 metric 由 subsystem 拥有，按 ticker 频率更新
- **Extension**（`UWorldMetricsExtension`）：可共享的功能模块，通过 acquire/release 引用计数管理生命周期。多个 metric 可以共享同一个 extension（如 Actor 追踪器），当所有使用者释放后自动回收

这种设计允许不同的 metric 复用共同的追踪逻辑（如 Actor 增删事件），而无需每个 metric 各自监听世界事件。

## 使用场景

- 你需要在运行时收集世界级别的统计数据（Actor 数量、类型分布等）→ 用 WorldMetrics
- 你需要将游戏运行时数据导出到 CSV 进行性能分析 → 用 CsvMetrics 子模块
- 你需要多个系统共享同一份 Actor 追踪数据 → 用 `UWorldMetricsActorTracker` extension
- 你需要一个带引用计数的共享功能模块，自动管理生命周期 → 用 Extension 机制

## C++ 用法

### 头文件引入

```cpp
#include "WorldMetricsSubsystem.h"
#include "WorldMetricInterface.h"
#include "WorldMetricsExtension.h"
#include "WorldMetricCollection.h"
```

### 基本用法 — 自定义 Metric

继承 `UWorldMetricInterface` 实现自定义指标：

```cpp
// MyActorCountMetric.h
#pragma once
#include "WorldMetricInterface.h"
#include "MyActorCountMetric.generated.h"

UCLASS()
class UMyActorCountMetric : public UWorldMetricInterface
{
    GENERATED_BODY()
public:
    virtual SIZE_T GetAllocatedSize() const override { return 0; }
    int32 ActorCount = 0;

private:
    virtual void Initialize() override;
    virtual void Deinitialize() override;
    virtual void Update(float DeltaTimeInSeconds) override;
};
```

```cpp
// MyActorCountMetric.cpp
#include "MyActorCountMetric.h"
#include "WorldMetricsSubsystem.h"

void UMyActorCountMetric::Initialize()
{
    // 可在此获取 extension
}

void UMyActorCountMetric::Deinitialize()
{
    ActorCount = 0;
}

void UMyActorCountMetric::Update(float DeltaTimeInSeconds)
{
    // 定期更新逻辑
}
```

### 添加和移除 Metric

```cpp
// 获取 subsystem
UWorldMetricsSubsystem* Subsystem = UWorldMetricsSubsystem::Get(GetWorld());

// 方式 1：模板方法（自动创建并添加）
UMyActorCountMetric* Metric = Subsystem->AddMetric<UMyActorCountMetric>();

// 方式 2：工厂方法（仅创建，不自动添加）
UMyActorCountMetric* Metric2 = Subsystem->CreateMetric<UMyActorCountMetric>();
Subsystem->AddMetric(Metric2);

// 方式 3：仅创建对象（不添加到 subsystem）
UMyActorCountMetric* Metric3 = Subsystem->CreateMetric<UMyActorCountMetric>();

// 移除 metric（subsystem 释放引用，metric 可被 GC）
Subsystem->RemoveMetric(Metric);

// 遍历所有 metric
Subsystem->ForEachMetric([](const UWorldMetricInterface* M) {
    // 处理每个 metric
    return true; // 返回 false 中断遍历
});

// 遍历特定类型的 metric
Subsystem->ForEachMetricOfClass<UMyActorCountMetric>([](const UMyActorCountMetric* M) {
    UE_LOG(LogTemp, Log, TEXT("Actor count: %d"), M->ActorCount);
    return true;
});
```

来源：`WorldMetricsSubsystem.h`、`WorldMetricsSubsystem.cpp`

### Extension 机制

Extension 使用 acquire/release 引用计数语义。首次 acquire 时创建，最后一个 owner release 后自动销毁：

```cpp
// metric 初始化时获取 extension
void UMyMetric::Initialize()
{
    // 获取 ActorTracker extension（如果不存在则创建）
    GetOwner().AcquireExtension<UWorldMetricsActorTracker>(this);
}

// metric 反初始化时释放
void UMyMetric::Deinitialize()
{
    GetOwner().ReleaseExtension<UWorldMetricsActorTracker>(this);
}
```

Extension 之间也可以互相依赖（Extension A acquire Extension B），形成依赖链。当最顶层的 metric 被移除时，整个依赖链会自动级联释放。

来源：`WorldMetricsSubsystem.cpp` (AcquireExtensionInternal / ReleaseExtensionInternal)

### 使用 FWorldMetricCollection 批量管理

`FWorldMetricCollection` 提供了批量管理 metric 的容器，确保每个 metric 类型只存在一个实例：

```cpp
FWorldMetricCollection Collection;
Collection.Initialize(GetOuterObject()); // 需要提供能获取 World 的对象

// 添加 metric 类型（不会重复添加）
Collection.Add<UMyActorCountMetric>();
Collection.Add<UMyOtherMetric>();

// GetOrAdd：存在则获取，不存在则创建
UMyActorCountMetric* Metric = Collection.GetOrAdd<UMyActorCountMetric>();

// 启用：将所有 metric 添加到 subsystem 开始运行
Collection.Enable(true);

// 查询
bool bHas = Collection.Contains<UMyActorCountMetric>();
UMyActorCountMetric* Found = Collection.Get<UMyActorCountMetric>();
int32 Count = Collection.Num();

// 遍历
Collection.ForEach<UMyActorCountMetric>([](const UMyActorCountMetric* M) {
    return true;
});

// 禁用：从 subsystem 移除所有 metric
Collection.Enable(false);

// 重置：移除所有 metric 并禁用
Collection.Reset();
```

来源：`WorldMetricCollection.h`、`WorldMetricCollection.cpp`

### Actor Tracker Extension

`UWorldMetricsActorTracker` 是内置的 Extension，用于追踪世界中 Actor 的增删：

```cpp
// 在 metric 中使用
void UMyMetric::Initialize()
{
    GetOwner().AcquireExtension<UWorldMetricsActorTracker>(this);
}

// 实现 IWorldMetricsActorTrackerSubscriber 接口接收通知
void UMyMetric::OnActorAdded(const AActor* Actor)
{
    // Actor 所有组件已注册，已进入世界
}

void UMyMetric::OnActorRemoved(const AActor* Actor)
{
    // Actor 即将移除，指针在此之后失效
}
```

也可以使用轮询模式，不实现 subscriber 接口，直接在 `Update()` 中查询。

来源：`WorldMetricsActorTracker.h`、`WorldMetricsActorTracker.cpp`

### CsvMetrics — CSV 性能数据导出

`UCsvMetricsSubsystem` 用于在 CSV profiler 采集期间自动添加/移除 metric：

```cpp
// 在 DefaultEngine.ini 中配置
// [CsvMetrics]
// +MetricClasses=/Script/MyModule.MyCsvActorCountMetric
```

`UCsvActorCountMetric` 是内置的 CSV metric 示例，它：
1. 通过 `UWorldMetricsActorTracker` extension 追踪 Actor 增删
2. 按 native class name 分类统计 Actor 数量
3. 在 CSV profiler 采集期间，将超过阈值（默认 5）的 Actor 类型计数写入 CSV

可通过控制台变量调整阈值：
```
csv.RecordActorCountThreshold 10
```

来源：`CsvActorCountMetric.h`、`CsvActorCountMetric.cpp`、`CsvMetricsSubsystem.h`

## Demo 示例

### 最小自定义 Metric

```cpp
// MySimpleMetric.h
#pragma once
#include "WorldMetricInterface.h"
#include "MySimpleMetric.generated.h"

UCLASS()
class UMySimpleMetric : public UWorldMetricInterface
{
    GENERATED_BODY()
public:
    int32 FrameCount = 0;
    virtual SIZE_T GetAllocatedSize() const override { return 0; }
private:
    virtual void Update(float DeltaTimeInSeconds) override { ++FrameCount; }
    virtual void Deinitialize() override { FrameCount = 0; }
};
```

使用方式：
```cpp
// 在某个 UObject（如 GameInstance）中
UWorldMetricsSubsystem* Subsystem = UWorldMetricsSubsystem::Get(GetWorld());
UMySimpleMetric* Metric = Subsystem->AddMetric<UMySimpleMetric>();

// 读取数据
UE_LOG(LogTemp, Log, TEXT("Frames: %d"), Metric->FrameCount);

// 不再需要时移除
Subsystem->RemoveMetric(Metric);
```

Build.cs 依赖：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "WorldMetricsCore" });
```

### 带 Actor Tracker 的完整 Metric

```cpp
// ActorDensityMetric.h
#pragma once
#include "WorldMetricInterface.h"
#include "WorldMetricsActorTrackerSubscriber.h"
#include "ActorDensityMetric.generated.h"

UCLASS()
class UActorDensityMetric : public UWorldMetricInterface, public IWorldMetricsActorTrackerSubscriber
{
    GENERATED_BODY()
public:
    int32 TotalActors = 0;
    virtual SIZE_T GetAllocatedSize() const override { return 0; }
private:
    virtual void Initialize() override
    {
        GetOwner().AcquireExtension<UWorldMetricsActorTracker>(this);
    }
    virtual void Deinitialize() override
    {
        GetOwner().ReleaseExtension<UWorldMetricsActorTracker>(this);
        TotalActors = 0;
    }
    virtual void Update(float DeltaTimeInSeconds) override
    {
        // 可在此输出到 CSV 或其他系统
    }
    virtual void OnActorAdded(const AActor* Actor) override { ++TotalActors; }
    virtual void OnActorRemoved(const AActor* Actor) override { --TotalActors; }
};
```

Build.cs 依赖：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "WorldMetricsCore" });
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统基础 |
| `Core` | 引擎核心（私有依赖） |
| `Engine` | UWorld、Subsystem 等（私有依赖） |

CsvMetrics 模块额外依赖：

| 模块 | 用途 |
|---|---|
| `WorldMetricsCore` | Metric/Extension 基类和 Subsystem |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-07-21 | `2415c7aa` | 修复 Clang 20 编译时的 `[[nodiscard]]` 警告 |
| 2025-05-19 | `a60b2b5c` | 修正合并模块的 API 导出宏，PURE_VIRTUAL 不需要 API export |
| 2025-04-23 | `6ae57335` | 将所有方法/静态变量改为 DLL 导出（而非类型导出） |

### 维护评价

WorldMetrics 创建于 2024 年 2 月，是一个相对较新的插件（约 2 年）。最近 3 次更新都是编译器兼容性和 API 导出相关的维护性修复，没有功能性变更。

**关键观察**：
- 标记为 `IsExperimentalVersion=true`，但仍处于实验阶段
- `UCsvMetricsSubsystem::ShouldCreateSubsystem()` 目前硬编码返回 `false`（有 TODO 注释），说明 CsvMetrics 子系统尚未正式启用
- 有完善的单元测试（`WorldMetricsTest` 模块），覆盖了 metric 增删、extension 生命周期、集合管理等场景
- 提供 `WorldMetrics.SelfTest` 控制台命令用于运行时自检
- `SupportedPrograms` 中列出了 `SpatialMetricsProfiler`，表明它也被独立程序使用

**推荐使用**：可用，但需注意实验性标记。核心框架（Subsystem + Metric + Extension）设计良好且稳定。CsvMetrics 子系统功能不完整（当前被禁用），不建议依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/WorldMetrics)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/WorldMetrics/Source/WorldMetricsTest/Private/WorldMetricsTest.cpp)
