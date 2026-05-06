# Gauntlet

> Provides a helper class for creating and managing tests in your game

| 属性 | 值 |
|---|---|
| 中文名 | 游戏测试框架 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Gauntlet` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Gauntlet) | |

## 用途

Gauntlet 是 UE 的实验性测试框架，提供了一套轻量级、模块化的自动测试基础设施。它的核心是一个 `FGauntletModule`，负责管理多个 `UGauntletTestController`，并通过状态机（State Machine）驱动测试流程。开发者只需继承 `UGauntletTestController`，重写 `OnInit`、`OnTick`、`OnStateChange` 等回调，即可快速实现针对游戏特定逻辑的自动化测试。

相比于传统的 FunctionalTest（基于关卡 Actor），Gauntlet 更适用于**无 UI、纯逻辑的游戏流程测试**，例如：

- 启动测试（验证游戏能否正常进入主菜单）
- 地图加载测试
- 会话流程测试
- 错误注入测试（通过 `UGauntletTestControllerErrorTest` 模拟崩溃）

## 使用场景

- 你需要在游戏启动后自动执行一系列验证步骤（如资源加载、网络连接），并在失败时记录结果 → Gauntlet 的状态机机制可以轻松驱动这类阶段性测试。
- 你希望编写一个能够持续运行、根据游戏世界状态自动切换行为的测试控制器 → 通过 `SetGameStateToTestStateMapping` 将 AGameState 子类映射到自定义状态，控制器即可在状态变化时收到通知。
- 你需要集成到 CI/CD 管线，通过命令行参数 `-gauntlet=MyController` 在无头服务器上自动运行测试并退出。

## 蓝图用法

Gauntlet 未公开任何 BlueprintCallable 或 BlueprintReadWrite 属性。其所有接口均为纯 C++，适合在 C++ 开发环境中使用。

## C++ 用法

### 头文件引入

```cpp
#include "GauntletModule.h"
#include "GauntletTestController.h"
```

### 基本用法

创建一个自定义测试控制器，重写关键生命周期函数。

*GauntletTestControllerMyTest.h*
```cpp
#pragma once

#include "GauntletTestController.h"
#include "GauntletTestControllerMyTest.generated.h"

UCLASS()
class UGauntletTestControllerMyTest : public UGauntletTestController
{
    GENERATED_BODY()

protected:
    virtual void OnInit() override;
    virtual void OnTick(float TimeDelta) override;
    virtual void OnStateChange(FName OldState, FName NewState) override;
};
```

*GauntletTestControllerMyTest.cpp*
```cpp
#include "GauntletTestControllerMyTest.h"

void UGauntletTestControllerMyTest::OnInit()
{
    // 初始化逻辑，例如注册游戏状态映射
    TMap<UClass*, FName> StateMapping;
    // StateMapping.Add(AMyGameState::StaticClass(), FName("Playing"));
    FGauntletModule* Module = FModuleManager::GetModulePtr<FGauntletModule>("Gauntlet");
    if (Module)
    {
        Module->SetGameStateToTestStateMapping(StateMapping);
    }
}

void UGauntletTestControllerMyTest::OnTick(float TimeDelta)
{
    // 每帧检测逻辑，例如检查某个条件达成后结束测试
    if (/* some condition */)
    {
        EndTest(ETestResult::Passed);
    }
}

void UGauntletTestControllerMyTest::OnStateChange(FName OldState, FName NewState)
{
    // 响应游戏状态变化
    if (NewState == FName("Playing"))
    {
        // 开始记录性能数据
    }
}
```

### 进阶用法

结合 `UGauntletTestControllerBootTest` 实现启动测试。只需重写 `IsBootProcessComplete()` 判断启动流程是否完成。

```cpp
UCLASS()
class UMyBootTestController : public UGauntletTestControllerBootTest
{
    GENERATED_BODY()

protected:
    virtual bool IsBootProcessComplete() const override
    {
        // 当主界面加载完成，或某个全局变量被设置时返回 true
        return GEngine->IsInitialized();
    }
};
```

通过命令行参数启动测试（在项目设置中注册控制器名，或在 `DefaultEngine.ini` 的 `[Gauntlet]` 段中配置）。

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何使用 Gauntlet 编写一个简单的“等待 5 秒后自动结束”的测试。

*GauntletWaitAndExit.h*
```cpp
#pragma once

#include "GauntletTestController.h"
#include "GauntletWaitAndExit.generated.h"

UCLASS()
class UGauntletWaitAndExit : public UGauntletTestController
{
    GENERATED_BODY()

protected:
    float ElapsedTime = 0.0f;

    virtual void OnInit() override
    {
        ElapsedTime = 0.0f;
    }

    virtual void OnTick(float TimeDelta) override
    {
        ElapsedTime += TimeDelta;
        if (ElapsedTime >= 5.0f)
        {
            EndTest(ETestResult::Passed);
        }
    }
};
```

*GauntletWaitAndExit.cpp*
```cpp
#include "GauntletWaitAndExit.h"
// 无需额外实现，因为所有函数已在头文件内联定义。
```

将此控制器类放入你的项目，然后在启动时添加命令行参数 `-gauntlet=GauntletWaitAndExit`，5 秒后测试会结束并退出。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-07-21 2415c7a Fix two types of nodiscard warnings seen when building with Clang 20
- 2025-04-23 93a1308 Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins
- 2025-04-07 8a50a64 UE: Skip ticking gauntlet if ticked while there is no world.
- 2025-02-12 8964a77 Fix odd spacing in UGauntletTestControllerBootTest and missing virtual keyword on the OnTick function
- 2024-11-10 66e9bb3 Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base

### 维护评价

Gauntlet 自 2024-11-10 创建至今约 1 年，仍处于实验性阶段（IsBetaVersion=true）。从 git 历史看，2025 年有多达 4 次 commit，涉及编译警告修复、代码格式修正、逻辑优化（避免在无 World 时 tick），表明团队仍在积极维护。尽管目前功能较为基础（仅提供框架），但结构清晰，适合需要自定义自动化测试的项目。对于新项目，如果未引入其他成熟测试框架，Gauntlet 是一个值得尝试的轻量级方案。潜在限制：缺乏蓝图支持、需要手动配置状态映射、无官方文档（DocsURL 为空）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Gauntlet)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Gauntlet/Tests)（若存在）