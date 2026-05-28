# Gauntlet

> Provides a helper class for creating and managing tests in your game

| 属性 | 值 |
|---|---|
| 中文名 | 自动化测试框架 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Gauntlet` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-06-06 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Gauntlet) | |

## 用途

Gauntlet 是一个用于 UE 项目编写和运行**自动化端到端测试**的运行时框架。它解决的核心问题是：如何让游戏在无人值守的情况下自动运行，并通过自定义逻辑判断测试是否通过。

与 UE 自带的 Automation 框架不同，Gauntlet 是面向**完整游戏流程**的测试——它启动真实的游戏实例，驱动地图切换、状态变化，让你用 C++ 编写的"测试控制器"监控整个游戏生命周期，并在满足条件后报告结果并退出。

典型用例：CI/CD 流水线中自动启动游戏，验证启动是否成功、主菜单是否加载、特定关卡能否正常运行、是否存在崩溃或性能问题等。

## 使用场景

- 你在 CI/CD 流水线中需要自动化验证游戏能否正常启动 → 用 `UGauntletTestControllerBootTest`
- 你需要自定义复杂的端到端测试逻辑（如等待特定游戏状态后截图） → 继承 `UGauntletTestController`
- 你需要监控长时间运行的游戏稳定性（心跳机制） → 在控制器中调用 `MarkHeartbeatActive`
- 你需要将游戏状态映射为测试状态，自动触发控制器响应 → 使用 `SetGameStateToTestStateMapping`

## 蓝图用法

Gauntlet 框架是纯 C++ 实现，不提供蓝图节点。测试控制器通过命令行参数 `-gauntlet=ControllerClassName` 指定，所有逻辑都在 C++ 侧完成。

## C++ 用法

### 头文件引入

```cpp
#include "GauntletModule.h"
#include "GauntletTestController.h"
```

### 基本用法

创建自定义测试控制器，继承 `UGauntletTestController` 并重写生命周期回调：

```cpp
// MyTestController.h
#pragma once
#include "GauntletTestController.h"
#include "MyTestController.generated.h"

UCLASS()
class UMyTestController : public UGauntletTestController
{
    GENERATED_BODY()

protected:
    virtual void OnInit() override;
    virtual void OnPostMapChange(UWorld* World) override;
    virtual void OnTick(float TimeDelta) override;
    virtual void OnStateChange(FName OldState, FName NewState) override;
};
```

```cpp
// MyTestController.cpp
#include "MyTestController.h"

void UMyTestController::OnInit()
{
    // 控制器初始化，启动测试逻辑
    UE_LOG(LogGauntlet, Log, TEXT("Test controller initialized"));
}

void UMyTestController::OnPostMapChange(UWorld* World)
{
    // 地图加载完成后的回调
    UE_LOG(LogGauntlet, Log, TEXT("Map loaded: %s"), *GetCurrentMap());
}

void UMyTestController::OnTick(float TimeDelta)
{
    // 每帧调用，检查测试条件
    // 例如：等待 10 秒后认为测试通过
    if (GetTimeInCurrentState() > 10.0)
    {
        EndTest(0); // 退出码 0 表示成功
    }
}

void UMyTestController::OnStateChange(FName OldState, FName NewState)
{
    UE_LOG(LogGauntlet, Log, TEXT("State changed: %s -> %s"), *OldState.ToString(), *NewState.ToString());
}
```

通过命令行启动：

```
UnrealEditor MyProject -game -gauntlet=UMyTestController
```

### 进阶用法

注册状态映射，让控制器自动响应游戏状态变化：

```cpp
// 在游戏模块初始化时（或自定义初始化函数中）
void UMyGameInstance::InitForGauntlet()
{
    FGauntletModule& GauntletModule = FModuleManager::GetModuleChecked<FGauntletModule>("Gauntlet");

    // 将 AGameState 子类映射为测试状态名
    TMap<UClass*, FName> GameStateMapping;
    GameStateMapping.Add(AMyMenuGameState::StaticClass(), FName("MenuState"));
    GameStateMapping.Add(AMyGameplayGameState::StaticClass(), FName("GameplayState"));
    GauntletModule.SetGameStateToTestStateMapping(GameStateMapping);

    // 将地图名映射为测试状态名
    TMap<FString, FName> WorldMapping;
    WorldMapping.Add(TEXT("/Game/Maps/MainMenu"), FName("FrontendMap"));
    WorldMapping.Add(TEXT("/Game/Maps/Level01"), FName("GameplayMap"));
    GauntletModule.SetWorldToTestStateMapping(WorldMapping);
}
```

手动广播状态变化：

```cpp
// 在任意位置手动触发状态广播
FGauntletModule& Gauntlet = FModuleManager::GetModuleChecked<FGauntletModule>("Gauntlet");
Gauntlet.BroadcastStateChange(FName("CustomTestState"));
```

截图和心跳机制：

```cpp
void UMyTestController::OnInit()
{
    // 设置每 5 秒自动截图
    FGauntletModule* Gauntlet = GetGauntlet();
    if (Gauntlet)
    {
        Gauntlet->SetScreenshotPeriod(5.0f);
    }
}

void UMyTestController::OnTick(float TimeDelta)
{
    // 定期标记心跳活跃，防止外部监控判定为无响应
    if (/* 某个有意义的动作发生 */)
    {
        MarkHeartbeatActive(TEXT("Checkpoint reached"));
    }
}
```

## Demo 示例

一个完整的最小测试控制器，验证游戏能否在 60 秒内进入 Gameplay 状态：

```cpp
// SimpleGameplayTestController.h
#pragma once
#include "GauntletTestController.h"
#include "SimpleGameplayTestController.generated.h"

UCLASS()
class USimpleGameplayTestController : public UGauntletTestController
{
    GENERATED_BODY()

protected:
    virtual void OnInit() override;
    virtual void OnStateChange(FName OldState, FName NewState) override;
    virtual void OnTick(float TimeDelta) override;

private:
    double TestStartTime = 0.0;
};
```

```cpp
// SimpleGameplayTestController.cpp
#include "SimpleGameplayTestController.h"
#include "GauntletModule.h"

void USimpleGameplayTestController::OnInit()
{
    TestStartTime = FPlatformTime::Seconds();
    UE_LOG(LogGauntlet, Log, TEXT("SimpleGameplayTest started"));
}

void USimpleGameplayTestController::OnStateChange(FName OldState, FName NewState)
{
    if (NewState == FName("GameplayState"))
    {
        UE_LOG(LogGauntlet, Log, TEXT("Gameplay state reached, test PASSED"));
        EndTest(0);
    }
}

void USimpleGameplayTestController::OnTick(float TimeDelta)
{
    double Elapsed = FPlatformTime::Seconds() - TestStartTime;
    if (Elapsed > 60.0)
    {
        UE_LOG(LogGauntlet, Error, TEXT("Timeout: gameplay state not reached in 60s"));
        EndTest(1); // 超时失败
    }
    else
    {
        // 每 5 秒发一次心跳
        MarkHeartbeatActive();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新版 UE_LOGF 格式 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充缺失的头文件包含和前向声明 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误查找替换后的二次修正 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配 FCoreDelegates API 变更，修复注册缺失问题 |

### 维护评价

- **实验性状态**：标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，长期停留在实验性阶段
- **更新频率**：近期有更新，但全部是**引擎代码清理**（头文件迁移、日志宏替换、API 适配），非功能性改动
- **核心功能未变化**：自 2018 年创建以来，测试控制器的 API（OnInit、OnTick、OnStateChange、EndTest）基本未变，说明框架已经稳定
- **风险提示**：虽然仍在引擎中维护，但 8 年未脱离实验性标签，Epic 可能随时废弃或替换为其他测试方案
- **推荐程度**：适用于需要在 CI/CD 中运行完整游戏端到端测试的项目。对于简单的单元测试，建议使用 UE 内置的 Automation 框架

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Gauntlet)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Gauntlet)（插件内含内置测试控制器 `BootTest` 和 `ErrorTest`）