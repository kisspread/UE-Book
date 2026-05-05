# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一套完整的远程控制解决方案，其核心目的是允许用户通过标准的网络协议（HTTP 和 WebSocket）从外部应用程序或网页服务来控制 Unreal Engine 的运行时或编辑器状态。它不仅仅是一个简单的 Web 服务器，而是一个功能丰富的框架，用于暴露引擎的内部属性、函数和对象，使得自动化、远程监控、虚拟制片控制面板集成等场景成为可能。该插件是 Epic 虚拟制作工具链的关键组成部分。

## 使用场景

- **虚拟制片 (Virtual Production)**：在片场，灯光师或导演可以通过平板电脑上的自定义网页界面，实时调整场景中灯光、材质或摄像机的参数，无需直接操作运行 Unreal 的工作站。
- **自动化测试与部署**：在持续集成/持续部署 (CI/CD) 流程中，通过脚本发送 HTTP 请求来触发引擎内的测试、截图或数据导出。
- **自定义控制面板**：为特定项目（如建筑可视化、产品配置器）开发独立的控制软件，通过 WebSocket 与引擎进行低延迟的双向通信。
- **多用户协作**：在多人协作编辑或评审场景下，同步不同客户端对场景的修改（通过 `RemoteControlMultiUser` 模块）。
- **第三方软件集成**：将 Unreal Engine 的实时渲染能力作为后端，集成到 DCC 工具、媒体服务器或其他专业软件中。

## 蓝图用法

该插件主要通过 C++ API 和 Web API 进行交互，蓝图直接暴露的节点相对较少，主要集中在 `RemoteControlAPI` 模块中，用于在蓝图中查询和操作远程控制预设。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Remote Control Preset` | 根据预设名称获取一个远程控制预设对象。 | `URemoteControlAPI` |
| `Get All Remote Control Presets` | 获取当前世界中所有可用的远程控制预设。 | `URemoteControlAPI` |
| `Get Exposed Entities` | 获取指定预设中所有已暴露的实体（属性、函数等）。 | `URemoteControlPreset` |
| `Set Entity Value` | 通过蓝图设置一个已暴露属性的值。 | `URemoteControlPreset` |

### 使用示例（蓝图描述）

1.  在蓝图中，使用 `Get Remote Control Preset` 节点，并传入预设名称（如 “MyLightingPreset”）来获取预设对象。
2.  将获取到的预设对象连接到 `Get Exposed Entities` 节点，以获取一个实体列表。
3.  遍历列表，找到代表某个灯光强度的实体。
4.  使用 `Set Entity Value` 节点，传入该实体和一个新的浮点数值，即可远程修改灯光强度。

## C++ 用法

核心用法是通过 `RemoteControlAPI` 模块在 C++ 中创建和管理远程控制预设，并将引擎对象暴露给 Web 接口。

### 头文件引入

```cpp
#include "RemoteControlAPI.h"
#include "RemoteControlPreset.h"
#include "RemoteControlExposeRegistry.h"
```

### 基本用法

以下代码演示如何在 C++ 中获取一个远程控制预设并暴露一个 Actor 的属性。
*(来源: 引擎测试用例及模块公共头文件)*

```cpp
// 获取 RemoteControlAPI 子系统
URemoteControlAPI* RemoteControlAPI = URemoteControlAPI::Get(GetWorld());
if (RemoteControlAPI)
{
    // 获取或创建一个名为 “MyPreset” 的预设
    URemoteControlPreset* Preset = RemoteControlAPI->GetOrCreatePreset(TEXT("MyPreset"));
    if (Preset)
    {
        // 假设我们有一个指向 AActor 的指针 MyActor
        AActor* MyActor = ...;
        // 暴露该 Actor 的 “ActorLocation” 属性，并给它一个别名 “ActorPosition”
        FRemoteControlPresetExposeArgs Args;
        Args.Label = TEXT("ActorPosition");
        Preset->ExposeProperty(MyActor, GET_MEMBER_NAME_CHECKED(AActor, ActorLocation), Args);
        
        // 暴露该 Actor 的一个自定义函数
        Preset->ExposeFunction(MyActor, GET_FUNCTION_NAME_CHECKED(AActor, CustomFunction));
    }
}
```

### 进阶用法

结合 `RemoteControlMultiUser` 模块，在多用户会话中同步远程控制操作。
*(来源: RemoteControlMultiUser 模块逻辑推断)*

```cpp
// 在多用户会话中，当本地用户通过 Web API 修改了一个暴露的属性时，
// RemoteControlMultiUser 模块会负责将这个变更（Transaction）广播给会话中的其他客户端。
// 开发者通常不需要直接调用此模块的 API，它作为底层同步机制自动工作。
// 但可以监听相关事件来定制同步行为，例如过滤某些属性的同步。
```

## Demo 示例

一个最小的 C++ 示例，展示如何在游戏模式中初始化并暴露一个属性。

**MyGameMode.h**
```cpp
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class URemoteControlPreset;

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    virtual void StartPlay() override;

private:
    UPROPERTY()
    TObjectPtr<URemoteControlPreset> MyPreset;
};
```

**MyGameMode.cpp**
```cpp
#include "MyGameMode.h"
#include "RemoteControlAPI.h"
#include "RemoteControlPreset.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();

    // 获取 RemoteControl API
    URemoteControlAPI* RCAPI = URemoteControlAPI::Get(GetWorld());
    if (RCAPI)
    {
        // 创建一个预设
        MyPreset = RCAPI->GetOrCreatePreset(TEXT("GameModePreset"));
        if (MyPreset)
        {
            // 暴露当前 GameMode 的 “bUseSeamlessTravel” 属性
            FRemoteControlPresetExposeArgs Args;
            Args.Label = TEXT("SeamlessTravel");
            MyPreset->ExposeProperty(this, GET_MEMBER_NAME_CHECKED(AGameModeBase, bUseSeamlessTravel), Args);
            
            UE_LOG(LogTemp, Log, TEXT("Remote Control Preset 'GameModePreset' created and property exposed."));
        }
    }
}
```

## 模块依赖

该插件由多个模块组成，模块间存在依赖关系。使用者通常只需要依赖 `RemoteControlAPI` 模块。

| 模块 | 用途 |
|---|---|
| `RemoteControlAPI` | 核心 API 模块，提供创建和管理预设、暴露实体的接口。 |
| `WebRemoteControl` | 实现 HTTP/WebSocket 服务器，处理来自外部的请求。 |
| `RemoteControlProtocol` | 定义远程控制协议和消息格式。 |
| `RemoteControlLogic` | 包含远程控制的核心逻辑，如实体解析和值设置。 |
| `RemoteControlMultiUser` | 与 Unreal 的多用户编辑框架（Concert）集成，同步远程控制操作。 |
| `RemoteControlCommon` | 公共数据类型和工具函数。 |
| `RemoteControlUI` | 编辑器内的远程控制管理 UI。 |
| `RemoteControlProtocolWidgets` | 为特定协议（如 OSC）提供编辑器控件。 |

## 维护状态

### 近期更新

```
- 6f6faa161371 Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactionFilterDelegate with new FOnFilterTransactionDelegate, which also passes const FTransactionObjectEvent& along. This allows subscribers to filter out changes based on properties changed.
- 177057a80010 [Backout] - CL34028050 [FYI] Dominik.Peacock Original CL Desc ----------------------------------------------------------------- Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactionFilterDelegate with new FOnFilterTransactionDelegate, which also passes const FTransactionObjectEvent& along. This allows subscribers to filter out changes based on properties changed.
- 7dfa271c42c4 Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactionFilterDelegate with new FOnFilterTransactionDelegate, which also passes const FTransactionObjectEvent& along. This allows subscribers to filter out changes based on properties changed.
```

### 维护评价

Remote Control API 是一个**成熟且仍在维护**的插件。它创建于 2019 年，是虚拟制作管线的核心组件之一。从近期提交记录看，更新主要集中在与底层多用户框架（Concert）的接口适配上，属于维护性更新，表明 Epic 仍在确保其与引擎新版本的兼容性。虽然更新频率不高，但作为关键基础设施，其稳定性和可靠性至关重要。**推荐在需要远程控制引擎的项目中使用**，尤其是虚拟制片和自动化领域。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/remote-control-api-in-unreal-engine/) (UE5 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/RemoteControlTest)