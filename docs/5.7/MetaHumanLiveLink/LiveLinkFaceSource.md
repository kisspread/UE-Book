# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Live Link源和蓝图工具） |
| 模块 | `MetaHumanLiveLinkSource` (Runtime), `LiveLinkFaceSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件的核心功能是建立 Epic 的 MetaHuman 应用（如 MetaHuman Animator）与 Unreal Engine 之间的实时数据连接。它充当一个桥梁，允许将 MetaHuman 应用中捕捉或编辑的实时面部动画数据（包括表情、头部朝向和位移）通过 Live Link 协议流式传输到引擎中，从而驱动引擎内的 MetaHuman 角色。这解决了数字人动画实时预览和表演驱动的关键需求，使创作者能够在编辑器或运行时即时看到动画效果。

## 使用场景

- **实时动画表演**：演员佩戴面部捕捉设备，通过 MetaHuman 应用进行表演，动画数据实时传输到 UE 中的 MetaHuman 角色，用于虚拟制片或游戏过场动画的实时预览。
- **动画迭代与预览**：动画师在 MetaHuman 应用中调整面部动画，无需导出/导入即可在 UE 场景中实时查看最终效果，加速创作流程。
- **蓝图驱动的连接管理**：通过蓝图在运行时动态创建和管理 Live Link 连接，适用于需要灵活控制数据流的应用程序。

## 蓝图用法

该插件提供了专门的蓝图函数库，用于在蓝图中创建和管理 Live Link Face 源。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Live Link Face Source` | 创建一个新的 Live Link Face 源实例，并返回其句柄。 | `ULiveLinkFaceSourceBlueprint` |
| `Connect` | 使用指定的地址、端口和主题名称，将已创建的 Live Link Face 源连接到 MetaHuman 应用。 | `ULiveLinkFaceSourceBlueprint` |

### 使用示例（蓝图描述）

1.  **创建源**：在蓝图中，调用 `Create Live Link Face Source` 节点。该节点会输出一个 `Live Link Face Source` 句柄和一个表示是否成功的布尔值。
2.  **连接设备**：将上一步获得的句柄传递给 `Connect` 节点。同时，输入 MetaHuman 应用所在设备的 IP 地址（`Address`）、主题名称（`Subject Name`，通常为设备名或自定义标识）以及端口号（`Port`，默认为 14785）。执行后，即可建立连接，Live Link 面板中将出现对应的主题。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceSourceBlueprint.h"
#include "LiveLinkFaceSourceSettings.h"
```

### 基本用法

通过蓝图函数库在 C++ 中创建和连接源。
（来源：`Engine/Plugins/MetaHuman/MetaHumanLiveLink/Source/LiveLinkFaceSource/Public/LiveLinkFaceSourceBlueprint.h`）

```cpp
// 创建 Live Link Face 源
FLiveLinkSourceHandle SourceHandle;
bool bSucceeded = false;
ULiveLinkFaceSourceBlueprint::CreateLiveLinkFaceSource(SourceHandle, bSucceeded);

if (bSucceeded)
{
    // 连接到 MetaHuman 应用
    const FString DeviceIP = TEXT("192.168.1.100");
    const FString SubjectName = TEXT("MyMetaHumanDevice");
    const int32 Port = 14785;
    
    ULiveLinkFaceSourceBlueprint::Connect(SourceHandle, SubjectName, DeviceIP, bSucceeded, Port);
}
```

### 进阶用法

直接操作源设置对象，进行更精细的控制。
（来源：`Engine/Plugins/MetaHuman/MetaHumanLiveLink/Source/LiveLinkFaceSource/Public/LiveLinkFaceSourceSettings.h`）

```cpp
// 假设你已经通过某种方式获取到了 ULiveLinkFaceSourceSettings 对象（例如，从 Live Link 面板）
ULiveLinkFaceSourceSettings* Settings = GetMySourceSettings(); // 伪代码

if (Settings)
{
    // 修改连接参数
    Settings->SetAddress(TEXT("10.0.0.50"));
    Settings->SetPort(14786);
    Settings->SetSubjectName(TEXT("NewSubject"));
    
    // 验证地址并请求重新连接
    if (Settings->IsAddressValid())
    {
        Settings->RequestConnect();
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在 Actor 中创建并连接一个 Live Link Face 源。

**MyMetaHumanConnector.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkSourceHandle.h"
#include "MyMetaHumanConnector.generated.h"

UCLASS()
class AMyMetaHumanConnector : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanConnector();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void ConnectToMetaHumanApp(const FString& IPAddress, const FString& SubjectName, int32 Port = 14785);

private:
    FLiveLinkSourceHandle LiveLinkSourceHandle;
};
```

**MyMetaHumanConnector.cpp**
```cpp
#include "MyMetaHumanConnector.h"
#include "LiveLinkFaceSourceBlueprint.h"

AMyMetaHumanConnector::AMyMetaHumanConnector()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanConnector::ConnectToMetaHumanApp(const FString& IPAddress, const FString& SubjectName, int32 Port)
{
    bool bSucceeded = false;
    
    // 1. 创建源
    ULiveLinkFaceSourceBlueprint::CreateLiveLinkFaceSource(LiveLinkSourceHandle, bSucceeded);
    if (!bSucceeded)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Live Link Face source."));
        return;
    }

    // 2. 连接
    ULiveLinkFaceSourceBlueprint::Connect(LiveLinkSourceHandle, SubjectName, IPAddress, bSucceeded, Port);
    if (bSucceeded)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully connected to MetaHuman App at %s:%d"), *IPAddress, Port);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to connect to MetaHuman App at %s:%d"), *IPAddress, Port);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架，提供主题、源和连接管理的基础架构。 |
| `LiveLinkInterface` | Live Link 的接口定义，用于实现自定义源和处理器。 |
| `MetaHumanIdentity` | MetaHuman 身份资产相关功能，可能用于处理面部绑定和动画数据映射。 |

## 维护状态

### 近期更新

- `d4a8efe9cd5c` 2025-10-03 Bughawk fixes #rb robert.hillary
  *（解读：针对特定问题（Bughawk）的修复，表明插件正在积极处理已知问题。）*
- `e2805c4d4c17` 2025-09-15 Support creating realtime Live Link sources via blueprint #rb robert.hillary
  *（解读：增加了通过蓝图创建实时 Live Link 源的功能，这是一个重要的功能增强。）*
- `8c52f4bcca57` 2025-08-20 Ability to calibrate head rotation #rb robert.hillary
  *（解读：增加了头部旋转校准功能，提升了动画数据的准确性。）*

### 维护评价

该插件创建于 2025 年初，非常年轻。从最近的提交记录看，它在近几个月内持续获得功能更新和错误修复，**处于活跃维护状态**。作为 MetaHuman 工作流的核心组件，预计 Epic 会持续投入资源进行维护和升级。目前没有发现已知的重大限制或废弃迹象，**推荐在需要实时 MetaHuman 动画驱动的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现公开的测试用例路径）