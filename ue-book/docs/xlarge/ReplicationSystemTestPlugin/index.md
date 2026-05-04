# Replication System Test Plugin

> Unit and functional tests for the network replication system.

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ReplicationSystemTestPlugin` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2022-07-13 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ReplicationSystemTestPlugin) | |

## 用途

本插件并非面向最终用户的功能性插件，而是 Epic Games 内部用于验证其新一代网络复制系统（Iris）正确性的**自动化测试框架**。它提供了一套基础设施和测试用例，用于对复制系统的核心功能（如对象同步、RPC、属性复制、生命周期管理等）进行单元测试和功能测试，确保系统在开发迭代中的稳定性和可靠性。

## 使用场景

- **网络系统开发者**：在开发或修改 Iris 复制系统时，运行此插件中的测试用例以验证改动是否引入回归问题。
- **引擎测试工程师**：将此插件集成到自动化测试流程中，作为网络模块质量保证的一部分。
- **高级用户/研究者**：希望深入理解 Iris 复制系统内部工作原理，可以通过阅读和调试这些测试用例来学习。

## 蓝图用法

无（纯C++测试框架）。

## C++ 用法

本插件主要提供测试基础设施和测试用例，其公共 API 较为简单，主要用于支持测试框架的运行。

### 头文件引入

```cpp
#include "ReplicationSystemTestPlugin/NetworkAutomationTest.h"
```

### 基本用法

插件的核心是提供一个日志类别和一个用于输出测试摘要的函数。测试用例通常使用 UE 内置的自动化测试框架（如 `IMPLEMENT_SIMPLE_AUTOMATION_TEST`）或 Catch2 来编写。

```cpp
// 示例：一个简单的网络自动化测试
#include "Misc/AutomationTest.h"
#include "ReplicationSystemTestPlugin/NetworkAutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyNetworkTest, "MyGame.Network.Replication", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FMyNetworkTest::RunTest(const FString& Parameters)
{
    // 测试逻辑...
    UE_LOG(LogNetworkAutomationTest, Display, TEXT("Running a basic replication test."));

    // 在测试结束时，可以调用此函数来打印插件的测试摘要（如果插件实现了该功能）
    UE::Net::PrintNetworkAutomationTestSummary();

    return true; // 返回 true 表示测试通过
}
```

### 进阶用法

由于这是一个测试插件，其“进阶用法”体现在编写针对复制系统复杂场景的测试用例上。这些用例通常位于插件的 `Private` 或 `Tests` 目录下，用于验证：
- 对象的创建、销毁和重新连接同步。
- 属性复制的优先级、条件复制和自定义序列化。
- RPC（远程过程调用）的可靠性和顺序。
- 复制系统在对象数量巨大、网络条件不佳（如丢包、延迟）下的表现。

## Demo 示例

以下是一个最小化的、可编译的测试用例示例，展示了如何利用本插件提供的日志类别。

```cpp
// MyReplicationTest.h
#pragma once

#include "CoreMinimal.h"

// 声明一个自定义的测试日志类别（可选，也可以直接使用插件提供的）
DECLARE_LOG_CATEGORY_EXTERN(LogMyReplicationTest, Display, All);

// MyReplicationTest.cpp
#include "MyReplicationTest.h"
#include "Misc/AutomationTest.h"
#include "ReplicationSystemTestPlugin/NetworkAutomationTest.h"

DEFINE_LOG_CATEGORY(LogMyReplicationTest);

// 定义一个简单的自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FBasicReplicationTest,
    "Project.Network.Iris.BasicTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter
)

bool FBasicReplicationTest::RunTest(const FString& Parameters)
{
    // 1. 测试前置设置
    UE_LOG(LogMyReplicationTest, Display, TEXT("Starting basic Iris replication test..."));

    // 2. 执行测试逻辑 (此处为占位)
    bool bTestPassed = true; // 假设测试通过

    // 3. 测试后置清理与结果输出
    if (bTestPassed)
    {
        UE_LOG(LogMyReplicationTest, Display, TEXT("Test PASSED."));
    }
    else
    {
        UE_LOG(LogMyReplicationTest, Error, TEXT("Test FAILED."));
    }

    // 4. 调用插件提供的摘要函数（如果需要）
    UE::Net::PrintNetworkAutomationTestSummary();

    return bTestPassed;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Catch2` | 第三方 C++ 单元测试框架，插件中部分测试用例可能基于此框架编写。 |

## 维护状态

### 近期更新

- 15de1db76bf6 Iris - Fixed issue with ObjectPoller not force polling ObjectReferences for pushbased fragments in mixed protocols after GC
  *修复了在垃圾回收后，混合协议下基于推送的片段中对象轮询器未强制轮询对象引用的问题。*
- 92e981630a28 Iris * Deprecated NetObjectFactory::DestroyReplicatedObject and replaced it with DetachedFromReplication * The new function will receive callbacks for any object removed from replication not just those flagged to be destroyed.
  *废弃了 `NetObjectFactory::DestroyReplicatedObject`，并用 `DetachedFromReplication` 替代。新函数将为任何从复制中移除的对象提供回调，而不仅仅是那些标记为销毁的对象。*
- c594b2bf5bff Iris - Test that caused NCL due to not-split part sent by hugeobject path failed to fit in packet.
  *修复了一个因巨大对象路径发送的未分割部分无法装入数据包而导致网络连接丢失（NCL）的测试。*
- 60484771c374 Iris * Renamed NetObjectFactory::SubObjectDestroyedFromReplication to SubObjectDetachedFromReplication * Clarified the function's documentation at the same time
  *将 `NetObjectFactory::SubObjectDestroyedFromReplication` 重命名为 `SubObjectDetachedFromReplication`，并同时澄清了该函数的文档。*
- 59a9ebcd4dd7 Iris - Fixed bug with FastArraySerialzierFragment if using not replicating items
  *修复了当使用不复制的项时，`FastArraySerializerFragment` 中的一个 bug。*

### 维护评价

- **活跃维护**：从近期提交记录看，该插件仍在被积极维护，用于测试和修复 Iris 复制系统的核心问题。
- **核心测试资产**：作为 Epic 内部网络系统开发的关键测试套件，其更新与 Iris 复制系统的开发紧密同步。
- **实验性/内部使用**：`EnabledByDefault: false` 表明它主要面向开发者和测试环境，不建议在最终产品中启用。
- **推荐使用**：对于需要测试或学习 Iris 复制系统的开发者，此插件是宝贵的参考和工具。对于普通项目开发，无需关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ReplicationSystemTestPlugin)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ReplicationSystemTestPlugin/Tests) (如果存在)