# Netcode Unit Test - Unreal Engine

> Exploit unit tests for Unreal Engine and some base Unreal Engine games, based on the Netcode Unit Test framework

| 属性 | 值 |
|---|---|
| 中文名 | 网络单元测试引擎 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NUTUnrealEngine` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-03-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine) | |

## 用途

NUTUnrealEngine 是 NetcodeUnitTest 框架的一部分，其核心用途是**对 Unreal Engine 自身的网络代码（Netcode）进行自动化单元测试和漏洞验证**。

与用于测试你自己的游戏网络逻辑的插件不同，这个插件主要面向**引擎开发者和 QA 人员**，用于：
1.  **复现和验证引擎网络层的已知 Bug 和安全漏洞**（如特定数据包大小导致的崩溃、FText 复制问题等）。
2.  **为引擎网络功能编写回归测试**，确保新的引擎更新不会破坏已有的网络行为（如数据包分片、压缩）。
3.  为像 ShooterGame、QAGame 等 Epic 的示例项目配置特定的测试环境（如默认地图）。

它本质上是一个**内部测试工具**，用于保障 Unreal Engine 网络模块的稳定性和安全性。

## 使用场景

-   你是 Epic Games 的引擎开发者或 QA 工程师，需要为引擎的网络模块编写或运行自动化测试用例。
-   你在为 Unreal Engine 贡献网络相关的 Pull Request，需要验证你的改动没有引入回归问题。
-   你正在研究 Unreal Engine 网络层的安全性和潜在漏洞，需要了解官方是如何进行相关测试的。

## 蓝图用法

此插件提供的功能主要用于 C++ 层面的单元测试框架，没有发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的公开 API。其测试用例（如 `UPacketLimitTest`）通过引擎的自动化测试系统（Automation）运行，而非蓝图图表。

## C++ 用法

此插件的核心用法是**定义继承自 `UClientUnitTest` 或 `UUnitTest` 的测试类**，并实现特定的虚函数来驱动测试流程。

### 头文件引入

```cpp
#include "UnitTests/PacketLimitTest.h" // 示例：测试类头文件
#include "INUTUnrealEngine.h" // 模块接口
```

### 基本用法

以 `UNetBitsTest` 为例，展示一个最简单的测试类框架。该测试旨在验证网络数据位（NetBits）相关的基本功能。

**文件路径**: `Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine/Classes/UnitTests/NetBitsTest.h`

```cpp
// 引入必要的单元测试基类
#include "UnitTests/UnitTest.h"

// 声明一个从 UUnitTest 继承的测试类
UCLASS()
class UNetBitsTest : public UUnitTest
{
    GENERATED_UCLASS_BODY()

public:
    // 重写测试执行函数，实现具体的测试逻辑
    virtual bool ExecuteUnitTest() override;
};

// 在 .cpp 中实现
bool UNetBitsTest::ExecuteUnitTest()
{
    // 在此编写测试网络位操作的代码
    // 例如：创建 FNetBitWriter/FNetBitReader，写入和读取各种类型数据，验证结果
    // ...

    // 测试通过返回 true，失败返回 false
    return true;
}
```

### 进阶用法

更复杂的测试，如 `UPacketLimitTest`，展示了如何控制客户端连接、拦截和检查发送的原始数据包。

**核心逻辑（简化自 `UPacketLimitTest`）**:
1.  **设置测试阶段**：通过 `TestStage` 枚举控制测试流程（如连接、发送特定大小包、验证）。
2.  **拦截数据包**：重写 `NotifySocketSendRawPacket` 函数，在数据包通过底层网络套接字发送前进行拦截和检查。
3.  **验证数据包大小**：在拦截点检查数据包大小 (`LastSocketSendSize`) 是否符合预期 (`TargetSocketSendSize`)。
4.  **前进到下一阶段**：通过 `NextTestStage()` 函数推进测试流程。

```cpp
// 在 NotifySocketSendRawPacket 中拦截和检查数据包
void UPacketLimitTest::NotifySocketSendRawPacket(void* Data, int32 Count, bool& bBlockSend)
{
    LastSocketSendSize = Count;
    // 如果当前包大小不是目标大小，阻止发送（可选）
    if (Count != TargetSocketSendSize)
    {
        bBlockSend = true;
    }
    // 调用基类实现
    Super::NotifySocketSendRawPacket(Data, Count, bBlockSend);
}

// 推进测试阶段的函数
void UPacketLimitTest::NextTestStage()
{
    // 根据当前阶段，设置下一个目标包大小或进入下一个测试阶段
    switch (TestStage)
    {
        case ELimitTestStage::Initial:
            TargetSocketSendSize = /* 计算下一个测试值 */;
            TestStage = ELimitTestStage::TestingLimit;
            break;
        // ... 其他阶段
    }
}
```

## Demo 示例

一个最小的、可编译的自定义网络单元测试示例，基于 `UNetBitsTest` 扩展。

**文件: MyNetTest.h**
```cpp
#pragma once
#include "UnitTests/UnitTest.h"
#include "MyNetTest.generated.h"

UCLASS()
class UMyNetTest : public UUnitTest
{
    GENERATED_UCLASS_BODY()

public:
    virtual bool ExecuteUnitTest() override;
};
```

**文件: MyNetTest.cpp**
```cpp
#include "MyNetTest.h"
#include "Misc/AutomationTest.h" // 用于断言宏

UMyNetTest::UMyNetTest(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

bool UMyNetTest::ExecuteUnitTest()
{
    // 示例：测试一个简单的网络变量复制逻辑
    // 1. 模拟设置一个要复制的变量
    // 2. 模拟序列化（打包）过程
    // 3. 模拟反序列化（解包）过程
    // 4. 验证解包后的值与原始值一致

    int32 OriginalValue = 12345;
    int32 ReplicatedValue = 0;

    // 伪代码：模拟序列化与反序列化
    // FNetBitWriter Writer(0);
    // Writer << OriginalValue;
    // FNetBitReader Reader(Writer.GetWrittenData());
    // Reader << ReplicatedValue;

    // 使用引擎提供的自动化测试断言进行验证
    // 测试条件：值相等，否则输出错误信息
    // TEST_EQUAL(TEXT("Network value replication should match"), OriginalValue, ReplicatedValue);

    // 返回测试是否通过
    return (OriginalValue == ReplicatedValue);
}
```

## 模块依赖

此插件的模块依赖非常集中，主要围绕其核心测试框架。

| 模块 | 用途 |
|---|---|
| `NetcodeUnitTest` | 核心的网络单元测试框架，提供了 `UUnitTest`、`UClientUnitTest` 等基类。 |
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 其他依赖均为 Unreal Engine 的标准基础模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复跨平台打印格式说明符不匹配的问题 |
| 2024-11-06 | `bc63a88d` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 适配引擎构建系统中编译警告设置的新路径 |
| 2023-11-01 | `e4faf8ba` | Enable truncation warnings in NetcodeUnitTest. | 启用 NetcodeUnitTest 模块的截断警告，提升代码质量 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 清理代码中多余的私有头文件包含 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件级别的通用提交 |

### 维护评价

-   **创建时间**：2021年，约5年历史。
-   **近期活动**：最近一次功能相关更新追溯到2023年（启用截断警告），近两年（2025， 2026）的提交均为编译修复或构建系统适配，没有新增测试用例或框架功能。
-   **维护状态**：**维护不活跃**。该插件似乎处于维护模式，仅在引擎底层构建系统或编译器警告规则变更时进行同步更新。它作为一个稳定的测试套件存在，但没有主动的功能迭代。
-   **已知限制**：`EnabledByDefault: false`，且平台限制为 `Win64` 和 `Linux`，表明它是一个非通用、面向特定环境的测试工具。
-   **推荐使用**：**仅推荐**给参与 Unreal Engine 引擎网络模块开发或深度 QA 测试的人员。对于一般的游戏开发者，此插件无需启用或使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine/Classes/UnitTests)