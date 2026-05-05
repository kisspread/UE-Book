# Storm Sync Motion Design Bridge

> Plugin bridge between Motion Design Plugin and Storm Sync to provide in-editor integration to synchronize assets

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | true |
| 包含内容 | true |
| 模块 | StormSyncAvaBridge (Runtime), StormSyncAvaBridgeEditor (Editor) |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge) | |

## 用途

StormSyncAvalancheBridge 是 Motion Design（原 Avalanche）与 StormSync 之间的桥接层，解决的核心问题是：**在虚拟制片流水线中，如何让编辑器中的 Motion Design 资产自动同步到远程播放服务器**。

具体来说，这个 plugin 做了三件事：

1. **地址发现桥接**：将 StormSync 传输层的消息总线地址（Server / Client / Discovery）注册到 Avalanche Playback Server/Client 的 UserData 中，使得远程节点可以自动发现彼此的 StormSync 端点，无需手动配置。

2. **IAvaMediaSyncProvider 实现**：通过 Unreal 的 Modular Feature 机制，提供 `FStormSyncAvaSyncProvider`，将 Motion Design 的资产同步接口（Push / Pull / Compare / SyncToAll）代理到 StormSync 传输层。

3. **Rundown 编辑器 UI 扩展**：在 Motion Design Rundown 编辑器的上下文菜单和工具栏中注入同步操作，让用户可以直接从 Rundown 界面推送、对比资产到远程播放服务器。

## 使用场景

- 你在使用 Motion Design（虚拟制片/广播图形）制作播出内容，需要将 Rundown 中引用的资产同步到远程渲染农场的播放服务器 → 启用此 plugin
- 你有多台机器运行 Avalanche Playback Server，需要自动发现和同步 StormSync 端点地址 → 此 plugin 自动处理
- 你在 Rundown 编辑器中选中了模板页面，想一键将对应的 Motion Design 资产推送到特定远程 → 使用 Rundown 编辑器中新增的 "Synchronize Actions" 菜单

## 蓝图用法

此 plugin **不暴露任何 BlueprintCallable 函数**。它完全在 C++ 层面工作，通过 Modular Feature 注册和编辑器 UI 扩展提供功能。所有交互通过 Motion Design Rundown 编辑器的 UI 进行。

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncAvaBridgeUtils.h"
#include "StormSyncAvaBridgeCommon.h"
```

### 基本用法 — 获取通道的远程服务器名称

`FStormSyncAvaBridgeUtils` 提供了一个静态工具方法，用于查询指定广播通道（Channel）关联的远程播放服务器名称。

```cpp
// 获取指定通道关联的远程 Playback Server 名称列表
// 来源: Source/StormSyncAvaBridge/Public/StormSyncAvaBridgeUtils.h
TArray<FString> ServerNames = FStormSyncAvaBridgeUtils::GetServerNamesForChannel(TEXT("ChannelA"));

for (const FString& ServerName : ServerNames)
{
    UE_LOG(LogTemp, Display, TEXT("Remote server: %s"), *ServerName);
}
```

该方法内部通过 `UAvaBroadcast::GetBroadcast()` 获取当前广播 Profile，遍历指定通道的 Media Output，筛选出远程（`IsRemote()`）输出并返回对应的服务器名称。

### 进阶用法 — 通过 UserData 地址进行手动同步

当 StormSync 服务器启动后，Bridge 会自动将以下地址键注册到 Playback Server/Client 的 UserData 中：

```cpp
// 来源: Source/StormSyncAvaBridge/Public/StormSyncAvaBridgeCommon.h
namespace UE::StormSync::AvaBridgeCommon
{
    // StormSync 服务端端点地址
    static constexpr const TCHAR* StormSyncServerAddressKey = TEXT("StormSyncServerAddress");
    // StormSync 客户端端点地址
    static constexpr const TCHAR* StormSyncClientAddressKey = TEXT("StormSyncClientAddress");
    // StormSync 发现管理器地址
    static constexpr const TCHAR* StormSyncDiscoveryAddressKey = TEXT("StormSyncDiscoveryAddress");
}
```

你可以通过 Playback Client 读取远程服务器的这些 UserData，从而获取远程 StormSync 端点的消息总线地址：

```cpp
// 来源: Source/StormSyncAvaBridge/Private/StormSyncAvaBridge.cpp (Console Command 实现逻辑)
if (IAvaMediaModule::Get().IsPlaybackClientStarted())
{
    const IAvaPlaybackClient& PlaybackClient = IAvaMediaModule::Get().GetPlaybackClient();

    // 获取远程服务器 "MyServer" 上注册的 StormSync Client 地址
    FString AddressId = PlaybackClient.GetServerUserData(
        TEXT("MyServer"),
        UE::StormSync::AvaBridgeCommon::StormSyncClientAddressKey
    );

    // 解析为 FMessageAddress 用于后续操作
    FMessageAddress RemoteAddress;
    if (FMessageAddress::Parse(AddressId, RemoteAddress))
    {
        // 可以用此地址发起 Push/Pull/Compare 等 StormSync 传输操作
    }
}
```

### 进阶用法 — Modular Feature 同步接口

`FStormSyncAvaSyncProvider` 实现了 `IAvaMediaSyncProvider` 接口，通过 Modular Feature 注册。如果你的代码需要以 provider-agnostic 的方式进行资产同步，可以直接使用该接口：

```cpp
// 通过 Modular Features 获取已注册的 sync provider
IModularFeatures& ModularFeatures = IModularFeatures::Get();
const FName FeatureName = IAvaMediaSyncProvider::GetModularFeatureName();

if (ModularFeatures.IsModularFeatureAvailable(FeatureName))
{
    IAvaMediaSyncProvider& SyncProvider = static_cast<IAvaMediaSyncProvider&>(
        ModularFeatures.GetModularFeature(FeatureName)
    );

    // 同步指定包到所有已知远端
    TArray<FName> Packages = { TEXT("/Game/MotionDesign/MyAsset") };
    SyncProvider.SyncToAll(Packages);

    // 推送到指定远端（异步，通过回调返回结果）
    SyncProvider.PushToRemote(TEXT("RemoteServer"), Packages,
        FOnAvaMediaSyncResponse::CreateLambda([](TSharedPtr<FAvaMediaSyncResponse> Response)
        {
            if (Response.IsValid() && Response->Status == EAvaMediaSyncResponseResult::Success)
            {
                UE_LOG(LogTemp, Display, TEXT("Push succeeded"));
            }
        })
    );
}
```

## Console Commands

此 plugin 注册了一个调试用的控制台命令：

| 命令 | 说明 |
|---|---|
| `StormSyncAvaBridge.Debug.GetUserData <ChannelName> <Key>` | 查询指定通道关联的远程播放服务器上指定 Key 的 UserData 值 |

示例：
```
StormSyncAvaBridge.Debug.GetUserData ChannelA StormSyncClientAddress
```

## Demo 示例

此 plugin 没有独立的可编译最小示例——它是作为 Motion Design + StormSync 生态系统的集成胶水层存在的。要使用它：

1. 启用 Motion Design (Avalanche) plugin
2. 启用 StormSync plugin
3. 启用此 StormSyncAvalancheBridge plugin
4. 在 Motion Design Rundown 编辑器中，选中引用了 Motion Design 资产的模板页面
5. 右键上下文菜单中会出现 "Synchronize Actions" 部分，包含 Initialize、Push、Compare 操作

## 模块依赖

### StormSyncAvaBridge (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `AvalancheMedia` | Motion Design 播放媒体框架（Private） |
| `CoreUObject` | UObject 系统（Private） |
| `Engine` | 引擎核心（Private） |
| `Slate` / `SlateCore` | UI 框架（Private） |
| `StormSyncCore` | StormSync 核心功能和委托（Private） |
| `StormSyncTransportCore` | StormSync 传输层核心类型（Private） |
| `StormSyncTransportServer` | StormSync 服务端模块接口（Private） |
| `StormSyncTransportClient` | StormSync 客户端模块接口（Private） |

### StormSyncAvaBridgeEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `AvalancheMedia` | Motion Design 播放媒体框架（Private） |
| `AvalancheMediaEditor` | Motion Design 编辑器集成（Private） |
| `CoreUObject` | UObject 系统（Private） |
| `EditorFramework` | 编辑器框架（Private） |
| `Engine` | 引擎核心（Private） |
| `Slate` / `SlateCore` | UI 框架（Private） |
| `StormSyncAvaBridge` | 本 plugin 的 Runtime 模块（Private） |
| `StormSyncCore` | StormSync 核心功能（Private） |
| `StormSyncEditor` | StormSync 编辑器模块，提供 UI 构建方法（Private） |
| `StormSyncTransportCore` | StormSync 传输层核心类型（Private） |
| `StormSyncTransportClient` | StormSync 客户端模块（Private） |
| `StormSyncTransportServer` | StormSync 服务端模块（Private） |

### Plugin 依赖

| Plugin | 说明 |
|---|---|
| `Avalanche` | Motion Design 主 plugin，提供 Rundown、Broadcast、Playback 等基础设施 |
| `StormSync` | 资产同步 plugin，提供传输层、包描述符、状态管理等核心功能 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `df329aa21f92` | **移除 beta 标签** — Motion Design 系列 plugin 正式脱离 beta 状态 |
| 2025-05-08 | `bdd7ab5baf1a` | **标记为 beta** — 从 Experimental 迁移到 VirtualProduction 后标记为 beta |
| 2025-05-08 | `d53ec51b85c0` | **从 Experimental 迁移到 VirtualProduction** — 与其他 Motion Design 系列 plugin（ActorModifier、ClonerEffector 等）一起迁移到正式分类 |

**解读**：三次 commit 都是分类/标签变更，没有功能性代码改动。2025-05 完成了从 Experimental 到 VirtualProduction 的迁移，2025-09 正式去掉 beta 标签。

### 维护评价

- **创建时间**：2024-01-30（首次出现在 Experimental 目录），约 2 年历史
- **当前状态**：已从 Experimental 毕业为 VirtualProduction 正式插件，beta 标签已移除
- **活跃度**：近期更新均为元数据变更（分类迁移、beta 标签管理），无功能性代码更新。这说明功能已经稳定
- **代码质量**：代码结构清晰，模块分层合理（Runtime/Editor），日志充分，错误处理完善
- **测试覆盖**：未发现自动化测试文件
- **风险**：Runtime 模块在 TargetDenyList 中排除了 Server 目标，说明此功能仅适用于客户端/编辑器场景
- **推荐**：✅ 推荐使用。如果你在虚拟制片流水线中使用 Motion Design + StormSync，这是必不可少的集成插件。作为 Epic 官方维护的桥接层，它已被正式标记为非 beta 状态

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge)
- [StormSync plugin 文档](../StormSync/index.md)（资产同步核心功能）
- [Motion Design (Avalanche) plugin 文档](../Avalanche/index.md)（广播图形系统）
