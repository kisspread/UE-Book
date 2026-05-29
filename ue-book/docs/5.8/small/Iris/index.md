# Iris

> Iris networking.

| 属性 | 值 |
|---|---|
| 中文名 | 虹膜网络系统 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Iris` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-13 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Iris) | |

## 用途

Iris 是一个**实验性的（Beta）网络复制系统**，旨在为虚幻引擎提供一个全新的、可能更高效或更灵活的用于同步游戏对象状态的底层网络框架。它并非一个面向特定玩法的功能插件（如动画网络同步），而是一个**系统级别的网络复制引擎/协议**，目标是替代或补充现有的 `Replication` 系统。

## 使用场景

- 你在开发一款对网络同步性能、带宽或确定性有极致要求的多人在线游戏，并希望尝试 UE 最新的网络技术。
- 你正在研究虚幻引擎网络架构的演进，并希望了解下一代复制系统的设计。
- **注意**：由于此插件处于实验性 Beta 状态，且默认禁用，**不建议在正式生产项目中启用**。它主要面向引擎开发者和网络技术研究者。

## 蓝图用法

当前版本的 Iris 插件**没有提供任何公开的蓝图 API**（未发现 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性）。它是一个纯 C++ 的底层运行时模块，需要通过编程接口使用。

## C++ 用法

### 头文件引入

```cpp
#include "Iris/IrisReplication.h" // 推测，具体头文件需查看源码
```

### 基本用法

基于初始提交信息，Iris 默认是**编译排除**的。要启用它，需要在项目的 `.Target.cs` 文件或引擎编译配置中定义相应的宏。

```cpp
// 在项目的 *.Target.cs 文件中添加宏定义，以启用 Iris 复制系统编译
// 这仅允许引擎模块在编译时包含 Iris 复制代码
public class MyGameTarget : TargetRules
{
    public MyGameTarget(TargetInfo Target) : base(Target)
    {
        // ... 其他设置
        // 全局定义宏以启用 Iris
        GlobalDefinitions.Add("WITH_IRIS_REPLICATION=1");
    }
}
```

### 进阶用法

启用宏后，理论上可以使用 Iris 提供的类和函数来创建网络对象、注册属性并进行同步。由于源码仅有一个文件，具体 API 需查阅 `Engine/Plugins/Experimental/Iris/Source/Iris/` 下的代码。核心思路是实现一个新的 `NetDriver`、`NetConnection` 或 `Channel` 逻辑，或者提供一套新的 `FNetSerializer`。

## Demo 示例

以下是一个**概念性**的最小示例，展示如何在项目中准备启用 Iris。**此代码无法直接编译运行，需要 Iris 内部的具体类定义**。

```cpp
// MyIrisReplicationActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyIrisReplicationActor.generated.h"

// 假设 Iris 提供了类似 IReplicationInterface 的基类或接口
// UCLASS()
// class MYGAME_API AMyIrisReplicationActor : public AActor, public IIrisReplicationInterface
// {
//     GENERATED_BODY()
//
// public:
//     AMyIrisReplicationActor();
//
//     // 实现 Iris 要求的复制接口方法
//     virtual void GetLifetimeReplicatedProps_Iris(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
// };

// 实际编译时需要替换为 Iris 提供的真实基类和头文件
UCLASS()
class MYGAME_API AMyIrisReplicationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyIrisReplicationActor();

    UPROPERTY(Replicated)
    float IrisReplicatedValue;
};
```

```cpp
// MyIrisReplicationActor.cpp
#include "MyIrisReplicationActor.h"
#include "Net/UnrealNetwork.h"

AMyIrisReplicationActor::AMyIrisReplicationActor()
{
    bReplicates = true;
}

void AMyIrisReplicationActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(AMyIrisReplicationActor, IrisReplicatedValue);
    // 如果 Iris 有特殊宏，则在此处使用，例如：
    // DOREPLIFETIME_IRIS(AMyIrisReplicationActor, IrisReplicatedValue);
}
```

## 模块依赖

此插件仅有 `Iris` 一个 Runtime 模块。从其功能（网络复制）推断，它极大概率依赖引擎的网络核心模块。

| 模块 | 用途 |
|---|---|
| `NetCore` | 底层网络抽象和功能，Iris 作为复制系统必然依赖 |
| `Networking` 或 `Sockets` | 可能的网络套接字或传输层依赖 |

**注意**：由于 Iris 是实验性底层模块，其依赖可能随版本变化。最准确的依赖信息应查看 `Engine/Plugins/Experimental/Iris/Source/Iris/Iris.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-17 | `c8fb077d` | Iris goes Beta. | Iris 插件正式进入 Beta 测试阶段。 |
| 2025-09-08 | `a8ec8516` | Iris Beta | 插件元数据更新，标记为 Beta 版本。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件层级的目录结构或构建系统更新，波及 Iris。 |
| 2022-10-12 | `acc15538` | Changes to allow compiling engine modules with Iris replication code by default, and link against mo | 改变编译配置，允许默认包含 Iris 复制代码并链接更多模块。 |
| 2022-10-07 | `31ed81a3` | Change Iris plugin status to Experimental. | 将插件状态从内部实验改为公开的 Experimental 状态。 |

### 维护评价

Iris 是一个诞生于 2022 年的**实验性**项目。从 Git 历史看，在初期（2022年）有过活跃的开发，但在此后长达近两年（2023-2024）的时间里**没有实质性功能更新**。直到 2025 年 9 月，连续两次提交将插件状态升级为 **Beta**，表明 Epic 可能重新开始推进该项目。

- **活跃程度**：长期不活跃后近期有复苏迹象。
- **状态**：从 Experimental 升级为 Beta，意味着进入了更广泛的内部测试阶段，但距离稳定版本仍有距离。
- **风险**：API 可能不稳定，存在重大变更的可能。
- **推荐**：**仅适用于**对虚幻引擎网络底层有深入研究需求、愿意承担技术风险和追踪频繁更新的开发者或技术研究者。普通项目**强烈不推荐**使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Iris)
- [官方文档] 暂无
- [测试用例] 在提供的插件目录下未发现独立的测试模块或文件。