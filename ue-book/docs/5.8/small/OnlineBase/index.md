# Online Base

> Shared code online subsystem (OSSv1) and online service (OSSv2) interfaces.

| 属性 | 值 |
|---|---|
| 中文名 | 在线基础 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineBase` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-24 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineBase) | |

## 用途

这个插件是虚幻引擎在线功能的**底层基础模块**。它不直接实现具体的在线平台（如 Steam、PlayStation Network）功能，而是提供一套共享的、基础的接口定义和工具，被所有具体的在线子系统（OSSv1）和在线服务（OSSv2）模块所依赖。

其核心价值在于：
1.  **代码复用与统一**：将通用的网络功能（如 LAN 会话发现）和数据结构（如会话设置键名常量）集中管理，避免不同在线模块间的重复代码。
2.  **架构桥接**：为新（OSSv2）旧（OSSv1）两代在线系统架构提供共享的基础层，促进其平稳过渡和共存。
3.  **底层工具支持**：提供网络字节序序列化等基础工具，确保跨平台网络通信的数据一致性。

## 使用场景

-   **开发多人游戏的局域网联机功能**：直接使用 `FLANSession` 类来实现基于 UDP 广播的服务器发现和加入。
-   **需要高效、跨平台的网络数据打包**：使用 `FNboSerializeToBuffer` 和 `FNboSerializeFromBuffer` 将游戏数据（如玩家信息、游戏设置）序列化为标准的网络字节序，用于网络发送和接收。
-   **统一不同在线后端的会话设置键名**：在代码中使用 `OnlineSessionNames.h` 中定义的宏（如 `SETTING_MAPNAME`、`SEARCH_DEDICATED_ONLY`）作为字典键，确保与特定在线子系统（如 Steam、EOS）交互时使用一致的键名。
-   **作为自定义在线子系统开发的起点**：当需要为一个新的在线平台开发 `IOnlineSubsystem` 或 `IOnlineServices` 接口实现时，此插件提供了最基础的依赖和共享代码。

## 蓝图用法

`OnlineBase` 插件主要提供底层的 C++ 接口和工具，其核心类（如 `FLANSession`、`FNboSerializeToBuffer`）通常不直接暴露为蓝图节点。蓝图层面更常用的功能（如会话创建、搜索）由上层的 `OnlineSubsystem` 或 `OnlineServices` 插件提供，并通过 `UOnlineSessionSubsystem` 等对象暴露。

此插件为那些在线功能蓝图节点提供了底层的 C++ 实现支持。

## C++ 用法

### 头文件引入

```cpp
#include "Online/LANBeacon.h"
#include "Online/NboSerializer.h"
#include "Online/OnlineSessionNames.h"
```

### 基本用法

**1. 使用 LAN 会话进行局域网发现 (来自 LANBeacon.h)**

```cpp
// 源码示例：创建一个LAN会话用于主机广播
FLANSession LANSession;
FOnValidQueryPacketDelegate QueryDelegate;
// 绑定一个lambda来处理客户端查询包
QueryDelegate.BindLambda([](uint8* Packet, int32 Length, uint64 ClientNonce) {
    // 这里应该解析查询并发送响应
});

// 启动LAN会话，开始监听查询
LANSession.Host(QueryDelegate);

// 在游戏循环中更新LAN会话状态
void AMyGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    LANSession.Tick(DeltaSeconds);
}

// 源码示例：创建一个LAN搜索请求
FLANSession LANSession;
FNboSerializeToBuffer QueryPacket(1024);
FOnValidResponsePacketDelegate ResponseDelegate;
FOnSearchingTimeoutDelegate TimeoutDelegate;

// 绑定委托处理服务器响应和超时
ResponseDelegate.BindLambda([](uint8* Packet, int32 Length) {
    // 处理服务器响应，解析服务器信息
});
TimeoutDelegate.BindLambda([]() {
    // 搜索超时处理
});

// 构造查询包内容（例如添加游戏版本信息）
QueryPacket << (uint32)MY_GAME_VERSION;
// 启动LAN搜索
LANSession.Search(QueryPacket, ResponseDelegate, TimeoutDelegate);
```

**2. 网络字节序序列化 (来自 NboSerializer.h)**

```cpp
// 源码示例：将数据打包成网络字节序
FNboSerializeToBuffer SenderBuffer(256);
FString PlayerName = TEXT("TestPlayer");
int32 Score = 1000;

// 将数据写入缓冲区，自动转换为大端字节序
SenderBuffer << PlayerName;
SenderBuffer << Score;

// 获取打包后的原始数据指针和长度，用于网络发送
uint8* DataPtr = (uint8*)SenderBuffer;
uint32 DataLen = SenderBuffer.GetByteCount();

// 源码示例：从网络字节序数据中解析
FNboSerializeFromBuffer ReceiverBuffer(DataPtr, DataLen);
FString ReceivedName;
int32 ReceivedScore;

// 从缓冲区读取数据，自动从大端字节序转换
ReceiverBuffer >> ReceivedName;
ReceiverBuffer >> ReceivedScore;
```

**3. 使用通用会话设置常量 (来自 OnlineSessionNames.h)**

```cpp
// 源码示例：在创建或搜索会话时使用定义好的常量键名
FOnlineSessionSettings Settings;
// 使用宏定义的键名，避免字符串拼写错误
Settings.Set(SETTING_MAPNAME, TEXT("GameMap01"), EOnlineDataAdvertisementType::ViaOnlineService);
Settings.Set(SETTING_GAMEMODE, TEXT("TeamDeathmatch"), EOnlineDataAdvertisementType::ViaOnlineService);
Settings.Set(SETTING_NUMBOTS, 2, EOnlineDataAdvertisementType::ViaOnlineService);
Settings.Set(SETTING_REGION, TEXT("Asia"), EOnlineDataAdvertisementType::ViaOnlineServiceAndPing);

// 搜索时使用搜索过滤键
FOnlineSessionSearch SearchSettings;
SearchSettings.QuerySettings.Set(SEARCH_DEDICATED_ONLY, true, EOnlineComparisonOp::Equals);
SearchSettings.QuerySettings.Set(SEARCH_MINSLOTSAVAILABLE, 4, EOnlineComparisonOp::GreaterThanEquals);
```

### 进阶用法

将 LAN 会话与序列化结合，实现自定义的局域网广播数据格式。

```cpp
// 在主机查询响应中，打包更丰富的游戏信息
void AMyGameMode::OnClientQuery(uint8* Packet, int32 Length, uint64 ClientNonce)
{
    FNboSerializeToBuffer ResponsePacket(1024);
    
    // 先创建标准的LAN响应包头
    LANSession.CreateHostResponsePacket(ResponsePacket, ClientNonce);
    
    // 附加自定义的游戏状态数据
    FString MapName = GetWorld()->GetMapName();
    int32 CurrentPlayers = GameState->PlayerArray.Num();
    int32 MaxPlayers = MaxPlayersAllowed;
    ResponsePacket << MapName;
    ResponsePacket << CurrentPlayers;
    ResponsePacket << MaxPlayers;
    
    // 广播响应
    LANSession.BroadcastPacket((uint8*)ResponsePacket, ResponsePacket.GetByteCount());
}
```

## Demo 示例

一个最小的 LAN 主机和客户端示例，演示 `OnlineBase` 的基础用法。

**MyLANGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Online/LANBeacon.h"
#include "MyLANGameMode.generated.h"

UCLASS()
class AMyLANGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AMyLANGameMode();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void Tick(float DeltaSeconds) override;

private:
	/** LAN会话管理器 */
	FLANSession LANSession;

	/** 处理客户端查询的委托 */
	void OnClientQueryReceived(uint8* Packet, int32 Length, uint64 ClientNonce);
};
```

**MyLANGameMode.cpp**
```cpp
#include "MyLANGameMode.h"
#include "Online/NboSerializeToBuffer.h"
#include "Online/OnlineSessionNames.h"

AMyLANGameMode::AMyLANGameMode()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMyLANGameMode::BeginPlay()
{
	Super::BeginPlay();

	// 创建查询委托并绑定处理函数
	FOnValidQueryPacketDelegate QueryDelegate;
	QueryDelegate.BindUObject(this, &AMyLANGameMode::OnClientQueryReceived);

	// 启动LAN会话，开始广播主机存在
	LANSession.Host(QueryDelegate);
}

void AMyLANGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	// 停止LAN会话
	LANSession.StopLANSession();
	Super::EndPlay(EndPlayReason);
}

void AMyLANGameMode::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	// 必须每帧更新LAN会话以处理传入的数据包
	LANSession.Tick(DeltaSeconds);
}

void AMyLANGameMode::OnClientQueryReceived(uint8* Packet, int32 Length, uint64 ClientNonce)
{
	UE_LOG(LogTemp, Log, TEXT("收到客户端查询，ClientNonce: %llu"), ClientNonce);

	// 构建响应包
	FNboSerializeToBuffer ResponsePacket(512);
	// 先构建标准的LAN响应头
	LANSession.CreateHostResponsePacket(ResponsePacket, ClientNonce);

	// 添加自定义的服务器信息
	FString ServerName = TEXT("My Awesome Server");
	int32 CurrentPlayerCount = 1;
	int32 MaxPlayerCount = 8;
	ResponsePacket << ServerName;
	ResponsePacket << CurrentPlayerCount;
	ResponsePacket << MaxPlayerCount;

	// 广播响应
	LANSession.BroadcastPacket((uint8*)ResponsePacket, ResponsePacket.GetByteCount());
	UE_LOG(LogTemp, Log, TEXT("已广播服务器响应"));
}
```

**MyLANPlayerController.h (客户端示例片段)**
```cpp
// 在客户端控制器中启动搜索
void AMyLANPlayerController::FindLANServers()
{
	FLANSession LANSearchSession;
	FNboSerializeToBuffer QueryPacket(256);
	FOnValidResponsePacketDelegate ResponseDelegate;
	FOnSearchingTimeoutDelegate TimeoutDelegate;

	ResponseDelegate.BindUObject(this, &AMyLANPlayerController::OnServerFound);
	TimeoutDelegate.BindUObject(this, &AMyLANPlayerController::OnSearchTimeout);

	// 发起搜索
	LANSearchSession.Search(QueryPacket, ResponseDelegate, TimeoutDelegate);
	UE_LOG(LogTemp, Log, TEXT("开始局域网服务器搜索..."));
}

void AMyLANPlayerController::OnServerFound(uint8* Packet, int32 Length)
{
	FNboSerializeFromBuffer ReceiverPacket(Packet, Length);
	FString ServerName;
	int32 CurrentPlayers, MaxPlayers;
	ReceiverPacket >> ServerName;
	ReceiverPacket >> CurrentPlayers;
	ReceiverPacket >> MaxPlayers;

	UE_LOG(LogTemp, Log, TEXT("发现服务器: %s, 玩家: %d/%d"), *ServerName, CurrentPlayers, MaxPlayers);
	// 在这里可以将服务器添加到UI列表中
}
```

## 模块依赖

`OnlineBase` 模块本身依赖较少，主要作为被依赖方。

无特殊依赖（仅标准 Core/Engine/Sockets 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 `UE_LOGF` 格式。 |
| 2026-03-26 | `03bb7402` | UE: Fix OSS Null not finding multiple LAN sessions from a single host. | 修复了 OSS Null 无法从同一主机找到多个 LAN 会话的问题。 |
| 2025-05-21 | `3b7a381e` | Removal of online code marked for deprecation in 5.5 | 清理了在 5.5 版本中被标记为弃用的在线相关代码。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为所有文件中的方法和静态变量添加了 DLL 导出声明 (`dllexport`)。 |
| 2025-02-17 | `c9d5cef7` | [Backout] - CL39884527 | 回滚了之前的某次提交。 |

### 维护评价

**活跃维护中**。
`OnlineBase` 插件创建于 2022 年初，相对较新。从 Git 历史看，它持续接受更新，包括功能修复（如多 LAN 会话发现）、代码现代化（日志宏迁移）、兼容性改进（DLL 导出）以及技术债务清理（移除弃用代码）。最后一次更新发生在 2026 年 4 月，表明该插件仍在被积极维护和调整，是虚幻引擎在线基础设施中一个稳定且必要的组成部分。

**推荐使用**。作为在线子系统的共享基础层，任何涉及网络多人功能的项目都会隐式依赖此插件。对于需要直接操作 LAN 功能或进行底层网络数据处理的开发者，它提供了必需的工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineBase)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (可在该目录下搜索与 Online 或 LAN 相关的测试)