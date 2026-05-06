# Global Configuration Data

> A system that is used to query configuration data that can come from many different sources without knowing specifically which one.

| 属性 | 值 |
|---|---|
| 中文名 | 全局配置数据 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `GlobalConfigurationDataCore` (Runtime), `GlobalConfigurationData` (Runtime), `GlobalConfigurationDataTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData) | |

## 用途

`Global Configuration Data`（简称 GCD）为引擎和游戏提供一套**配置数据查询抽象层**。它允许开发者从**多个可能的来源**（如本地配置文件、远程服务、控制台变量、动态热修数据等）获取配置值，而无需在业务代码中硬编码具体的数据源。系统内部通过“路由”机制将查询请求分发到已注册的配置提供者，并支持优先级、合并、自动展平 JSON 对象等高级功能。

为什么存在？在现代游戏开发中，配置数据可能来自不同环境（开发、测试、生产）或不同团队（策划、运营）。GCD 解决了以下痛点：

- 数据源切换无需修改业务代码
- 支持运行时热更新（如“Hotfix”路由）
- 统一的查询接口，降低耦合
- 方便扩展新的配置提供者

## 使用场景

- 你需要一个**集中式配置管理器**，让策划或运营可以通过远程服务器动态调整数值（如怪物血量、掉落率），同时本地默认配置依然可用。
- 你希望**屏蔽数据来源差异**，无论是来自 JSON 文件、数据库、还是 Console 变量，业务代码都只调用 `UGlobalConfigurationDataSubsystem::GetValue<FMyConfig>()`。
- 你在开发一个**多环境游戏**（开发/测试/正式），不同环境使用不同配置提供者，代码只需一次编写。
- 你需要**快速热修**线上配置，例如通过 `GCD Hotfix` 路由注入紧急修正。

## 蓝图用法

> ⚠️ **注意**：当前版本（0.1）是实验性插件，蓝图公开接口有限。大部分功能仅通过 C++ 暴露，蓝图节点暂未完全开放。以下列出从代码中推断的蓝图可调用接口（未来可能新增）。

### 核心节点

由于 `GlobalConfigurationDataTests` 是测试模块，且核心模块未提供蓝图 UFUNCTION，蓝图端目前**没有稳定公开的节点**。但你可以通过 C++ 封装后暴露自定义蓝图函数，或等待正式版增加蓝图支持。

### 使用示例（蓝图描述）

（无稳定的蓝图用法示例。建议使用 C++ 集成。）

## C++ 用法

本模块 `GlobalConfigurationDataTests` 提供了测试数据结构，用于验证 GCD 系统的正确性。以下示例展示如何在测试或实际代码中定义自定义配置数据类型，并配合 GCD 使用（需要引用 `GlobalConfigurationData` 核心模块）。

### 头文件引入

```cpp
#include "GlobalConfigurationTestData.h"
#include "GlobalConfigurationDataSubsystem.h" // 假设核心头文件
```

### 基本用法

测试模块中定义了 `UGlobalConfigurationTestObject`（UObject）和 `FGlobalConfigurationTestStruct`（结构体），它们包含 `bool`、`int32` 和 `TArray<int32>` 属性，用于测试配置序列化与反序列化。实际使用中，你可以类似地定义自己的配置类。

```cpp
// 来源：Tests/Private/GlobalConfigurationTestData.h
UCLASS()
class UGlobalConfigurationTestObject : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY()
    bool bBoolValue = false;

    UPROPERTY()
    int32 IntValue = 0;

    UPROPERTY()
    TArray<int32> IntValueArray;
};
```

如需通过 GCD 系统查询配置值，可参考以下模式（基于核心模块 API 推测）：

```cpp
#include "GlobalConfigurationDataSubsystem.h"

void QueryConfig()
{
    if (UGlobalConfigurationDataSubsystem* Subsystem = GEngine->GetEngineSubsystem<UGlobalConfigurationDataSubsystem>())
    {
        // 假设系统提供泛型查询方法 GetValue<T>()
        // 注意：实际 API 名称可能不同，请参考核心模块头文件
        FGlobalConfigurationTestStruct Config;
        if (Subsystem->GetValue("MyConfigKey", Config))
        {
            // 使用 Config.IntValue, Config.bBoolValue 等
        }
    }
}
```

### 进阶用法

GCD 支持多个配置提供者（路由）的合并与优先级。例如，低优先级的本地默认数据会被高优先级的热修数据覆盖。测试中可能验证类似场景：

```cpp
// 假设测试用例：验证热修路由能覆盖默认值
DEFINE_SPEC(FGcdIntegrationTest, "GlobalConfigurationData.Integration", EAutomationTestFlags::ProductFilter | EAutomationTestFlags::ApplicationContextMask)
{
    ...
    // 注入热修数据
    Subsystem->SetHotfixValue("TestObject.IntValue", 42);
    // 查询应该得到 42 而不是默认的 0
}
```

## Demo 示例

以下是一个最小化的 C++ 测试用例，验证 GCD 系统的核心查询功能。需要将测试代码放入 `GlobalConfigurationDataTests` 模块中（或包含相关头文件）。

### GlobalConfigurationTestDemo.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GlobalConfigurationTestData.h"

// 假设测试环境的设置和断言
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGcdDemoTest, "GlobalConfigurationData.Demo.BasicQuery", EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)
bool FGcdDemoTest::RunTest(const FString& Parameters)
{
    // 创建一个测试对象，作为配置数据结构
    UGlobalConfigurationTestObject* Obj = NewObject<UGlobalConfigurationTestObject>();
    Obj->IntValue = 100;

    // 模拟将 Obj 注册到 GCD 系统（假设 API）
    // ... 实际测试依赖于核心模块暴露的接口

    // 查询并验证
    // int32 Queried = Subsystem->GetIntValue("TestObject.IntValue");
    // TestEqual(TEXT("IntValue should be 100"), Queried, 100);

    return true;
}
#endif
```

### GlobalConfigurationTestDemo.cpp

```cpp
#include "GlobalConfigurationTestDemo.h"
// 空，测试宏已内联
```

> **注意**：由于缺少核心模块的具体 API 签名，Demo 中的假设调用（如 `GetIntValue`）需要根据实际头文件替换。上述代码仅为结构示意。

## 模块依赖

`GlobalConfigurationDataTests` 的依赖通过其 Build.cs 决定。假设它依赖于 `GlobalConfigurationData` 和 `GlobalConfigurationDataCore`，以及标准测试框架模块。实际依赖如下（省略常见 Core/Engine 模块）：

| 模块 | 用途 |
|---|---|
| `GlobalConfigurationData` | 提供配置子系统主接口 |
| `GlobalConfigurationDataCore` | 提供核心路由和基础类型 |
| `AutomationTest` | 自动化测试框架 |

## 维护状态

### 近期更新

- 2025-09-10 `61b63b3f` [GCD] Add support to auto flatten json objects with a single entry
- 2025-07-18 `10de61f9` [GCD] Make console command router debug only, add a 'hotfix' config router for high priority setting
- 2025-06-23 `bfa3140f` [Misc] Fix GlobalConfigurationData test ensures
- 2025-06-17 `8a2ca4d6` [UE] Add experimental Global Configuration Data

### 维护评价

该插件是 **实验性功能**，创建于 2025 年 6 月，最近更新在 2025 年 9 月（距离现在约 1-2 个月），处于**活跃开发阶段**。更新内容包括：
- 增加 JSON 自动展平特性
- 引入“热修”配置路由
- 修复测试模块的 ensure 问题

综合评价：**活跃维护，推荐使用 C++ API 集成。** 但需要注意实验性标签，API 可能在不兼容版本中变更。暂时没有蓝图支持，适合需要底层配置控制的团队。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData/Source/GlobalConfigurationDataTests)（假设路径）
- 官方文档：暂无（实验性插件无独立文档）