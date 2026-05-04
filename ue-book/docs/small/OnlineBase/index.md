# Online Base

> Shared code online subsystem (OSSv1) and online service (OSSv2) interfaces.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | OnlineBase (Runtime) |
| 创建时间 | 2022-01-24 |
| 年龄标签 | 🆕 (约4年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineBase) | |

## 用途

OnlineBase 是 UE 在线子系统（Online Subsystem）架构的**基础设施层**。它不提供具体平台（如 Steam、EOS、Xbox）的实现，而是提供所有在线子系统共享的底层工具：

1. **网络字节序序列化器** (`NboSerializer`)：用于 LAN 发现、UDP 数据包构建等底层网络通信，确保多字节数据在不同端序平台上正确传输
2. **LAN 会话发现** (`LANBeacon` / `FLANSession`)：通过 UDP 广播实现局域网内的服务器发现，供 `OnlineSubsystemNull` 等子系统的 LAN 匹配使用
3. **会话设置名称常量** (`OnlineSessionNames.h`)：定义了跨所有在线子系统通用的 Session Setting 键名（如 `MAPNAME`、`GAMEMODE`）和 Search Setting 键名（如 `DEDICATEDONLY`、`MINSLOTSAVAILABLE`），是整个 OSS 框架的"共享字典"
4. **匹配用 Build ID CVar**：提供 `buildidoverride` 控制台变量，用于覆盖匹配时的 Build ID

简而言之：OnlineBase 解决的问题是"多个在线子系统需要共享但又不属于引擎核心的公共代码放在哪里"。

## 使用场景

- **你在实现自定义 Online Subsystem** → 依赖 OnlineBase 获取 NBO 序列化器、LAN 发现、以及标准的 Session/Search Setting 名称常量
- **你在做局域网多人游戏** → 使用 `FLANSession` 的 Host/Search 机制来发现局域网内的服务器
- **你需要构建自定义 UDP 协议包** → 使用 `FNboSerializeToBuffer` / `FNboSerializeFromBuffer` 进行跨平台的二进制序列化
- **你在使用 `OnlineSubsystemNull` 做本地测试** → 它的 LAN 匹配底层就依赖 OnlineBase 的 LANBeacon

## 蓝图用法

OnlineBase 没有暴露任何 `BlueprintCallable` 函数。它是一个纯 C++ 基础设施模块，不直接面向蓝图使用。

蓝图用户会通过具体的 Online Subsystem（如 `OnlineSubsystemNull`、`OnlineSubsystemSteam`）间接使用 OnlineBase 提供的功能。

## C++ 用法

### 头文件引入

```cpp
// 网络字节序序列化器
#include "Online/NboSerializer.h"

// LAN 发现
#include "Online/LANBeacon.h"

// 会话设置名称常量
#include "Online/OnlineSessionNames.h"

// 基础宏（ONLINE_SUCCESS 等）
#include "Online/OnlineBase.h"
```

### NboSerializer — 网络字节序序列化

`NboSerializer` 提供两个核心类：`FNboSerializeToBuffer`（写入）和 `FNboSerializeFromBuffer`（读取），使用网络字节序（大端序）进行数据序列化，确保跨平台兼容。

```cpp
// === 写入端 ===
// 构造一个 1024 字节的序列化缓冲区
FNboSerializeToBuffer Writer(1024);

// 写入各种类型（自动转换为网络字节序）
Writer << (uint8)1;
Writer << (int32)42;
Writer << (float)3.14f;
Writer << FString(TEXT("Hello"));
Writer << FGuid::NewGuid();
Writer << MyInternetAddr;  // FInternetAddr

// 获取写入的数据和大小
const TArray<uint8>& Data = Writer.GetBuffer();
uint32 NumBytesWritten = Writer.GetByteCount();

// 检查是否溢出
if (Writer.HasOverflow())
{
    // 缓冲区不够大
}

// === 读取端 ===
FNboSerializeFromBuffer Reader(Data.GetData(), NumBytesWritten);

uint8 ByteVal;
int32 IntVal;
float FloatVal;
FString StringVal;
FGuid GuidVal;

Reader >> ByteVal;
Reader >> IntVal;
Reader >> FloatVal;
Reader >> StringVal;
Reader >> GuidVal;

// 检查读取是否溢出
if (Reader.HasOverflow())
{
    // 数据损坏或不完整
}
```

**支持的类型**：`bool`、`char`、`uint8`、`int32`、`uint32`、`uint64`、`float`、`double`、`FString`、`TCHAR*`、`FName`、`FInternetAddr`、`FGuid`。

### LAN 会话发现

`FLANSession` 封装了局域网内服务器发现的完整流程：

```cpp
// === 服务器端（Host） ===
FLANSession LanSession;

// 设置查询回调：当收到客户端的查询包时触发
FOnValidQueryPacketDelegate QueryDelegate;
QueryDelegate.BindLambda([](uint8* Data, int32 DataSize, uint64 ClientNonce)
{
    UE_LOG(LogTemp, Log, TEXT("收到 LAN 查询，Nonce: %llu"), ClientNonce);
    // 在此处理查询，构建响应包
});

LanSession.Host(QueryDelegate);

// === 客户端（Search） ===
FLANSession LanSession;
uint64 ClientNonce = FMath::RandHelper64(INT64_MAX);
LanSession.LanNonce = ClientNonce;

// 构建查询包
FNboSerializeToBuffer QueryPacket(256);
LanSession.CreateClientQueryPacket(QueryPacket, ClientNonce);
// 可以在 QueryPacket 后面追加自定义数据

// 设置响应回调
FOnValidResponsePacketDelegate ResponseDelegate;
ResponseDelegate.BindLambda([](uint8* Data, int32 DataSize)
{
    UE_LOG(LogTemp, Log, TEXT("收到 LAN 服务器响应"));
    // 在此解析服务器信息
});

FOnSearchingTimeoutDelegate TimeoutDelegate;
TimeoutDelegate.BindLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("LAN 搜索超时"));
});

LanSession.Search(QueryPacket, ResponseDelegate, TimeoutDelegate);

// === 每帧 Tick（必须） ===
// FLANSession 需要每帧 Tick 来轮询 socket 和处理超时/重试
LanSession.Tick(DeltaTime);

// === 停止 ===
LanSession.StopLANSession();
```

### 会话设置名称常量

`OnlineSessionNames.h` 定义了全局通用的 `FName` 常量，用于在所有 Online Subsystem 中统一 Session Settings 和 Search Settings 的键名：

```cpp
#include "Online/OnlineSessionNames.h"

// 创建 Session 时使用标准键名
FOnlineSessionSettings Settings;
Settings.Set(SETTING_MAPNAME, FString(TEXT("MyMap")), EOnlineDataAdvertisementType::ViaOnlineService);
Settings.Set(SETTING_GAMEMODE, FString(TEXT("FFA")), EOnlineDataAdvertisementType::ViaOnlineService);
Settings.Set(SETTING_NUMBOTS, 4, EOnlineDataAdvertisementType::ViaOnlineService);
Settings.Set(SETTING_REGION, FString(TEXT("us-east")), EOnlineDataAdvertisementType::ViaOnlineService);

// 搜索 Session 时使用标准搜索键名
TSharedRef<FOnlineSessionSearch> SearchSettings = MakeShared<FOnlineSessionSearch>();
SearchSettings->QuerySettings.Set(SEARCH_DEDICATED_ONLY, true, EOnlineComparisonOp::Equals);
SearchSettings->QuerySettings.Set(SEARCH_MINSLOTSAVAILABLE, 1, EOnlineComparisonOp::GreaterThanEquals);
```

**常用 Session Setting 键名**：

| 常量 | 键名 | 值类型 | 说明 |
|---|---|---|---|
| `SETTING_MAPNAME` | `MAPNAME` | FString | 当前地图名 |
| `SETTING_GAMEMODE` | `GAMEMODE` | FString | 游戏模式 |
| `SETTING_NUMBOTS` | `NUMBOTS` | int32 | 机器人数量 |
| `SETTING_BEACONPORT` | `BEACONPORT` | int32 | Beacon 主机端口 |
| `SETTING_QOS` | `QOS` | int32 | QoS Beacon 响应开关 |
| `SETTING_REGION` | `REGION` | FString | 区域标识 |
| `SETTING_SESSIONKEY` | `SESSIONKEY` | FString | 会话密钥 |
| `SETTING_HOST_MIGRATION` | `HOSTMIGRATION` | — | 主机迁移开关 |
| `SETTING_MAXSPECTATORS` | `MAXSPECTATORS` | int32 | 观战席位数 |

**常用 Search Setting 键名**：

| 常量 | 键名 | 值类型 | 说明 |
|---|---|---|---|
| `SEARCH_DEDICATED_ONLY` | `DEDICATEDONLY` | bool | 仅搜索专用服务器 |
| `SEARCH_EMPTY_SERVERS_ONLY` | `EMPTYONLY` | bool | 仅搜索空服务器 |
| `SEARCH_NONEMPTY_SERVERS_ONLY` | `NONEMPTYONLY` | bool | 仅搜索非空服务器 |
| `SEARCH_MINSLOTSAVAILABLE` | `MINSLOTSAVAILABLE` | int | 最少可用槽位 |
| `SEARCH_MATCHMAKING_QUEUE` | `MATCHMAKINGQUEUE` | FString | 匹配队列名 |

### Build ID 覆盖

通过控制台变量覆盖匹配用的 Build ID（主要用于开发测试）：

```cpp
// 在控制台中设置
// buildidoverride 12345

// 在代码中获取
#include "Online/OnlineBase.h"

TAutoConsoleVariable<int32>& BuildIdCVar = GetBuildIdOverrideCVar();
int32 CurrentBuildId = BuildIdCVar.GetValueOnGameThread();
```

## Demo 示例

以下示例展示如何使用 `FLANSession` 和 `NboSerializer` 实现一个简单的 LAN 服务器发现：

```cpp
// MyLANDiscovery.h
#pragma once

#include "Online/LANBeacon.h"
#include "Online/NboSerializer.h"

class FMyLANDiscovery
{
public:
    /** 作为服务器启动 LAN 广播 */
    void StartHosting()
    {
        FOnValidQueryPacketDelegate QueryDelegate;
        QueryDelegate.BindRaw(this, &FMyLANDiscovery::OnQueryReceived);
        LanSession.Host(QueryDelegate);
        UE_LOG(LogTemp, Log, TEXT("LAN 服务器已启动，等待查询..."));
    }

    /** 作为客户端搜索 LAN 服务器 */
    void StartSearching()
    {
        uint64 Nonce = FMath::RandHelper64(INT64_MAX);
        LanSession.LanNonce = Nonce;

        // 构建查询包（仅包含头部，无自定义 payload）
        FNboSerializeToBuffer QueryPacket(LAN_BEACON_PACKET_HEADER_SIZE);
        LanSession.CreateClientQueryPacket(QueryPacket, Nonce);

        FOnValidResponsePacketDelegate ResponseDelegate;
        ResponseDelegate.BindRaw(this, &FMyLANDiscovery::OnResponseReceived);

        FOnSearchingTimeoutDelegate TimeoutDelegate;
        TimeoutDelegate.BindRaw(this, &FMyLANDiscovery::OnSearchTimeout);

        LanSession.Search(QueryPacket, ResponseDelegate, TimeoutDelegate);
    }

    /** 每帧调用 */
    void Tick(float DeltaTime)
    {
        LanSession.Tick(DeltaTime);
    }

    void Stop()
    {
        LanSession.StopLANSession();
    }

private:
    FLANSession LanSession;

    void OnQueryReceived(uint8* Data, int32 DataSize, uint64 ClientNonce)
    {
        UE_LOG(LogTemp, Log, TEXT("收到查询，构建响应..."));

        // 构建响应包
        FNboSerializeToBuffer ResponsePacket(LAN_BEACON_MAX_PACKET_SIZE);
        LanSession.CreateHostResponsePacket(ResponsePacket, ClientNonce);

        // 追加自定义服务器信息（如服务器名、当前人数等）
        FString ServerName = TEXT("My Awesome Server");
        int32 CurrentPlayers = 3;
        int32 MaxPlayers = 8;

        ResponsePacket << ServerName;
        ResponsePacket << CurrentPlayers;
        ResponsePacket << MaxPlayers;

        // 广播响应
        LanSession.BroadcastPacket(ResponsePacket, ResponsePacket.GetByteCount());
    }

    void OnResponseReceived(uint8* Data, int32 DataSize)
    {
        // 解析服务器响应
        FNboSerializeFromBuffer Reader(Data, DataSize);

        FString ServerName;
        int32 CurrentPlayers;
        int32 MaxPlayers;

        Reader >> ServerName;
        Reader >> CurrentPlayers;
        Reader >> MaxPlayers;

        UE_LOG(LogTemp, Log, TEXT("发现服务器: %s (%d/%d)"),
            *ServerName, CurrentPlayers, MaxPlayers);
    }

    void OnSearchTimeout()
    {
        UE_LOG(LogTemp, Log, TEXT("LAN 搜索超时，未发现更多服务器"));
    }
};
```

## 模块依赖

从 `OnlineBase.Build.cs` 提取：

| 模块 | 依赖类型 | 用途 |
|---|---|---|
| `Sockets` | Public | Socket API，LANBeacon 的 UDP 广播依赖 |
| `Core` | Private | 引擎核心（容器、字符串、日志等） |
| `CoreUObject` | Private | UObject 系统 |

> **注意**：OnlineBase 明确**不依赖 Engine**（代码中有注释 `// NOTE: OnlineBase cannot depend on Engine!`），这使得它可以在 Engine 加载前被其他模块使用。

如果你的模块要使用 OnlineBase 提供的功能，在 `Build.cs` 中添加：

```cpp
PublicDependencyModuleNames.Add("OnlineBase");
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-21 | `3b7a381e` | Removal of online code marked for deprecation in 5.5 | 移除了 5.5 版本标记为废弃的代码，属于正常的版本清理 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage | 构建系统调整：将 DLL 导出标记从类型级改为方法/静态变量级，属于编译基础设施优化 |
| 2025-02-17 | `c9d5cef7` | [Backout] - Add OnlineInit dependency resolver to the OnlineBase Plugin | 回退了一个尝试在 OnlineBase 中添加 OnlineInit 依赖解析器的改动，说明 Epic 曾考虑扩展此模块但最终撤回 |

### 维护评价

- **创建时间**：2022 年 1 月（约 4 年历史）
- **维护状态**：**维护中** — 2025 年仍有代码变更（废弃代码清理、构建系统调整）
- **稳定性**：这是一个非常稳定的基础设施模块，代码量小且功能成熟，更新主要来自周围框架的变更（如废弃清理、编译标记调整），而非自身功能变化
- **已知限制**：
  - 不支持动态重载（`SupportsDynamicReloading() = false`）
  - `GenerateNonce()` 使用 `FMath::Rand()` 而非密码学安全随机数（代码中有 TODO 注释希望改用 `CryptGenRandom`）
  - LAN 发现基于 UDP 广播，仅限局域网使用
- **推荐使用**：✅ 作为在线子系统的基础依赖，它是必选的。如果你在开发自定义 Online Subsystem 或需要 LAN 发现功能，直接依赖即可。普通游戏开发者通常不需要直接引用此模块——它会被具体平台的 Online Subsystem 自动拉入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineBase)
- [OnlineSubsystem 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/online-subsystem-in-unreal-engine)
