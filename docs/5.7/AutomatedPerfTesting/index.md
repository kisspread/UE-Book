# AutomatedPerfTesting

> This plugin provides Gauntlet Test Controllers to facilitate automatic performance testing.

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、默认材质测试地图和网格体） |
| 模块 | `AutomatedPerfTesting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-23 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Performance/AutomatedPerfTesting) | |

## 用途

AutomatedPerfTesting 是一个基于 **Gauntlet** 自动化测试框架的性能测试插件。它解决的核心问题是：**如何在 CI/CD 管线中自动、可重复地采集游戏运行时性能数据**。

传统的性能测试需要人工在编辑器中操作、截图、记录数据，这个插件将整个流程自动化了——你只需要在 Project Settings 中配置好测试参数，通过命令行或 Project Launcher 启动测试，插件会自动加载地图、播放序列/回放、切换相机/材质、采集 CSV 性能数据和 Insights Trace，最后自动退出并输出结果文件。

插件提供了 **5 种内置测试类型**，覆盖了常见的性能测试场景：

| 测试类型 | 控制器类 | 用途 |
|---|---|---|
| Sequence | `UAutomatedSequencePerfTest` | 沿 Level Sequence 播放路径采集性能数据 |
| Replay | `UAutomatedReplayPerfTest` | 回放录制的网络 Replay 文件并采集性能 |
| ProfileGo | `UAutomatedProfileGoTest` | 传送到指定位置执行 profiling 命令 |
| Static Camera | `UAutomatedStaticCameraPerfTestBase` | 在地图中放置的相机位置间切换采集 |
| Material | `UAutomatedMaterialPerfTest` | 将材质渲染到平板上逐个采集渲染性能 |

## 使用场景

- **你正在做一款大型开放世界游戏**，需要在 CI 中自动测试每个地图的帧率 → 用 Sequence 或 Static Camera 测试
- **你需要对比不同材质的渲染开销**，有几十个材质要逐一测试 → 用 Material 测试
- **你录了一段游戏回放**，想在每次构建后自动回放并采集性能数据 → 用 Replay 测试
- **你想在特定摄像机位置采集 profiling 数据**（如 Kismet 场景切换点）→ 用 ProfileGo 测试
- **你需要在 Gauntlet 自动化管线中集成性能测试** → 这个插件正是为此而生

## 蓝图用法

此插件主要面向 C++ 和命令行自动化，蓝图暴露有限。以下是可用的蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTestID()` | 获取当前测试的唯一标识字符串 | `UAutomatedPerfTestSubsystem` |
| `GetComboFromTestName()` | 根据名称查找 Map/Sequence 组合 | `UAutomatedSequencePerfTestProjectSettings` |
| `GetReplayPathFromName()` | 根据名称查找 Replay 文件路径 | `UAutomatedReplayPerfTestProjectSettings` |
| `GetMapFromAssetName()` | 根据资产名查找地图路径 | `UAutomatedStaticCameraPerfTestProjectSettings` |
| `SetupTest()` | 设置测试（蓝图可实现事件） | `IAutomatedPerfTestInterface` |
| `RunTest()` | 运行测试（蓝图可实现事件） | `IAutomatedPerfTestInterface` |
| `TeardownTest()` | 拆解测试（蓝图可实现事件） | `IAutomatedPerfTestInterface` |
| `Exit()` | 退出测试（蓝图可实现事件） | `IAutomatedPerfTestInterface` |

### GameMode 接口

插件提供了 `AAutomatedPerfTestGameModeBase`，这是一个可蓝图化的 GameMode 基类，实现了 `IAutomatedPerfTestInterface`。你可以基于它创建蓝图 GameMode，在 `SetupTest`、`RunTest`、`TeardownTest`、`Exit` 回调中添加自定义蓝图逻辑。

**蓝图使用方式**：创建一个基于 `AAutomatedPerfTestGameModeBase` 的蓝图 GameMode → 在 Project Settings 中通过 `GameModeOverride` 指定该 GameMode 的别名 → 测试运行时会自动调用你的蓝图回调。

### 项目设置

所有测试类型都在 **Project Settings → Plugins** 下有自己的配置面板：

- **Automated Performance Testing** — 通用设置（TeardownToExitDelay）
- **Automated Performance Testing | Sequence** — 地图/序列组合列表
- **Automated Performance Testing | Replay** — 回放文件列表
- **Automated Performance Testing | ProfileGo** — 场景/集合/命令配置
- **Automated Performance Testing | Static Camera** — 地图列表和相机参数
- **Automated Performance Testing | Materials** — 材质列表和渲染参数

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestControllerBase.h"  // 基类，继承它创建自定义测试控制器
#include "AutomatedPerfTestProjectSettings.h" // 项目设置
#include "AutomatedPerfTestInterface.h"        // GameMode 接口
```

### 基本用法：自定义测试控制器

所有测试控制器都继承自 `UAutomatedPerfTestControllerBase`（本身继承自 `UGauntletTestController`）。基本流程是重写 `OnInit` → `SetupTest` → `RunTest` → `TeardownTest` → `Exit`。

```cpp
// 来源: Source/AutomatedPerfTesting/Private/AutomatedSequencePerfTest.cpp

// 1. 在 OnInit 中读取配置、解析命令行参数
void UMyPerfTest::OnInit()
{
    Super::OnInit();
    Settings = GetDefault<UMyTestProjectSettings>();
    SetCSVOutputMode(Settings->CSVOutputMode);
}

// 2. SetupTest 中准备测试环境（加载地图、创建对象等）
void UMyPerfTest::SetupTest()
{
    Super::SetupTest();  // 会调用 GameMode->SetupTest()
    SetupProfiling();    // 启动 CSV Profiler / FPS Chart / Video Capture
    // ... 设置定时器延迟后调用 RunTest
}

// 3. RunTest 中开始采集性能数据
void UMyPerfTest::RunTest()
{
    Super::RunTest();
    MarkProfilingStart();  // 标记 Insights/CSV region 开始
    // ... 执行测试逻辑
}

// 4. TeardownTest 中结束采集
void UMyPerfTest::TeardownTest(bool bExitAfterTeardown)
{
    MarkProfilingEnd();
    TeardownProfiling();   // 停止 CSV Profiler / FPS Chart / Video Capture
    Super::TeardownTest(bExitAfterTeardown);
}
```

### 命令行参数

测试通过 Gauntlet 启动，控制器类名通过命令行指定。基类解析以下通用参数：

```bash
# 通用参数（所有测试类型共享）
-AutomatedPerfTest.DoCSVProfiler          # 启用 CSV 性能数据采集
-AutomatedPerfTest.DoInsightsTrace         # 启用 Unreal Insights Trace
-AutomatedPerfTest.DoFPSChart              # 启用 FPS Chart
-AutomatedPerfTest.DoVideoCapture          # 启用视频录制
-AutomatedPerfTest.LockDynamicRes          # 锁定动态分辨率
-AutomatedPerfTest.DeviceProfileOverride=X # 覆盖设备配置文件
-AutomatedPerfTest.TestID=X               # 自定义测试 ID
-AutomatedPerfTest.TraceChannels=X        # 自定义 Trace 通道（默认: default,screenshot,stats）
-AutomatedPerfTest.ArtifactOutputPath=X   # 输出文件路径

# Sequence 测试专用
-AutomatedPerfTest.SequencePerfTest.MapSequenceName=X  # 指定单个 MapSequence 组合

# Replay 测试专用
-AutomatedPerfTest.ReplayPerfTest.ReplayName=X  # 指定回放文件名

# Static Camera 测试专用
-AutomatedPerfTest.StaticCameraPerfTest.MapName=X  # 指定单个地图

# ProfileGo 测试专用
-profilego=ScenarioName           # 指定 ProfileGo 场景
-profilego.config=filepath.json   # 从 JSON 加载配置
-profilego.loops=N                # 循环次数
-profilego.exit                   # 完成后退出
-profilego.ignorepawn             # 忽略玩家 Pawn
```

### CSV 输出模式

```cpp
// 来源: Source/AutomatedPerfTesting/Public/AutomatedPerfTestControllerBase.h
enum class EAutomatedPerfTestCSVOutputMode : uint8
{
    Single,    // 整个会话输出一个 CSV
    Separate,  // 每个地图/测试段输出独立 CSV
    Granular   // 每个相机切换/材质输出独立 CSV
};
```

### 进阶用法：创建自定义测试类型

```cpp
// 1. 定义项目设置类
UCLASS(Config=Engine, DefaultConfig, DisplayName="My Custom Perf Test")
class UMyPerfTestSettings : public UDeveloperSettings
{
    GENERATED_BODY()
public:
    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite)
    TArray<FSoftObjectPath> AssetsToTest;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite)
    float WarmUpTime = 5.0f;
};

// 2. 定义测试控制器
UCLASS()
class UMyPerfTestController : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()
public:
    virtual void OnInit() override;
    virtual FString GetTestID() override;
    virtual void SetupTest() override;
    virtual void RunTest() override;
    virtual void TeardownTest(bool bExitAfterTeardown = true) override;
};
```

## Demo 示例

### Build.cs 依赖配置

```csharp
// 你的模块 Build.cs 中需要添加：
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "Gauntlet"  // 必须依赖 Gauntlet
});

// 如果需要自定义 Project Settings UI：
PrivateDependencyModuleNames.AddRange(new string[]
{
    "CoreUObject",
    "Engine",
    "DeveloperSettings"
});
```

### 最小自定义测试控制器

```cpp
// MySimplePerfTest.h
#pragma once
#include "AutomatedPerfTestControllerBase.h"
#include "MySimplePerfTest.generated.h"

UCLASS()
class UMySimplePerfTest : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()

public:
    virtual FString GetTestID() override
    {
        return Super::GetTestID() + "_Simple";
    }

    virtual void SetupTest() override
    {
        Super::SetupTest();
        SetupProfiling();

        // 延迟 3 秒后开始测试
        FTimerHandle Handle;
        GetWorld()->GetTimerManager().SetTimer(
            Handle, this, &UMySimplePerfTest::RunTest, 1.0f, false, 3.0f);
    }

    virtual void RunTest() override
    {
        Super::RunTest();
        MarkProfilingStart();

        // 采集 10 秒后结束
        FTimerHandle Handle;
        GetWorld()->GetTimerManager().SetTimer(
            Handle, this, &UMySimplePerfTest::FinishTest, 1.0f, false, 10.0f);
    }

private:
    void FinishTest()
    {
        MarkProfilingEnd();
        TeardownProfiling();
        TeardownTest();
    }
};
```

### GameMode 接口实现

```cpp
// MyPerfTestGameMode.h
#pragma once
#include "AutomatedPerfTestGameModeBase.h"
#include "MyPerfTestGameMode.generated.h"

UCLASS()
class AMyPerfTestGameMode : public AAutomatedPerfTestGameModeBase
{
    GENERATED_BODY()

public:
    // 重写 C++ 版本的回调（蓝图版本通过 BlueprintImplementableEvent 实现）
    virtual void SetupTest_Implementation() override
    {
        // 在测试开始前执行自定义逻辑
    }

    virtual void RunTest_Implementation() override
    {
        // 测试运行时的自定义逻辑
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `Gauntlet` | 自动化测试框架，所有测试控制器的基类 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `LevelSequence` | Level Sequence 播放（用于 Sequence 测试） |
| `MovieScene` | Sequencer 底层支持 |
| `DeveloperSettings` | Project Settings 配置面板支持 |
| `Json` / `JsonUtilities` | ProfileGo JSON 配置导入导出 |
| `Slate` / `SlateCore` | 编辑器 UI（用于 Launch Extension） |
| `ProjectLauncher` | Project Launcher 集成（仅编辑器，Win64/Linux/Mac） |
| `Projects` | 插件信息查询（仅编辑器） |
| `UnrealEd` | 编辑器功能（仅编辑器） |

**注意**：`ProjectLauncher`、`Projects`、`UnrealEd` 仅在编辑器构建且目标平台为 Win64/Linux/Mac 时链接。运行时构建只需要 `Core` + `Gauntlet`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-11-18 | `eb102e4` | [APT] Fix crash due to MultiWorld having multiple valid Game Worlds | 修复 MultiWorld 场景下多 Game World 共存导致的崩溃，改用世界名匹配 |
| 2025-10-03 | `b5eabe2` | Fix APT/PL2 dependency issue | 修复与 ProjectLauncher 2 的依赖问题 |
| 2025-10-03 | `5524a81` | Ensure AutomatedPerfTest plugin is not enabled by default | 将插件设为默认禁用 |

### 维护评价

- **创建时间**：2024 年 5 月，约 2 年历史
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion=true`，说明 Epic 认为此功能尚不稳定
- **默认禁用**：`Installed=false`，需要手动在插件列表中启用
- **最近活动**：2025 年 11 月有实质性 bug 修复，仍在活跃维护中
- **依赖关系**：强依赖 Gauntlet 框架，这意味着它主要用于 Epic 内部和有 Gauntlet 基础设施的团队
- **已知限制**：
  - ProfileGo 子系统标注为 WIP（"subject to change"）
  - Camera Cut 命名在打包构建中不完整（无法从 Sequencer 获取 spawnable camera 的标签）
  - Replay 路径在某些平台上需要手动复制文件
- **推荐程度**：如果你的团队已经使用 Gauntlet 做自动化测试，这个插件是性能测试的绝佳补充。如果你没有 Gauntlet 基础设施，直接使用此插件的门槛较高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Performance/AutomatedPerfTesting)
- 官方文档（无，.uplugin 中 DocsURL 为空）
- 依赖插件：[Gauntlet](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/Gauntlet)
