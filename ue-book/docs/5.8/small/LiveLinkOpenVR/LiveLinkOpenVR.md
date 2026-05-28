# LiveLinkOpenVR

> Live Link plugin for OpenVR (Not supported for native arm64.)

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接OpenVR |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOpenVR` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkOpenVR) | |

## 用途

这个插件为 **Live Link** 系统提供了一个基于 **OpenVR** (SteamVR) 的数据源。它主要用于 **LiveLinkHub** 这类多进程应用程序，解决之前使用 **LiveLinkXR** 插件时遇到的一些工作流问题。其核心作用是允许 Unreal Engine 的 Live Link 系统能够稳定地消费来自 SteamVR 的设备（如追踪器、控制器、基站、HMD）的实时位姿和输入数据，为虚拟制片和 VR 开发提供灵活的数据分发能力。

## 使用场景

- 你在进行**虚拟制片**，需要将 SteamVR 追踪的**摄像机**或**追踪器**数据发送到另一个独立的渲染进程或引擎实例（如使用 LiveLinkHub）。
- 你需要一个比 LiveLinkXR 更稳定或更适合多进程架构的 OpenVR 数据源。
- 你需要将 SteamVR **手柄**的输入（按钮、摇杆）映射到 Unreal Engine 的 `GamepadInputDevice` 角色中，用于虚拟制片或交互控制。

## 蓝图用法

此插件主要通过 Live Link 系统界面操作，本身不暴露大量蓝图节点。其配置主要在编辑器的 Live Link 面板中完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `获取 VR 系统` | 返回当前加载的 OpenVR IVRSystem 接口指针，用于底层 VR 操作。 | `FLiveLinkOpenVRModule` |
| `加载 OpenVR 库` | 手动加载 OpenVR 动态链接库，通常模块启动时自动执行。 | `FLiveLinkOpenVRModule` |
| `卸载 OpenVR 库` | 手动卸载 OpenVR 动态链接库，通常模块关闭时自动执行。 | `FLiveLinkOpenVRModule` |

### 使用示例（蓝图描述）

此插件的使用主要在编辑器中：
1.  打开 **Live Link** 窗口（Window > Live Link）。
2.  点击 **Source** 下拉菜单，选择 **LiveLinkOpenVR**。
3.  在弹出的设置面板中，配置要追踪的设备类型（追踪器、控制器、HMD、基站）以及更新频率。
4.  创建源后，对应的 OpenVR 设备会自动成为 Live Link Subject，你可以在场景中创建 `Live Link Component` 并指定该 Subject 来获取实时变换。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkOpenVRModule.h"
```

### 基本用法

获取 OpenVR 系统接口，用于执行底层 VR 操作。
```cpp
// 获取 OpenVR 模块实例
FLiveLinkOpenVRModule& OpenVRModule = FLiveLinkOpenVRModule::Get();

// 获取 IVRSystem 接口
vr::IVRSystem* VrSystem = OpenVRModule.GetVrSystem();
if (VrSystem)
{
    // 使用 VrSystem 进行操作，例如获取设备追踪状态
    vr::TrackedDevicePose_t Poses[vr::k_unMaxTrackedDeviceCount];
    VrSystem->GetDeviceToAbsoluteTrackingPose(vr::TrackingUniverseStanding, 0, Poses, vr::k_unMaxTrackedDeviceCount);
}
```

### 进阶用法

通过 `LiveLinkClient` 订阅由 OpenVR 源提供的 Live Link Subject。
```cpp
// 获取 LiveLink 客户端
UWorld* World = GetWorld();
if (World)
{
    ULiveLinkSubsystem* LiveLinkSubsystem = World->GetSubsystem<ULiveLinkSubsystem>();
    if (LiveLinkSubsystem)
    {
        ILiveLinkClient* LiveLinkClient = LiveLinkSubsystem->GetClient();

        // 创建一个 Subject Key，假设源名称和主题名称已知
        FLiveLinkSubjectKey SubjectKey;
        // ... (设置 SourceGuid 和 SubjectName)

        // 订阅该主题的数据
        LiveLinkClient->SubscribeSubject(SubjectKey);

        // 在 Tick 中获取最新数据
        FLiveLinkFrameData FrameData;
        if (LiveLinkClient->GetSubjectData(SubjectKey, FrameData))
        {
            // 处理 FrameData 中的变换、输入等数据
        }
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何在 Actor 中获取并使用来自 LiveLinkOpenVR 源的 HMD 位姿。

### OpenVRHMDTracker.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkTypes.h"
#include "OpenVRHMDTracker.generated.h"

UCLASS()
class AOpenVRHMDTracker : public AActor
{
    GENERATED_BODY()
    
public:
    AOpenVRHMDTracker();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category="LiveLink")
    FLiveLinkSubjectName HMDSubjectName;

private:
    FGuid LiveLinkSourceGuid;
};
```

### OpenVRHMDTracker.cpp
```cpp
#include "OpenVRHMDTracker.h"
#include "LiveLinkSubsystem.h"
#include "ILiveLinkClient.h"

AOpenVRHMDTracker::AOpenVRHMDTracker()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AOpenVRHMDTracker::BeginPlay()
{
    Super::BeginPlay();
    // 此处可以添加初始化代码，确保 LiveLink 源已创建
}

void AOpenVRHMDTracker::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    UWorld* World = GetWorld();
    if (!World) return;

    ULiveLinkSubsystem* LiveLinkSubsystem = World->GetSubsystem<ULiveLinkSubsystem>();
    if (!LiveLinkSubsystem) return;

    ILiveLinkClient* LiveLinkClient = LiveLinkSubsystem->GetClient();
    if (!LiveLinkClient) return;

    // 构建 Subject Key
    FLiveLinkSubjectKey SubjectKey;
    SubjectKey.SubjectName = HMDSubjectName;
    // 注意：SourceGuid 需要根据你创建的 OpenVR 源的 GUID 来设置，这里仅为示例
    // SubjectKey.Source = LiveLinkSourceGuid;

    // 获取最新的帧数据
    FLiveLinkFrameData FrameData;
    if (LiveLinkClient->GetSubjectData(SubjectKey, FrameData))
    {
        // 从 FrameData 中提取变换
        if (FrameData.Transforms.Num() > 0)
        {
            const FTransform& DeviceTransform = FrameData.Transforms[0].Transform;
            // 使用 DeviceTransform 更新本 Actor 的位置和旋转
            SetActorTransform(DeviceTransform);
        }
    }
}
```

## 模块依赖

从代码结构推断，使用此插件需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 核心接口，是所有 Live Link 源和客户端的必需依赖。 |
| `OpenVR` | 本插件内置的 OpenVR SDK 外部模块，用于与 SteamVR 运行时通信。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF`，属于引擎范围的日志系统更新。 |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis. | 引擎构建系统更新，支持按 CPU 架构包含/排除插件模块，本插件因此支持禁用 arm64。 |
| 2025-05-23 | `f3063039` | LiveLinkOpenVR disabled for arm64 | 明确在构建配置中禁用了该插件对 Win64 arm64 架构的支持。 |
| 2024-11-22 | `8ca76f71` | LiveLinkOpenVR: Improved default bindings. | 改进了插件的默认数据绑定，可能提升了开箱即用的兼容性。 |
| 2024-09-27 | `9d145f1b` | LiveLinkOpenVR: Marshal SteamVR Input into LiveLinkGamepadInputDevice role. | 新增功能：将 SteamVR 手柄的输入映射到 Live Link 的 `GamepadInputDevice` 角色，扩展了插件用途。 |

### 维护评价

- **创建时间**：2024年9月，是一个相对较新的插件。
- **最近更新**：最近的更新集中在2025年和2026年，最近一次是2026年4月的编译适配，表明项目仍在跟随引擎主分支维护。
- **活跃度**：尽管更新频率不高，但至今仍有实质性更新（如输入映射功能），属于**活跃维护**状态。
- **已知限制**：插件在 `.uplugin` 中明确标注为 **Experimental** 且 **EnabledByDefault=false**，不支持原生 arm64，目前仅用于 Windows x64 平台。官方可能在后续版本进行重大更改或整合。
- **推荐度**：如果你需要**将 SteamVR 数据多进程分发到 LiveLinkHub**，并且遇到了 LiveLinkXR 的特定问题，那么这个官方实验性插件是值得一试的稳定方案。但对于常规单进程 VR 开发，LiveLinkXR 可能仍是更主流的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkOpenVR)
- [官方文档]( ) (无)
- [测试用例]( ) (未在提供信息中明确)