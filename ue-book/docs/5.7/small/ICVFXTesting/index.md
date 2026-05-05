# ICVFXTesting

> Testing utilities to be used by ICVFX projects

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | Hidden（不在编辑器 UI 中显示） |
| 包含内容 | true |
| 模块 | ICVFXTesting (Runtime) |
| 创建时间 | 2023-01-31 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/ICVFXTesting) | |

## 用途

ICVFXTesting 是基于 [Gauntlet 自动化框架](https://docs.unrealengine.com/5.7/en-US/automation-testing-in-unreal-engine/) 构建的 ICVFX（In-Camera VFX，机内视觉特效）性能测试工具。它解决了在虚拟制片流水线中自动化收集性能数据的问题。

ICVFX 场景需要运行 nDisplay 多视口、LED 墙渲染、LiveLink 相机同步等高开销系统，手动逐个测试不同位置和配置下的性能非常低效。这个 plugin 将整个流程自动化——自动移动 DisplayClusterRootActor 到预设测试位置，收集 FPS 图表、内存报告和视频录制，并支持多轮重复运行。

## 使用场景

- 你正在做一个 ICVFX 虚拟制片项目，需要基准测试不同场景位置下的帧率和内存 → 用 ICVFXTesting 自动遍历 `AICVFXTestLocation` 并收集 perf 数据
- 你需要在 CI/Gauntlet 中自动运行 ICVFX 性能回归测试 → 用此 plugin 配合 Gauntlet 的 `ICVFXTestControllerAutoTest` 控制器
- 你想对比 Lumen 开/关、Nanite 开/关等不同渲染配置对 ICVFX 场景的性能影响 → 通过命令行参数切换配置并自动收集报告

## 蓝图用法

此 plugin 主要面向自动化测试，没有暴露 BlueprintCallable 函数。但它提供了一个可在关卡中放置的蓝图可用 Actor：

### AICVFXTestLocation

| 属性 | 说明 |
|---|---|
| 基类 | `ACameraActor` |
| 蓝图类型 | `Blueprintable` / `BlueprintType` |
| 用途 | 在关卡中放置测试位置，运行时 DisplayClusterRootActor 会被移动到此处并采集性能数据 |
| 默认停留时间 | 60 秒/位置（可通过 `UICVFXTestControllerAutoTest::TimePerTestLocation` 调整） |

**使用方法**：在 ICVFX 关卡中放置若干 `AICVFXTestLocation` Actor，将它们摆放在你需要测试性能的关键位置（例如 LED 墙正前方、侧面、角落等）。测试运行时会自动扫描场景中所有 `AICVFXTestLocation` 并依次遍历。

## C++ 用法

### 核心架构

```
UGauntletTestController (Gauntlet 框架)
  └─ UICVFXTestControllerBase (基础功能：FPS 图表、内存报告、视频录制、控制台命令)
       └─ UICVFXTestControllerAutoTest (ICVFX 专用自动测试状态机)
```

### 头文件引入

```cpp
#include "ICVFXTestControllerBase.h"
#include "ICVFXTestControllerAutoTest.h"
#include "ICVFXTestLocation.h"
```

### 测试状态机

`UICVFXTestControllerAutoTest` 实现了一个 5 阶段状态机：

| 状态 | 说明 |
|---|---|
| `InitialLoad` | 等待关卡加载完成，获取 GPU 索引 |
| `Soak` | 沙盒浸泡期，等待 nDisplay 场景初始化、设置 LiveLink、收集初始性能数据 |
| `TraverseTestLocations` | 依次移动到每个 `AICVFXTestLocation` 并采集性能数据 |
| `Finished` | 停止 FPS 图表/视频录制、生成 MemReport，决定是否重跑下一轮 |
| `Shutdown` | 清理资源，调用 `EndICVFXTest` 退出 |

### 命令行参数与控制台变量

通过 Gauntlet 或命令行传递，控制测试行为：

| CVar / 参数 | 默认值 | 说明 |
|---|---|---|
| `ICVFXTest.MaxRunCount` | 1 | 最大运行轮数 |
| `ICVFXTest.SoakTime` | 30.0 | 沙盒浸泡时间（秒），设为 0 则无限浸泡 |
| `ICVFXTest.SkipTestSequence` | false | 跳过测试位置遍历阶段 |
| `ICVFXTest.FPSChart` | false | 启用 FPS 图表收集 |
| `ICVFXTest.MemReport` | false | 启用内存报告 |
| `ICVFXTest.MemReportInterval` | 1800.0 | 内存报告间隔（秒） |
| `ICVFXTest.MemReportArgs` | "-full -csv" | MemReport 命令参数 |
| `ICVFXTest.VideoCapture` | false | 启用视频录制 |
| `ICVFXTest.RequestShutdown` | false | 当前轮完成后立即关闭 |
| `ICVFXTest.TraceFileName` | "" | Unreal Insights trace 文件路径 |
| `ICVFXTest.DisplayClusterUAssetPath` | "" | nDisplay 配置资产路径 |

### 基本用法（提取自源码）

移动 DisplayClusterRootActor 到测试位置（来自 `ICVFXTestControllerAutoTest.cpp`）：

```cpp
// GoToTestLocation - 将 DisplayClusterRootActor 移动到指定测试位置
void UICVFXTestControllerAutoTest::GoToTestLocation(int32 Index)
{
    FString TestLocationName = TestLocations[Index]->GetActorNameOrLabel();
    CSV_EVENT(ICVFXTest, TEXT("TestLocation %s"), *TestLocationName);
    TimeAtTestLocation = 0.0;

    UE_LOG(LogICVFXTest, Display, TEXT("AutoTest TraverseTestLocations: Moving to test location: %s"),
        *TestLocations[Index]->GetActorNameOrLabel());

    // 核心逻辑：将 nDisplay Root Actor 的 Transform 设置为测试位置的 Transform
    DisplayClusterActor->SetActorTransform(TestLocations[Index]->GetActorTransform());
}
```

扫描场景中的测试位置（来自 `ICVFXTestControllerAutoTest.h`）：

```cpp
void UICVFXTestControllerAutoTest::UpdateTestLocations()
{
    UClass* TestLocationClass = AICVFXTestLocation::StaticClass();
    TestLocations.Reset();

    for (TActorIterator<AActor> ItActor = TActorIterator<AActor>(GetWorld(), TestLocationClass);
         ItActor; ++ItActor)
    {
        TestLocations.Add(*ItActor);
    }

    if (TestLocations.Num())
    {
        UE_LOG(LogICVFXTest, Display, TEXT("Found %d test locations."), TestLocations.Num());
    }
    else
    {
        // 没找到测试位置时，使用 DisplayCluster Root Actor 当前位置
        TestLocations.Add(DisplayClusterActor);
    }
    SetTestLocations(TestLocations);
}
```

设置 Inner GPU 索引（用于多 GPU 的 ICVFX 场景，来自 `ICVFXTestControllerAutoTest.h`）：

```cpp
void UICVFXTestControllerAutoTest::UpdateInnerGPUIndex()
{
    // 获取所有 ICVFXCameraComponent 并设置 GPU 索引
    TArray<UDisplayClusterICVFXCameraComponent*> CameraComponents;
    ADisplayClusterRootActor* RootActor = Cast<ADisplayClusterRootActor>(DisplayClusterActor);
    RootActor->GetComponents<UDisplayClusterICVFXCameraComponent>(CameraComponents, false);

    for (UDisplayClusterICVFXCameraComponent* CameraComponent : CameraComponents)
    {
        CameraComponent->CameraSettings.RenderSettings.AdvancedRenderSettings.GPUIndex =
            GetInnerGPUIndex();
    }
    // 刷新视口配置
    if (IDisplayClusterViewportManager* ViewportManager = RootActor->GetViewportManager())
    {
        const FString NodeId = IDisplayCluster::Get().GetClusterMgr()->GetNodeId();
        ViewportManager->GetConfiguration().UpdateConfigurationForClusterNode(
            EDisplayClusterRenderFrameMode::Mono, RootActor->GetWorld(), NodeId);
    }
}
```

### Gauntlet C# 端用法

在 Gauntlet 测试脚本中通过 `ICVFXTestConfig` 配置测试参数（来自 `ICVFX.TestNode.cs`）：

```csharp
// 关键配置参数
ICVFXTestConfig Config = GetConfiguration();
Config.MaxRunCount = 3;           // 运行 3 轮
Config.SoakTime = 60.0f;          // 每轮浸泡 60 秒
Config.FPSChart = true;           // 收集 FPS 图表
Config.MemReport = true;          // 收集内存报告
Config.VideoCapture = true;       // 录制视频
Config.Lumen = true;              // 启用 Lumen
Config.Nanite = true;             // 启用 Nanite
Config.ViewportScreenPercentage = 100.0f;
Config.MaxGPUCount = 1;
Config.DisplayConfigPath = "/path/to/displayconfig.json";
Config.DisplayClusterNodeName = "node0";
```

## Demo 示例

### 最小自动化测试设置

1. **在关卡中放置测试位置**：放置若干 `AICVFXTestLocation` Actor（蓝图类名 `ICVFXTestLocation`）

2. **通过 Gauntlet 启动测试**（Windows 平台）：

```bash
# 基本运行：1 轮，30 秒浸泡，收集 FPS 图表和内存报告
RunUAT.bat RunUnreal -project=YourProject \
    -platform=Win64 -configuration=Development \
    -test=ICVFXTest.AutoTest \
    -ICVFXTest.MaxRunCount=1 \
    -ICVFXTest.SoakTime=30 \
    -ICVFXTest.FPSChart=true \
    -ICVFXTest.MemReport=true

# 启用 Lumen + Nanite + 多 GPU
RunUAT.bat RunUnreal -project=YourProject \
    -platform=Win64 -configuration=Development \
    -test=ICVFXTest.AutoTest \
    -ICVFXTest.Lumen=true \
    -ICVFXTest.Nanite=true \
    -ICVFXTest.MaxGPUCount=2

# 指定 nDisplay 配置 + Unreal Insights trace
RunUAT.bat RunUnreal -project=YourProject \
    -platform=Win64 -configuration=Development \
    -test=ICVFXTest.AutoTest \
    -ICVFXTest.DisplayConfig=path/to/config.json \
    -ICVFXTest.DisplayClusterNodeName=node0 \
    -ICVFXTest.EnableTrace=true \
    -ICVFXTest.TraceRootFolder=C:/Traces
```

3. **Build.cs 依赖**（如果你要继承或扩展此 plugin）：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core", "Engine", "CoreUObject", "Gauntlet"
});
PrivateDependencyModuleNames.AddRange(new string[] {
    "CinematicCamera", "DisplayCluster", "Engine",
    "LiveLink", "LiveLinkComponents", "LiveLinkInterface", "RenderCore"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Engine` | 引擎核心（World、Timer、Console 等） |
| `CoreUObject` | UObject 系统 |
| `Gauntlet` | Epic 的自动化测试框架，提供 `UGauntletTestController` 基类 |
| `CinematicCamera` | `ACineCameraActor` 支持（私有依赖） |
| `DisplayCluster` | nDisplay 核心模块（私有依赖） |
| `LiveLink` / `LiveLinkComponents` / `LiveLinkInterface` | LiveLink 相机同步（私有依赖） |
| `RenderCore` | 渲染核心，支持多 GPU（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-06-12 | `cea02304` | 修复测试脚本中的拼写错误 |
| 2025-06-11 | `6a48c6cb` | 修复离屏节点的命令行参数传递，修复 Nanite/Lumen 开关传递到自动化脚本的问题 |
| 2025-05-09 | `8d37f38f` | Switchboard 中的 PerfTesting 升级 |

### 维护评价

- **状态**：活跃维护 ✅
- **年龄**：约 3 年（2023-01 创建）
- **最近更新**：2025 年 6 月，最近 3 个月内有实质性功能更新
- **Beta 状态**：`IsBetaVersion=true`，`Hidden=true` — 仅供 Epic 内部虚拟制片团队使用，不在编辑器 UI 中公开
- **平台限制**：仅 Win64（ICVFX/LED 墙场景通常是 Windows 工作站）
- **推荐**：如果你在做虚拟制片项目的性能基准测试，此 plugin 提供了经过 Epic 内部验证的 ICVFX 自动化测试流程。注意它是 Beta 且 Hidden，API 可能在未来版本中变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/ICVFXTesting)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/ICVFXTesting/Build/Scripts/Automation/Tests)
