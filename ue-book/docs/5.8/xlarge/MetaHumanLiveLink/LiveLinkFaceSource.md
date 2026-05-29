# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

该插件提供了一套完整的 Live Link 框架实现，专门用于从外部设备（如运行 Epic 的 Live Link Face 应用的 iPhone）实时流式传输 MetaHuman 角色的面部动画数据到 Unreal Engine 中。它解决的核心问题是：**将外部实时捕获的面部表情和头部动作数据，无缝、低延迟地映射并驱动引擎内的 MetaHuman 角色。** 插件通过处理自定义的 UDP 数据包，解析控制值（如 ARKit 或 MHA 生成的 blendshape 权重），并通过 Live Link 框架将这些数据广播到引擎，从而实现“所见即所得”的实时动画驱动。

## 使用场景

- **虚拟制片与实时直播**：使用 iPhone 上的 Live Link Face 应用捕获演员的面部表情，并实时驱动场景中的 MetaHuman 角色，用于虚拟制作预览或直播互动。
- **动画预览与预演**：动画师可以通过设备实时测试面部表情效果，快速迭代动画，而无需录制和回放。
- **多机位/多人表演**：通过插件的发现和连接机制，可以连接多个设备，同时驱动多个 MetaHuman 角色。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Live Link Face Source` | 创建一个 Live Link Face 数据源实例，并返回其句柄。 | `ULiveLinkFaceSourceBlueprint` |
| `Connect` | 使用指定的主题名称、地址和端口，将先前创建的数据源连接到远程设备。 | `ULiveLinkFaceSourceBlueprint` |
| `Set Head Orientation` | 设置是否接收并应用头部旋转（朝向）动画数据。 | `ULiveLinkFaceSubjectSettings` |
| `Get Head Orientation` | 获取当前是否接收头部旋转动画数据的设置。 | `ULiveLinkFaceSubjectSettings` |
| `Set Head Translation` | 设置是否接收并应用头部平移（位置）动画数据。 | `ULiveLinkFaceSubjectSettings` |
| `Get Head Translation` | 获取当前是否接收头部平移动画数据的设置。 | `ULiveLinkFaceSubjectSettings` |

### 使用示例（蓝图描述）

1.  **创建数据源**：在你的蓝图（如 PlayerController 或专门的管理蓝图）中，调用 `Create Live Link Face Source` 节点。这会创建一个数据源实例，并输出一个 `LiveLinkFaceSource` 句柄和一个 `Succeeded` 布尔值。
2.  **连接设备**：接下来，调用 `Connect` 节点。将上一步的 `LiveLinkFaceSource` 句柄连接过来，输入运行 Live Link Face 应用的 iPhone 的 IP 地址（`SubjectName`），以及默认端口 `14785`。连接成功后，Live Link 面板中会出现一个新的源。
3.  **配置主题设置**：在 Live Link 面板中找到连接的主题，或在蓝图中通过其他方式获取其设置对象 (`ULiveLinkFaceSubjectSettings`)。使用 `Set Head Orientation` 和 `Set Head Translation` 节点来控制是否应用头部的旋转和位移动画数据。通常两者都应为 `true` 以获得完整的头部运动。
4.  **驱动角色**：将 Live Link 主题数据绑定到你的 MetaHuman 角色蓝图中的 `Live Link Component` 或 `Animation Blueprint`，即可看到面部表情被实时驱动。

## C++ 用法

### 头文件引入

```cpp
// 核心 Live Link Face 源
#include "LiveLinkFaceSource.h"

// 蓝图函数库
#include "LiveLinkFaceSourceBlueprint.h"

// 主题设置
#include "LiveLinkFaceSubjectSettings.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码手动创建并连接一个 Live Link Face 源。这适用于需要更精细控制连接时机或参数的场景。
*(来源: `LiveLinkFaceSourceBlueprint.h`, `LiveLinkFaceSource.h`)*

```cpp
// 假设在某个 Actor 或 GameInstance 中
#include "LiveLinkFaceSourceBlueprint.h"
#include "LiveLinkFaceSource.h"

void AMyActor::ConnectToLiveLinkFaceDevice(const FString& DeviceIPAddress)
{
    FLiveLinkSourceHandle SourceHandle;
    bool bSucceeded = false;
    
    // 步骤 1: 创建数据源实例
    ULiveLinkFaceSourceBlueprint::CreateLiveLinkFaceSource(SourceHandle, bSucceeded);
    if (!bSucceeded)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create LiveLinkFaceSource"));
        return;
    }
    
    // 步骤 2: 连接到设备（使用默认端口14785）
    ULiveLinkFaceSourceBlueprint::Connect(SourceHandle, TEXT("MySubject"), DeviceIPAddress, bSucceeded);
    if (bSucceeded)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully connected to Live Link Face device at %s"), *DeviceIPAddress);
    }
}
```

### 进阶用法

1.  **直接实例化源**：`ULiveLinkFaceSourceBlueprint` 是蓝图友好的封装。在纯 C++ 中，你也可以直接使用 `FLiveLinkFaceSource`。
    ```cpp
    // 需要包含 LiveLink 接口头文件
    #include "ILiveLinkClient.h"
    
    // 创建源
    FString ConnectionString = TEXT("192.168.1.100:14785");
    TSharedPtr<ILiveLinkSource> MySource = MakeShareable(new FLiveLinkFaceSource(ConnectionString));
    
    // 将其注册到 Live Link 系统 (通常需要通过 IModularFeatures)
    // 实际项目中，蓝图方法或编辑器菜单创建更常用。
    ```

2.  **配置主题设置**：连接成功后，可以通过 Live Link 主题键获取并修改其设置。
    ```cpp
    #include "LiveLinkFaceSubjectSettings.h"
    #include "ILiveLinkClient.h"
    
    // 假设已获取 LiveLinkClient 指针和主题键
    ILiveLinkClient* LiveLinkClient = ...;
    FLiveLinkSubjectKey SubjectKey = ...;
    
    ULiveLinkFaceSubjectSettings* Settings = Cast<ULiveLinkFaceSubjectSettings>(
        LiveLinkClient->GetSubjectSettings(SubjectKey));
    
    if (Settings)
    {
        // 禁用头部平移，只保留朝向
        Settings->SetHeadTranslation(false);
        Settings->SetHeadOrientation(true);
    }
    ```

## Demo 示例

一个最小的、用于测试连接的 Actor 类。

### MyLiveLinkFaceTestActor.h
```cpp
// MyLiveLinkFaceTestActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkSourceHandle.h"
#include "MyLiveLinkFaceTestActor.generated.h"

UCLASS()
class AMyLiveLinkFaceTestActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyLiveLinkFaceTestActor();
    
    // 要连接的设备IP地址
    UPROPERTY(EditAnywhere, Category="Live Link Face")
    FString DeviceAddress = TEXT("192.168.1.100");
    
    // 主题名称
    UPROPERTY(EditAnywhere, Category="Live Link Face")
    FString SubjectName = TEXT("TestSubject");
    
    // 开始按钮（在编辑器细节面板中显示）
    UFUNCTION(CallInEditor, Category="Live Link Face")
    void ConnectToFaceApp();
    
    UFUNCTION(CallInEditor, Category="Live Link Face")
    void Disconnect();
    
private:
    FLiveLinkSourceHandle LiveLinkSourceHandle;
};
```

### MyLiveLinkFaceTestActor.cpp
```cpp
// MyLiveLinkFaceTestActor.cpp
#include "MyLiveLinkFaceTestActor.h"
#include "LiveLinkFaceSourceBlueprint.h"

AMyLiveLinkFaceTestActor::AMyLiveLinkFaceTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyLiveLinkFaceTestActor::ConnectToFaceApp()
{
    bool bSucceeded = false;
    ULiveLinkFaceSourceBlueprint::CreateLiveLinkFaceSource(LiveLinkSourceHandle, bSucceeded);
    
    if (bSucceeded)
    {
        ULiveLinkFaceSourceBlueprint::Connect(LiveLinkSourceHandle, SubjectName, DeviceAddress, bSucceeded, 14785);
        if (bSucceeded)
        {
            UE_LOG(LogTemp, Log, TEXT("Connected to %s:%d as '%s'"), *DeviceAddress, 14785, *SubjectName);
        }
    }
}

void AMyLiveLinkFaceTestActor::Disconnect()
{
    // 根据 Live Link 框架，销毁句柄通常会断开连接
    LiveLinkSourceHandle.Reset();
    UE_LOG(LogTemp, Log, TEXT("Disconnected from Live Link Face source"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorWidgets` | 提供编辑器 UI 控件，用于构建连接和设置界面。 |
| `UnrealEd` | 编辑器核心功能，用于集成编辑器菜单和资产浏览器。 |
| `PropertyEditor` | 用于创建和管理自定义的属性面板（Details Panel）编辑器。 |
| `LiveLink` | Live Link 框架的核心运行时，必须依赖。 |
| `CaptureManager` | 用于管理外部捕获设备（如 iPhone）的控制和数据流，是 `FLiveLinkFaceControl` 的底层实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 为身体动画暴露了检测阈值参数。 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 改进了面部动画序列的导出逻辑，以支持组合求解。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数导致的编译警告。 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | 在苹果平台上，为文件媒体源包使用了 AVFoundation 媒体后端。 |
| 2026-05-12 | `fa06fada` | New ADA model | 集成了新的 ADA 模型。 |

### 维护评价

- **创建时间**：插件于 2025 年 2 月创建，属于较新的官方插件。
- **更新频率**：从最近的提交记录看（2026年5月），插件仍在被 Epic Games 积极维护和开发，频繁有新功能（如身体动画阈值、ADA模型）和改进（如导出逻辑、平台兼容性）提交。
- **活跃度**：非常高。作为 MetaHuman 官方套件的关键实时组成部分，它受到持续关注。
- **已知问题**：暂无从提交记录中明确的长期未修复问题。
- **推荐使用**：**强烈推荐**。如果你的项目需要将移动设备捕获的实时面部/身体动画驱动 MetaHuman 角色，这是官方提供的最直接、集成度最高的解决方案。由于更新活跃，建议使用最新引擎版本以获得最佳体验和新功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档]() (待 Epic 提供)
- [测试用例]() (暂未发现公开的独立测试用例目录)