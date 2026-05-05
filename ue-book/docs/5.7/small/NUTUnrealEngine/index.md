# Netcode Unit Test - Unreal Engine

> Exploit unit tests for Unreal Engine and some base Unreal Engine games, based on the Netcode Unit Test framework

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | NUTUnrealEngine (UncookedOnly) |
| 创建时间 | 2021-03-23 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine) | |

## 用途

NUTUnrealEngine 是 [NetcodeUnitTest](../NetcodeUnitTest/index.md) 框架的**具体测试用例集合**，专门为 Unreal Engine 自身的网络代码和 Epic 旗下示例游戏（ShooterGame、QAGame、UnrealTournament）提供单元测试和漏洞利用（exploit）测试。

它解决的核心问题是：**验证 UE 网络代码中的已知 bug 是否已被修复**。每个测试用例会记录对应的 JIRA ID 和 changelist，启动服务器/客户端实例，发送特定的网络数据包，然后检测服务器是否崩溃或异常——从而确认漏洞补丁是否生效。

与 NetcodeUnitTest（框架本身）不同，这个 plugin 不提供任何基础设施，只包含纯粹的测试用例。

## 使用场景

- 你在维护 UE 网络代码，需要回归测试确认旧漏洞不会复现 → 启用此 plugin
- 你在开发自定义网络协议扩展，想参考 Epic 的测试写法 → 阅读此 plugin 源码
- 你在做 UE 引擎 CI，需要自动化检测网络安全性 → 将此 plugin 的测试纳入自动化管线

**注意**：此 plugin 类型为 `UncookedOnly`，仅在编辑器/开发环境中可用，不会被打包到发布版本中。仅支持 **Win64** 和 **Linux** 平台。

## 蓝图用法

此 plugin 不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它是纯 C++ 的自动化测试模块，不提供蓝图接口。

## C++ 用法

### 头文件引入

```cpp
#include "INUTUnrealEngine.h"
```

### 模块接口

模块提供标准的加载/可用性检查接口：

```cpp
// 检查模块是否已加载
if (INUTUnrealEngine::IsAvailable())
{
    // 获取模块实例
    INUTUnrealEngine& Module = INUTUnrealEngine::Get();
}
```

### 测试用例结构

此 plugin 包含以下测试用例（均继承自 NetcodeUnitTest 框架的基类）：

| 测试类 | 类型 | 基类 | 状态 | 说明 |
|---|---|---|---|---|
| `UNetBitsTest` | Test | `UUnitTest` | 活跃 | 验证 `FBitWriter`/`FBitReader` 的序列化正确性 |
| `UFTextCrash` | Exploit | `UClientUnitTest` | 活跃 | 验证空 FText 通过 RPC 发送时的崩溃修复 |
| `UPacketLimitTest` | Exploit | `UClientUnitTest` | 已禁用 (`#if 0`) | 测试网络包大小限制的边界情况 |
| `UPacketLimitTest_Oodle` | Exploit | `UPacketLimitTest` | 已禁用 (`#if 0`) | Oodle 压缩下的包大小限制测试 |
| `UUTT61_DebugReplicateData` | Exploit | `UClientUnitTest` | 已废弃 | UT 的 GameplayDebuggingComponent 数组溢出漏洞 |

### 基本用法：编写单元测试（UNetBitsTest 示例）

`UNetBitsTest` 是最简单的测试——不需要服务器/客户端，直接在本地验证位序列化逻辑：

```cpp
// 来源: Classes/UnitTests/NetBitsTest.h + Private/UnitTests/NetBitsTest.cpp
UCLASS()
class UNetBitsTest : public UUnitTest
{
    GENERATED_UCLASS_BODY()
public:
    virtual bool ExecuteUnitTest() override;
};

// 构造函数中设置测试元数据
UNetBitsTest::UNetBitsTest(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    UnitTestName = TEXT("NetBitsTest");
    UnitTestType = TEXT("Test");
    UnitTestDate = FDateTime(2016, 03, 19);
    UnitTestTimeout = 60;
    bWorkInProgress = true;

    ExpectedResult.Add(TEXT("ShooterGame"), EUnitTestVerification::VerifiedFixed);
}

bool UNetBitsTest::ExecuteUnitTest()
{
    TMap<FString, bool> TestResults;

    // 测试 SerializeInt 在不同范围下的读写一致性
    {
        FBitWriter Writer(0, true);
        uint32 WriteValue = 0;
        Writer.SerializeInt(WriteValue, 2);  // 范围为 2，应占用 1 bit

        FBitReader Reader(Writer.GetData(), Writer.GetNumBits());
        uint32 ReadValue = 0;
        Reader.SerializeInt(ReadValue, 2);

        TestResults.Add(TEXT("Two range write"), !Writer.IsError() && Writer.GetNumBits() == 1);
        TestResults.Add(TEXT("Two range read"), !Reader.IsError() && ReadValue == WriteValue);
    }

    // 测试 SerializeIntPacked 在不同 bit 偏移下的正确性
    {
        const uint32 TestValues[] = { 0U, 0x43U, 0x1234U, 0xFFFFFFFFU };
        for (uint32 BitOffset = 0; BitOffset <= 32; ++BitOffset)
        {
            for (size_t TestIt = 0; TestIt != 4; ++TestIt)
            {
                FBitWriter Writer(256, false);
                uint32 Padding = 0xFFFFFFFFU;
                Writer.SerializeBits(&Padding, BitOffset);
                Writer.SerializeIntPacked(TestValues[TestIt]);

                FBitReader Reader(Writer.GetData(), Writer.GetNumBits());
                uint32 ReadPadding = 0;
                Reader.SerializeBits(&ReadPadding, BitOffset);
                uint32 ReadValue = 0;
                Reader.SerializeIntPacked(ReadValue);

                // 验证读写一致
            }
        }
    }
    // ...
}
```

### 进阶用法：编写漏洞利用测试（UFTextCrash 示例）

`UFTextCrash` 演示了典型的客户端-服务器 exploit 测试模式：

```cpp
// 来源: Classes/UnitTests/FTextCrash.h + Private/UnitTests/FTextCrash.cpp
UCLASS()
class UFTextCrash : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()
public:
    virtual void InitializeEnvironmentSettings() override;
    virtual void ExecuteClientUnitTest() override;
    virtual void NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                   const TArray<FString>& InLogLines) override;
};

// 构造函数：设置测试标志
UFTextCrash::UFTextCrash(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    UnitTestName = TEXT("FTextCrash");
    UnitTestType = TEXT("Exploit");
    UnitTestDate = FDateTime(2014, 07, 11);
    UnitTestBugTrackIDs.Add(TEXT("JIRA UE-5691"));
    UnitTestCLs.Add(TEXT("2367048 (//depot/UE4/)"));

    // 标记多个游戏项目中此漏洞已修复
    ExpectedResult.Add(TEXT("ShooterGame"), EUnitTestVerification::VerifiedFixed);
    ExpectedResult.Add(TEXT("FortniteGame"), EUnitTestVerification::VerifiedFixed);
    // ...

    // 设置测试标志：启动服务器、接受玩家控制器、需要 NUTActor、
    // 期望服务器崩溃、期望断开连接
    SetFlags<EUnitTestFlags::LaunchServer | EUnitTestFlags::AcceptPlayerController |
             EUnitTestFlags::RequireNUTActor | EUnitTestFlags::ExpectServerCrash |
             EUnitTestFlags::ExpectDisconnect,
             EMinClientFlags::AcceptActors | EMinClientFlags::SendRPCs |
             EMinClientFlags::NotifyNetActors>();
}

// 测试执行：发送空 FText 到服务器
void UFTextCrash::ExecuteClientUnitTest()
{
    if (UnitNUTActor.IsValid())
    {
        FText BlankText;
        UnitNUTActor->ServerReceiveText(BlankText);  // 触发服务器端崩溃
        SendGenericExploitFailLog();  // 如果漏洞未修复，此消息会被阻断
    }
}

// 日志分析：判断漏洞是否已修复
void UFTextCrash::NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                    const TArray<FString>& InLogLines)
{
    Super::NotifyProcessLog(InProcess, InLogLines);

    if (InProcess.HasSameObject(ServerHandle.Pin().Get()))
    {
        for (auto CurLine : InLogLines)
        {
            if (CurLine.Contains(TEXT("Unhandled Exception: EXCEPTION_ACCESS_VIOLATION")))
            {
                VerificationState = EUnitTestVerification::VerifiedNotFixed;  // 漏洞仍存在
                break;
            }
            else if (CurLine.Contains(GetGenericExploitFailLog()))
            {
                VerificationState = EUnitTestVerification::VerifiedFixed;  // 已修复
                break;
            }
        }
    }
}
```

### 环境设置

模块启动时注册三个游戏环境，为每种游戏配置默认地图和连接参数：

```cpp
// 来源: Private/NUTUnrealEngine.cpp + Public/UnrealEngineEnvironment.h
virtual void StartupModule() override
{
    FNUTModuleInterface::StartupModule();
    FShooterGameEnvironment::Register();  // ShooterGame → 地图 "Sanctuary"
    FQAGameEnvironment::Register();       // QAGame → 地图 "QAEntry"
    FUTEnvironment::Register();           // UnrealTournament → 地图 "DM-DeckTest"
}
```

## Demo 示例

此 plugin 不适合独立使用。它依赖 NetcodeUnitTest 框架来运行测试。

要运行其中的测试用例：

1. 确保 `NetcodeUnitTest` 和 `NUTUnrealEngine` 两个 plugin 都已启用
2. 在编辑器中打开 Session Frontend → Automation 面板
3. 搜索 "NetBitsTest" 或 "FTextCrash" 等测试名称
4. 运行测试，查看输出日志中的验证结果

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统（UCLASS、UPROPERTY 等） |
| `Engine` | 引擎核心（网络连接、Actor、FBitWriter/FBitReader） |
| `NetcodeUnitTest` | 网络单元测试框架（提供 UUnitTest、UClientUnitTest 基类） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-11-06 | `bc63a88d` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 构建系统适配，将旧的编译警告属性迁移到新格式，无功能变更 |
| 2023-11-01 | `e4faf8ba` | Enable truncation warnings in NetcodeUnitTest | 开启截断警告，代码质量改进 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes | 清理冗余的 include 语句，无功能变更 |

### 维护评价

- **创建时间**：2021-03-23（重命名自 UE4 版本，实际测试用例最早可追溯到 2014 年）
- **最近更新**：最近 3 次提交（2023-2024）全部是构建/编译层面的维护，无功能性更新
- **维护状态**：⚠️ **维护不活跃** — 超过 2 年没有实质性功能更新
- **已知限制**：
  - `PacketLimitTest` 和 `PacketLimitTest_Oodle` 已被 `#if 0` 禁用，注释提到"将在游戏级包中恢复"
  - `UTT61_DebugReplicateData` 已移至 `Obsolete` 目录
  - `NetBitsTest` 仍标记为 `bWorkInProgress = true`（自 2016 年起）
  - 仅支持 Win64 和 Linux
- **是否推荐使用**：✅ 适合作为学习 UE 网络测试写法的参考；⚠️ 不建议直接用于生产环境的网络测试（很多测试已禁用或废弃）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine)
- [NetcodeUnitTest 框架文档](../NetcodeUnitTest/index.md)
- 官方文档：无（.uplugin 中 DocsURL 为空）
