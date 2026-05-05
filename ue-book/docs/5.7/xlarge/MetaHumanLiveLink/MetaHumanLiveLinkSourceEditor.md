# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画资产、Live Link预设） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件提供了一套完整的解决方案，用于将来自移动设备（如 iPhone）的实时面部捕捉数据流式传输到 Unreal Engine 5 中的 MetaHuman 角色。它解决了从物理设备发现、数据接收、协议解析到最终驱动 MetaHuman 面部动画的全链路问题。该插件是 MetaHuman 实时动画工作流的核心组件，使得创作者能够在编辑器或运行时，使用 iPhone 上的 Live Link Face 等应用实时预览和驱动高保真 MetaHuman 角色的面部表情。

## 使用场景

- **虚拟直播与实时表演**：主播或演员使用 iPhone 进行面部捕捉，其表情实时驱动 UE5 中的 MetaHuman 虚拟形象进行直播或录制。
- **实时动画预览**：动画师在 UE5 编辑器中实时查看 iPhone 捕捉的面部动画效果，快速迭代和调整 MetaHuman 角色的表演。
- **远程协作**：表演者与位于不同地点的动画师或导演协作，通过网络实时传输面部动画数据。
- **游戏内实时面部动画**：在支持的平台（如移动端）上，利用设备摄像头实现玩家面部表情到游戏角色的实时映射。

## 蓝图用法

该插件主要通过 Live Link 框架和编辑器 UI 进行操作，直接暴露的蓝图节点较少。核心交互发生在 Live Link 面板和源设置中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaHuman Live Link Source` | 创建一个 MetaHuman Live Link 源，用于连接设备。 | `UMetaHumanLiveLinkSourceFactory` |
| `Create Live Link Face Source` | 创建一个 Live Link Face 源，用于连接 iPhone 应用。 | `ULiveLinkFaceSourceFactory` |

### 使用示例（蓝图描述）

1.  **连接设备**：在编辑器中，打开 `Live Link` 面板（窗口 -> Live Link）。点击 `Source` 下拉菜单，选择 `MetaHuman Live Link` 或 `Live Link Face`。在弹出的设置窗口中，输入 iPhone 设备的 IP 地址或从发现的设备列表中选择。
2.  **应用到角色**：在场景中选中你的 MetaHuman 角色蓝图，在其 `Details` 面板中找到 `Animation` -> `Live Link` 部分。将 `Subject Name` 设置为与 Live Link 面板中连接的源对应的 Subject 名称。
3.  **开始捕捉**：在 iPhone 上打开 Live Link Face 应用，连接到 UE5 项目。此时，MetaHuman 角色的面部应开始实时响应 iPhone 捕捉的表情。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanLiveLinkSource.h"
#include "MetaHumanLiveLinkSubjectSettings.h"
```

### 基本用法

以下代码展示了如何在 C++ 中程序化地创建一个 MetaHuman Live Link 源并尝试连接设备。此逻辑通常封装在编辑器工具或自定义面板中。

```cpp
// 来源: 基于 MetaHumanLiveLinkSource 模块功能推断
#include "MetaHumanLiveLinkSource.h"
#include "LiveLinkClient.h"
#include "ILiveLinkClient.h"

void ConnectToMetaHumanDevice(const FString& DeviceIPAddress)
{
    // 获取 Live Link 客户端
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (ModularFeatures.IsModularFeatureAvailable(ILiveLinkClient::ModularFeatureName))
    {
        ILiveLinkClient* LiveLinkClient = &ModularFeatures.GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);

        // 创建 MetaHuman Live Link 源设置
        UMetaHumanLiveLinkSourceSettings* Settings = NewObject<UMetaHumanLiveLinkSourceSettings>();
        Settings->DeviceAddress = DeviceIPAddress;

        // 创建源并添加到客户端
        TSharedPtr<IMetaHumanLiveLinkSource> Source = MakeShared<FMetaHumanLiveLinkSource>(Settings);
        LiveLinkClient->AddSource(Source);
    }
}
```

### 进阶用法

结合 `MetaHumanLiveLinkSubjectSettings`，可以对特定的 Live Link Subject（即一个数据流，如“头部”或“眼睛”）进行更精细的控制，例如校准或重定向。

```cpp
// 来源: 基于 MetaHumanLiveLinkSubjectSettings 和编辑器定制推断
#include "MetaHumanLiveLinkSubjectSettings.h"
#include "MetaHumanLiveLinkSubjectSettingsCustomization.h"

void CustomizeSubjectSettings(UMetaHumanLiveLinkSubjectSettings* InSettings)
{
    // 在编辑器中，可以通过 IDetailCustomization 来扩展设置面板
    // FMetaHumanLiveLinkSubjectSettingsCustomization 就是为此目的创建的
    // 它允许在 Details 面板中为特定设置（如头部旋转校准）添加自定义按钮和UI

    // 例如，触发一个校准流程
    if (InSettings)
    {
        InSettings->CalibrateHeadRotation();
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个自定义的 Live Link 源，该源可以生成模拟的 MetaHuman 面部数据。这可用于测试或作为开发自定义源的起点。

**MyMetaHumanLiveLinkSource.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "LiveLinkSource.h"
#include "ILiveLinkClient.h"

class FMyMetaHumanLiveLinkSource : public ILiveLinkSource
{
public:
    FMyMetaHumanLiveLinkSource();
    virtual ~FMyMetaHumanLiveLinkSource();

    // ILiveLinkSource interface
    virtual void ReceiveClient(ILiveLinkClient* InClient, FGuid InSourceGuid) override;
    virtual bool IsSourceStillValid() const override;
    virtual bool RequestSourceShutdown() override;
    virtual FText GetSourceType() const override { return FText::FromString(TEXT("My MetaHuman Source")); }
    virtual FText GetSourceMachineName() const override { return FText::FromString(FPlatformProcess::ComputerName()); }
    virtual FText GetSourceStatus() const override { return FText::FromString(TEXT("Active")); }

private:
    ILiveLinkClient* Client;
    FGuid SourceGuid;
    bool bIsActive;
    FTimerHandle UpdateTimerHandle;

    void Update();
    void SendFaceData();
};
```

**MyMetaHumanLiveLinkSource.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyMetaHumanLiveLinkSource.h"
#include "Roles/LiveLinkAnimationRole.h"
#include "Roles/LiveLinkAnimationTypes.h"
#include "LiveLinkTypes.h"

FMyMetaHumanLiveLinkSource::FMyMetaHumanLiveLinkSource()
    : Client(nullptr)
    , bIsActive(true)
{
    // 启动一个定时器来模拟数据更新
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (World)
    {
        World->GetTimerManager().SetTimer(UpdateTimerHandle, this, &FMyMetaHumanLiveLinkSource::Update, 1.0f / 30.0f, true); // 30 FPS
    }
}

FMyMetaHumanLiveLinkSource::~FMyMetaHumanLiveLinkSource()
{
    RequestSourceShutdown();
}

void FMyMetaHumanLiveLinkSource::ReceiveClient(ILiveLinkClient* InClient, FGuid InSourceGuid)
{
    Client = InClient;
    SourceGuid = InSourceGuid;
}

bool FMyMetaHumanLiveLinkSource::IsSourceStillValid() const
{
    return bIsActive;
}

bool FMyMetaHumanLiveLinkSource::RequestSourceShutdown()
{
    bIsActive = false;
    if (UWorld* World = GEditor->GetEditorWorldContext().World())
    {
        World->GetTimerManager().ClearTimer(UpdateTimerHandle);
    }
    return true;
}

void FMyMetaHumanLiveLinkSource::Update()
{
    if (Client && bIsActive)
    {
        SendFaceData();
    }
}

void FMyMetaHumanLiveLinkSource::SendFaceData()
{
    // 创建一个 Live Link Subject
    FLiveLinkSubjectKey SubjectKey(SourceGuid, FName("MyMetaHumanFace"));

    // 创建动画帧数据
    FLiveLinkFrameDataStruct FrameData(FLiveLinkAnimationFrameData::StaticStruct());
    FLiveLinkAnimationFrameData& AnimFrameData = *FrameData.Cast<FLiveLinkAnimationFrameData>();

    // 模拟一些面部混合形状值 (0.0 到 1.0)
    // 实际应用中，这些值应来自面部捕捉设备或算法
    AnimFrameData.CurveValues.Add(0.5f); // 例如， JawOpen
    AnimFrameData.CurveValues.Add(0.2f); // 例如， SmileLeft
    AnimFrameData.CurveValues.Add(0.0f); // 例如， BrowUpLeft

    // 设置时间
    AnimFrameData.WorldTime = FPlatformTime::Seconds();

    // 发送数据到 Live Link 客户端
    Client->PushSubjectFrameData_AnyThread(SubjectKey, MoveTemp(FrameData));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 框架核心，提供源、角色、主题等基础架构。 |
| `MetaHumanCore` | MetaHuman 核心库，提供面部绑定、动画重定向等基础功能。 |
| `MetaHumanIdentity` | 用于处理 MetaHuman 身份资产和面部网格。 |
| `MetaHumanSDK` | MetaHuman SDK，提供与 MetaHuman 技术栈交互的接口。 |
| `UnrealEd` | 编辑器功能，用于 `MetaHumanLocalLiveLinkSource` 模块的编辑器集成。 |

## 维护状态

### 近期更新

- 09c462fbc626 GUI pass #rb robert.hillary
  - *解读：对插件的图形用户界面（GUI）进行了优化和调整。*
- 8c52f4bcca57 Ability to calibrate head rotation #rb robert.hillary
  - *解读：新增了头部旋转校准功能，提升了动画数据的准确性。*
- a3a29f966481 Move source actor to its own plugin #rb trivial
  - *解读：将源 Actor 移动到独立的插件中，进行了代码重构，可能是为了更好的模块化。*

### 维护评价

该插件创建于 **2025年2月**，非常新。从最近的提交记录看，它仍在**积极开发中**，近期有功能新增（头部校准）和界面优化。作为 MetaHuman 实时工作流的关键部分，预计会随着 MetaHuman 技术栈的更新而持续维护。目前没有发现已知的重大问题或废弃标记。**强烈推荐**给所有需要实时 MetaHuman 面部动画的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink)