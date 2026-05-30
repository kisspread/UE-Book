# ICVFXTesting

> Testing utilities to be used by ICVFX projects

| 属性 | 值 |
|---|---|
| 中文名 | ICVFX 测试工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图可放置的测试位置 Actor） |
| 模块 | `ICVFXTesting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-31 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ICVFXTesting) | |

## 用途

ICVFXTesting 为 **In-Camera Visual Effects**（摄像机内视觉特效，即 LED 墙虚拟拍摄）项目提供自动化性能测试框架。它基于 Unreal 的 Gauntlet 自动化测试系统，解决了以下问题：

1. **ICVFX 性能基准测试**：自动在场景中多个测试位置之间移动 nDisplay 显示集群根 Actor，在每个位置停留一段时间，采集 FPS、内存等性能数据
2. **多轮次测试**：支持配置运行次数，自动循环执行多次测试取平均
3. **自动性能报告**：在测试过程中自动生成 FPS Chart、CSV 性能分析、内存报告
4. **视频录制**：自动控制视频捕获，用于回放分析
5. **GPU 索引管理**：管理内侧视口使用的 GPU 索引，适应 ICVFX 的多 GPU 渲染架构
6. **LiveLink 集成**：自动连接 LiveLink 相机数据，同步真实摄像机与虚拟场景

简而言之：这个插件让 ICVFX 团队能够在多个机位位置上**无人值守地**运行标准化性能测试，而不需要手动移动机位、手动记录数据。

## 使用场景

- 你正在用 nDisplay LED 墙做虚拟拍摄（ICVFX），需要评估不同机位的渲染性能 → 用 ICVFXTesting
- 你需要自动化地在多个测试位置循环采集 FPS、内存、GPU 性能数据 → 用 ICVFXTesting
- 你想在持续运行（soak test）期间监控 ICVFX 场景的稳定性 → 用 ICVFXTesting
- 你需要通过 Gauntlet 框架在 CI/CD 管线中运行 ICVFX 性能回归测试 → 用 ICVFXTesting

## 蓝图用法

### 核心类

#### AICVFXTestLocation（蓝图可放置）

这是一个特殊的相机 Actor，用于在场景中标记测试位置。你可以在编辑器中将它放置到场景中的任意位置，测试控制器会自动将 nDisplay 显示集群根 Actor 移动到这些位置进行测试。

**在编辑器中的使用方式：**

1. 在场景中放置一个 `AICVFXTestLocation` Actor（位于 Actor 面板 → ICVFX 分类下）
2. 将其移动到你想测试的位置（对应实际摄像机在 LED 墙前的位置）
3. 在场景中放置多个测试位置 Actor，覆盖所有需要测试的机位
4. 自动测试控制器会在初始化时自动收集场景中所有 `AICVFXTestLocation` Actor

> **注意**：测试控制器（`UICVFXTestControllerBase` 和 `UICVFXTestControllerAutoTest）是 C++ 类，不直接在蓝图中使用。它们通过 Gauntlet 命令行框架启动，配置通过命令行参数和配置文件完成。

### 测试配置命令前缀

测试控制器在初始化时会自动解析以下命令前缀的控制台变量（可通过命令行或配置文件设置）：

| 命令前缀 | 用途 |
|---|---|
| `t.FPSChart.DoCsvProfile` | 启用 CSV 性能分析 |
| `ICVFXTest` | 插件专用测试参数 |
| `r.nanite` | Nanite 渲染设置 |
| `r.ScreenPercentage` | 屏幕分辨率百分比 |
| `r.RayTracing` | 光线追踪开关 |
| `r.DynamicGlobalIlluminationMethod` | 动态全局光照方法 |
| `r.ReflectionMethod` | 反射方法 |
| `r.Lumen` | Lumen 全局光照设置 |
| `FX.AllowGPUParticles` | GPU 粒子开关 |
| `r.Shadow.Virtual.Enable` | 虚拟阴影贴图开关 |

## C++ 用法

### 头文件引入

```cpp
#include "ICVFXTestControllerBase.h"
#include "ICVFXTestControllerAutoTest.h"
#include "ICVFXTestLocation.h"
```

### 基本用法：创建自定义测试控制器

最常见的方式是继承 `UICVFXTestControllerBase` 来创建自定义测试逻辑：

```cpp
// MyICVFXTestController.h
#pragma once

#include "ICVFXTestControllerBase.h"
#include "MyICVFXTestController.generated.h"

UCLASS()
class UMyICVFXTestController : public UICVFXTestControllerBase
{
    GENERATED_BODY()

public:
    UMyICVFXTestController(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer) {}

protected:
    virtual void OnInit() override
    {
        Super::OnInit();
        // 自定义初始化逻辑
    }

    virtual void OnTick(float TimeDelta) override
    {
        Super::OnTick(TimeDelta);
        // 自定义每帧逻辑
    }

    virtual void OnStateChange(FName OldState, FName NewState) override
    {
        Super::OnStateChange(OldState, NewState);
        // 处理状态变化
    }
};
```

### 进阶用法：使用自动测试控制器

`UICVFXTestControllerAutoTest` 提供了完整的状态机驱动测试流程。你可以继承它来自定义每个状态的行为：

```cpp
// 基于 .uplugin 中的 TestControllerAutoTest 类分析
// 测试流程状态机: InitialLoad → Soak → TraverseTestLocations → Finished → Shutdown

// 在你的测试 GameMode 或配置中设置自定义控制器
// 通过 Gauntlet 命令行指定控制器类

// 自动测试控制器的典型使用流程：
void ExampleAutoTestSetup()
{
    // 1. 在场景中放置 AICVFXTestLocation Actor 标记测试位置
    // 2. 控制器 OnInit 时自动收集场景中所有 TestLocation
    // 3. 自动初始化 LiveLink 连接
    // 4. 按状态机循环执行测试
}
```

### 自动测试状态机详解

```
InitialLoad → Soak → TraverseTestLocations → Finished → Shutdown
```

| 状态 | 行为 |
|---|---|
| `InitialLoad` | 等待关卡完全加载 |
| `Soak` | 在当前位置持续运行，执行稳定性测试（可配置浸泡时间） |
| `TraverseTestLocations` | 遍历所有测试位置，在每个位置停留 `TimePerTestLocation` 秒（默认 60 秒） |
| `Finished` | 测试完成，收集最终数据 |
| `Shutdown` | 清理资源，结束测试 |

### 配置项

```cpp
// UICVFXTestControllerAutoTest 的可配置属性
float TimePerTestLocation = 60.f;      // 每个测试位置停留时间（秒）
double TimeAtTestLocation = 0.0;       // 当前位置已停留时间
TObjectPtr<AActor> DisplayClusterActor; // nDisplay 集群根 Actor

// 运行次数控制（来自基类）
// 通过命令行参数配置运行次数
uint32 GetRunCount();         // 已完成运行次数
uint32 GetMaxRunCount();      // 最大运行次数
uint32 GetRunsRemaining();    // 剩余运行次数
uint32 MarkRunComplete();     // 标记当前运行完成
```

### GPU 索引管理

在多 GPU 渲染架构中，可以通过以下方法管理内侧视口使用的 GPU：

```cpp
// 设置内侧视口的 GPU 索引
void SetInnerGPUIndex(int32 InGPUIndex);

// 获取当前 GPU 索引
int32 GetInnerGPUIndex() const;

// 更新 GPU 索引（自动调用）
void UpdateInnerGPUIndex();
```

## Demo 示例

### 自定义 ICVFX 测试控制器

```cpp
// MyICVFXPerfTestController.h
#pragma once

#include "ICVFXTestControllerBase.h"
#include "MyICVFXPerfTestController.generated.h"

UCLASS()
class UMyICVFXPerfTestController : public UICVFXTestControllerBase
{
    GENERATED_BODY()

public:
    UMyICVFXPerfTestController(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
    }

protected:
    virtual void OnInit() override
    {
        Super::OnInit();

        // 通过命令行请求 FPS Chart 和内存报告
        // 控制器会根据命令行参数自动启用这些功能
    }

    virtual void OnTick(float TimeDelta) override
    {
        Super::OnTick(TimeDelta);

        // 检查是否所有运行已完成
        if (GetRunsRemaining() == 0)
        {
            EndICVFXTest(0);
        }
    }

    virtual void OnPreWorldInitialize(UWorld* World) override
    {
        // 世界初始化后的自定义逻辑
        // 可在此处设置测试环境
    }
};
```

```cpp
// MyICVFXPerfTestController.cpp
#include "MyICVFXPerfTestController.h"

UMyICVFXPerfTestController::UMyICVFXPerfTestController(
    const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

void UMyICVFXPerfTestController::OnInit()
{
    Super::OnInit();
    UE_LOG(LogTemp, Log, TEXT("ICVFX Perf Test: Initialized, %d runs remaining"),
        GetRunsRemaining());
}

void UMyICVFXPerfTestController::OnTick(float TimeDelta)
{
    Super::OnTick(TimeDelta);
}

void UMyICVFXPerfTestController::OnPreWorldInitialize(UWorld* World)
{
    UE_LOG(LogTemp, Log, TEXT("ICVFX Perf Test: World initialized"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Gauntlet` | Unreal 自动化测试框架，提供 `UGauntletTestController` 基类 |
| `LiveLinkCamera` | LiveLink 相机数据同步，用于将真实摄像机数据连接到虚拟场景 |
| `nDisplay` | nDisplay 多屏幕/LED 墙渲染系统，提供 `DisplayCluster` Actor 和集群管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `e1420e00` | Automation: Only set OutputPath if we're not setting an ArtifactsPath. This means that we can easily | 自动化构建流程优化：调整输出路径设置逻辑 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移：从 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-03-06 | `14f0178c` | Remove unneeded Microsoft.CSharp PackageReference | 清理不必要的 C# 包引用 |
| 2026-02-17 | `a3398a37` | AutomationScripts: Use default TargetFramework from shared property sheet | 自动化脚本构建配置统一化 |
| 2026-02-16 | `125566ea` | [Backout] - CL50919955 | 回退一次之前的提交 |

### 维护评价

ICVFXTesting 于 2023 年 1 月创建，当前标记为 **Beta 版本**且为 **Hidden** 插件。近期（2026 年）有持续的提交记录，但大部分是全局性的基础设施维护（日志宏迁移、构建系统调整），而非插件本身的功能更新。最近 5 次提交中**没有针对 ICVFX 测试功能本身的实质性改动**。

- **年龄**：约 3 年，属于较新的插件
- **状态**：Beta，Hidden，Installed=false — 明确的实验性质
- **维护频率**：有提交但多为全局维护性变更
- **平台限制**：仅支持 Win64，符合 ICVFX/LED 墙制作环境的实际情况
- **依赖链**：依赖 Gauntlet + nDisplay + LiveLinkCamera，部署需要完整的虚拟制片环境

**建议**：适用于 ICVFX 项目的内部自动化测试需求。由于是 Beta 且 Hidden，不建议作为核心生产流程的依赖。接口可能会有变动。如果你的项目使用 nDisplay LED 墙并需要自动化性能测试，可以参考此插件的实现模式，或直接在你的项目中创建类似的测试控制器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ICVFXTesting)
- 官方文档（无）