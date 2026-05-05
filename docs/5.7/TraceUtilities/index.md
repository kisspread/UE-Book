# TraceUtilities

> A collection of tools that increase usability of Unreal Insights and the Trace Framework

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ true |
| 包含内容 | ✅ true（SVG 图标） |
| 模块 | TraceUtilities (Runtime), EditorTraceUtilities (EditorNoCommandlet), InsightsEditor (EditorNoCommandlet) |
| 创建时间 | 2022-08-17 |
| 年龄标签 | 🆕 (~3.7 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TraceUtilities) | |

## 用途

TraceUtilities 将 Unreal Insights 和 Trace Framework 的核心能力封装为蓝图可用的 API，并在编辑器底部状态栏集成了 Trace 控制面板。

它解决三个问题：

1. **蓝图中无法控制 Trace**：引擎的 `FTraceAuxiliary` 和 `UE::Trace` 命名空间全是 C++ API，没有 BlueprintCallable 接口。TraceUtilities 的 `UTraceUtilLibrary` 补上了这个缺口——你可以在蓝图中启停 Trace、切换 Channel、插入 Bookmark 和 Region 标记。

2. **Insights 启动流程繁琐**：手动找 `UnrealInsights.exe`、拼命令行参数、处理 exe 不存在时的编译——`FUnrealInsightsLauncher` 将这一切自动化。

3. **编辑器中缺乏 Trace 状态感知**：`SInsightsStatusBarWidget` 在编辑器状态栏显示当前 Trace 状态，支持一键启停、Channel 切换、快照保存，并可直接打开 Insights 查看结果。

## 使用场景

- 你在做性能分析，想在蓝图的特定位置插入 Trace Bookmark/Region 来标记关键帧 → 用 `TraceBookmark` / `TraceMarkRegionStart` / `TraceMarkRegionEnd`
- 你想在运行时通过蓝图动态启停 Trace 录制（例如只在特定关卡录制）→ 用 `StartTraceToFile` / `StopTracing`
- 你想把 Trace 数据通过网络发送到另一台机器上的 UnrealTraceServer → 用 `StartTraceSendTo`
- 你需要在编辑器中快速查看哪些 Trace Channel 已启用 → 用 `GetEnabledChannels` / `GetAllChannels`
- 你想从 C++ 代码中以编程方式打开 UnrealInsights 并加载指定的 `.utrace` 文件 → 用 `FUnrealInsightsLauncher::OpenTraceFile`

## 蓝图用法

所有蓝图节点都在 `UTraceUtilLibrary` 类中，分类为 `Perf | Insights Trace`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartTraceToFile` | 开始录制 Trace 到本地 `.utrace` 文件，指定 Channel 列表 | `UTraceUtilLibrary` |
| `StartTraceSendTo` | 开始录制并通过网络发送到目标地址（Trace Store） | `UTraceUtilLibrary` |
| `StopTracing` | 停止当前 Trace 录制 | `UTraceUtilLibrary` |
| `PauseTracing` | 暂停 Trace 录制（不关闭连接） | `UTraceUtilLibrary` |
| `ResumeTracing` | 恢复已暂停的 Trace 录制 | `UTraceUtilLibrary` |
| `IsTracing` | 查询当前是否正在录制 | `UTraceUtilLibrary` |
| `ToggleChannel` | 启用/禁用指定 Trace Channel | `UTraceUtilLibrary` |
| `IsChannelEnabled` | 查询指定 Channel 是否已启用 | `UTraceUtilLibrary` |
| `GetEnabledChannels` | 获取所有已启用的 Channel 名称列表 | `UTraceUtilLibrary` |
| `GetAllChannels` | 获取所有已注册的 Channel 名称列表 | `UTraceUtilLibrary` |
| `TraceBookmark` | 在 Trace 中插入一个命名书签（在 Insights 时间线上可见） | `UTraceUtilLibrary` |
| `TraceMarkRegionStart` | 标记一个命名 Region 的开始 | `UTraceUtilLibrary` |
| `TraceMarkRegionEnd` | 标记一个命名 Region 的结束 | `UTraceUtilLibrary` |
| `TraceScreenshot` | 在 Trace 中触发一张截图（可选是否显示 UI） | `UTraceUtilLibrary` |

### 使用示例（蓝图描述）

**录制性能数据到文件：**

1. 在 BeginPlay 中，创建一个 String Array 变量 `Channels`，填入 `"cpu,gpu,frame"`
2. 拖出 `StartTraceToFile` 节点，FileName 设为 `"MyProfile"`, Channels 连接到变量
3. 在 EndPlay 中，调用 `StopTracing`
4. 生成的 `.utrace` 文件位于项目的 Profiling 目录

**标记关键逻辑区间：**

1. 在关键逻辑开始前，调用 `TraceMarkRegionStart`，Name 设为 `"BossFight"`
2. 在关键逻辑结束后，调用 `TraceMarkRegionEnd`，Name 设为 `"BossFight"`
3. 在 Insights 的 Timing 视图中可看到该 Region 的耗时

## C++ 用法

### 头文件引入

```cpp
// 蓝图库（Runtime 模块）
#include "TraceUtilLibrary.h"

// Insights 启动器（Editor 模块）
#include "UnrealInsightsLauncher.h"

// 编辑器模块接口
#include "IEditorTraceUtilitiesModule.h"
```

### 基本用法

`UTraceUtilLibrary` 的所有方法都是静态的，可以直接调用：

```cpp
// 开始录制到文件，指定 Channel
TArray<FString> Channels = { TEXT("cpu"), TEXT("gpu"), TEXT("frame") };
UTraceUtilLibrary::StartTraceToFile(TEXT("MyProfile"), Channels);

// 暂停 / 恢复
UTraceUtilLibrary::PauseTracing();
UTraceUtilLibrary::ResumeTracing();

// 停止录制
UTraceUtilLibrary::StopTracing();

// 插入书签
UTraceUtilLibrary::TraceBookmark(TEXT("PlayerDeath"));

// 标记 Region
UTraceUtilLibrary::TraceMarkRegionStart(TEXT("LoadingScreen"));
// ... 执行加载逻辑 ...
UTraceUtilLibrary::TraceMarkRegionEnd(TEXT("LoadingScreen"));
```

来源：`Engine/Plugins/TraceUtilities/Source/TraceUtilities/Private/TraceUtilLibrary.cpp`

### 进阶用法

**查询和切换 Channel：**

```cpp
// 获取所有可用 Channel
TArray<FString> AllChannels = UTraceUtilLibrary::GetAllChannels();

// 动态启用/禁用 Channel
UTraceUtilLibrary::ToggleChannel(TEXT("memory"), true);
bool bEnabled = UTraceUtilLibrary::IsChannelEnabled(TEXT("memory"));

// 获取当前已启用的 Channel
TArray<FString> ActiveChannels = UTraceUtilLibrary::GetEnabledChannels();
```

**从 C++ 启动 UnrealInsights：**

```cpp
#include "UnrealInsightsLauncher.h"

// 获取 Insights 可执行文件路径
FString InsightsPath = FUnrealInsightsLauncher::Get()->GetInsightsApplicationPath();

// 打开本地 .utrace 文件
FUnrealInsightsLauncher::Get()->OpenTraceFile(TEXT("C:/Traces/MyProfile.utrace"));

// 从 Trace Store 打开远程 Trace
FUnrealInsightsLauncher::Get()->OpenRemoteTrace(TEXT("192.168.1.100"), 1980, TraceID);

// 打开当前活跃的 Trace Session
FUnrealInsightsLauncher::Get()->OpenActiveTraceFromStore(TEXT("localhost"));

// 如果 exe 不存在会自动编译
FUnrealInsightsLauncher::Get()->StartUnrealInsights(InsightsPath, TEXT(""));
```

来源：`Engine/Plugins/TraceUtilities/Source/EditorTraceUtilities/Private/UnrealInsightsLauncher.cpp`

## Demo 示例

一个最小的 Trace 录制示例模块：

### Build.cs

```csharp
using UnrealBuildTool;

public class MyTraceExample : ModuleRules
{
    public MyTraceExample(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "TraceUtilities"  // Runtime 模块，可在打包版本中使用
        });
    }
}
```

### MyTraceExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTraceExample.generated.h"

UCLASS()
class AMyTraceExample : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

### MyTraceExample.cpp

```cpp
#include "MyTraceExample.h"
#include "TraceUtilLibrary.h"

void AMyTraceExample::BeginPlay()
{
    Super::BeginPlay();

    // 开始录制 CPU 和 GPU 数据
    TArray<FString> Channels = { TEXT("cpu"), TEXT("gpu"), TEXT("frame") };
    bool bStarted = UTraceUtilLibrary::StartTraceToFile(TEXT("MyGameplayTrace"), Channels);

    if (bStarted)
    {
        UE_LOG(LogTemp, Log, TEXT("Trace recording started"));
    }
}

void AMyTraceExample::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 停止录制
    if (UTraceUtilLibrary::IsTracing())
    {
        UTraceUtilLibrary::StopTracing();
        UE_LOG(LogTemp, Log, TEXT("Trace recording stopped"));
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

### TraceUtilities（Runtime）

如果你只需要蓝图/C++ 控制 Trace 录制，依赖此模块即可。打包后也可用。

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统（私有） |
| `Engine` | 引擎核心（私有） |
| `TraceLog` | Trace 底层日志系统（私有） |

### EditorTraceUtilities（EditorNoCommandlet）

编辑器专用，提供状态栏 UI 和 Insights 启动器。不可在打包版本中使用。

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `Engine` | 引擎核心（私有） |
| `InputCore` | 输入系统（私有） |
| `Slate` / `SlateCore` | UI 框架（私有） |
| `ToolMenus` | 编辑器菜单系统（私有） |
| `TraceAnalysis` | Trace 数据分析（私有） |
| `TraceInsightsFrontend` | Insights 前端（私有） |
| `TraceTools` | Trace 工具集（私有） |
| `TraceLog` | Trace 底层日志系统（私有） |
| `UATHelper` | UAT 构建辅助（私有，用于自动编译 Insights） |

### InsightsEditor（EditorNoCommandlet）

Insights 窗口的编辑器集成。

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `TraceInsights` | Insights 主体（公开） |
| `Engine` | 引擎核心（私有） |
| `InputCore` | 输入系统（私有） |
| `Slate` / `SlateCore` | UI 框架（私有） |
| `ToolMenus` | 编辑器菜单系统（私有） |
| `TraceLog` | Trace 底层日志系统（私有） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-28 | `39303958` | PlatformEvents channel uses callbacks | 功能更新：PlatformEvents Channel 改用回调机制 |
| 2025-07-25 | `18717d9e` | Fix Timing Insights window visibility in Fortnite. | Bug 修复：修复 Timing Insights 窗口在 Fortnite 中的可见性问题 |
| 2025-07-12 | `b8bdcd83` | Run UnrealCodeFixup to fix dll storage | 代码维护：修复 DLL 导出存储属性 |

### 维护评价

- **创建时间**：2022-08-17，约 3.7 年前
- **最近更新**：2025-08-28，距今约 8 个月，有功能性更新
- **维护状态**：✅ **活跃维护**——最近 1 年内有功能更新和 Bug 修复
- **已知限制**：
  - `EditorTraceUtilities` 和 `InsightsEditor` 模块仅限编辑器使用（EditorNoCommandlet），打包版本不可用
  - `TraceScreenshot` 仅在 `UE_SCREENSHOT_TRACE_ENABLED` 宏开启时有效
  - Config 文件中 `OpenLiveSesssionOnTraceStart` 拼写有误（多了个 s），但作为实际键名需保持一致
- **推荐使用**：✅ 推荐。这是 Epic 官方维护的 Trace 控制工具，是连接蓝图/编辑器与 Unreal Insights 的标准桥梁。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TraceUtilities)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [TraceUtilities 模块](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/TraceUtilities/Source/TraceUtilities)
- [EditorTraceUtilities 模块](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/TraceUtilities/Source/EditorTraceUtilities)
- [InsightsEditor 模块](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/TraceUtilities/Source/InsightsEditor)
