# Live Link OpenTrackIO

> Live Link plugin for supporting OpenTrackIO (https://opentrackio.org) devices in Unreal Engine or Live Link Hub.

| 属性 | 值 |
|---|---|
| 中文名 | OpenTrackIO 实时链接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试数据） |
| 模块 | `LiveLinkOpenTrackIO` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-04-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkOpenTrackIO) | |

## 用途

本插件用于将支持 [OpenTrackIO](https://opentrackio.org) 标准的外部设备（主要是物理跟踪摄像头）的数据，实时集成到 Unreal Engine 中。它通过 UDP 网络连接接收符合 OpenTrackIO 规范的数据包，解析其中的摄像头姿态、镜头参数和元数据，并将其映射为 Unreal Engine 的 Live Link 主题。该主题使用 `ULiveLinkLensRole`，能够驱动虚拟摄像机、获取实时镜头数据。解决了虚拟制作（Virtual Production）中，物理摄像机跟踪数据与虚拟引擎场景同步的核心问题。

## 使用场景

- 你在搭建一个 LED 虚拟影棚，需要将现场的摄影机运动实时同步到 Unreal 中的虚拟摄像机。
- 你在进行多机位拍摄，每个摄影机都运行了 OpenTrackIO 跟踪软件，需要同时将多路数据接入 Unreal。
- 你在进行虚拟制作直播，需要低延迟地接收并渲染来自跟踪系统的数据。

## 蓝图用法

### 核心数据结构

该插件的核心是 `FLiveLinkOpenTrackIOData` 结构体，它在蓝图中以 `OpenTrackIO Data` 显示，包含了从 OpenTrackIO 设备接收的所有数据。你可以通过 Live Link 节点获取此数据。

| 节点 / 属性 | 说明 | 所在类 |
|---|---|---|
| `Transforms` | 存储摄像头在空间中的变换列表（位置、旋转、缩放）。通常使用第一个元素。 | `FLiveLinkOpenTrackIOData` |
| `Lens` | 包含动态镜头数据，如光圈 (Iris)、焦距 (FocalLength)、对焦距离 (FocusDistance) 等。 | `FLiveLinkOpenTrackIOData` |
| `Camera` | 包含与摄像头相关的静态或准静态数据，如 ISO、快门角度等。 | `FLiveLinkOpenTrackIOData` |
| `Custom` | 用于存放自定义的键值对数据。 | `FLiveLinkOpenTrackIOData` |

### 源设置 (Source Settings)

当创建 OpenTrackIO 源后，可以在 Live Link 窗口调整其设置。

| 属性 | 说明 | 所在类 |
|---|---|---|
| `Protocol` | 选择网络协议：`Multicast` (默认) 或 `Unicast`。 | `ULiveLinkOpenTrackIOSourceSettings` |
| `MulticastEndpoint` | 多播组地址和端口（仅当协议为 Multicast 时有效）。默认为 `239.135.1.1:55555`。 | `ULiveLinkOpenTrackIOSourceSettings` |
| `UnicastEndpoint` | 单播监听地址和端口（仅当协议为 Unicast 时有效）。`0.0.0.0:0` 表示绑定默认网卡。 | `ULiveLinkOpenTrackIOSourceSettings` |
| `SubjectsPerTransform` | 控制是否为 OpenTrackIO 数据中的每个变换 (Transform) 创建独立的 Live Link 主题。 | `ULiveLinkOpenTrackIOSourceSettings` |

### 使用示例 (蓝图描述)

1.  在 Live Link 窗口，点击 `+ Source` 并选择 `OpenTrackIO`。
2.  在弹出的设置面板中配置网络参数（如使用单播，则填写正确的端口），然后点击 `Create`。
3.  在 Live Link 主题列表中，找到新出现的主题，其 `Role` 应显示为 `OpenTrackIO`。
4.  在蓝图中，使用 `Get Live Link Data` 节点，将主题名称设为 OpenTrackIO 主题的名称。
5.  将 `Blueprint Data` 输出提升为变量，即可访问其中的 `StaticData` 和 `FrameData`，从而获取 `Transforms`、`Lens` 等实时数据。
6.  你可以将 `Transforms[0]` 中的位置和旋转数据应用到场景中的虚拟摄像机 Actor 上。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkOpenTrackIOTypes.h" // 核心数据结构
#include "LiveLinkOpenTrackIOConversions.h" // 坐标转换工具
```

### 基本用法

在代码中，你通常通过 Live Link 接口来间接使用本插件的数据。以下示例展示如何从一个已知的 OpenTrackIO Live Link 主题中提取数据。

```cpp
// 来源: 概念示例，结合 LiveLinkClient.h
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkLensRole.h"
#include "LiveLinkOpenTrackIOTypes.h"

// 假设你已经有一个有效的 Live Link Client 指针 (Client) 和主题名称 (SubjectName)
FLiveLinkSubjectKey SubjectKey;
SubjectKey.SubjectName = FName(TEXT("YourOpenTrackIOSubjectName"));

// 获取最新的帧数据
TSubclassOf<ULiveLinkRole> RoleClass = ULiveLinkLensRole::StaticClass();
FLiveLinkSubjectFrameData FrameData;
if (Client->EvaluateFrame_AnyThread(SubjectKey, RoleClass, FrameData))
{
    // 将通用帧数据转换为 OpenTrackIO 特定的帧数据
    if (FLiveLinkOpenTrackIOFrameData* OpenTrackFrameData = FrameData.FrameData.Cast<FLiveLinkOpenTrackIOFrameData>())
    {
        // 访问 OpenTrackIO 数据
        const FLiveLinkOpenTrackIOData& OpenTrackData = OpenTrackFrameData->OpenTrackData;

        // 例如，获取第一个变换的 Unreal 世界坐标 (已转换)
        if (OpenTrackData.Transforms.Num() > 0)
        {
            FTransform UnrealTransform = LiveLinkOpenTrackIOConversions::ToUnrealTransform(OpenTrackData.Transforms[0]);
            // 使用 UnrealTransform...
        }

        // 例如，获取光圈值 (检查是否设置)
        if (OpenTrackData.Lens.Iris.IsSet())
        {
            float Aperture = OpenTrackData.Lens.Iris.GetValue();
            // 使用 Aperture...
        }
    }
}
```

### 进阶用法

你可以直接创建一个 `FLiveLinkOpenTrackIOData` 实例，并使用转换工具函数来处理手动构造或从非 Live Link 来源获取的 OpenTrackIO 格式数据。

```cpp
// 来源: LiveLinkOpenTrackIOConversions.h
#include "LiveLinkOpenTrackIOConversions.h"

// 假设你已经手动填充了一个 FLiveLinkOpenTrackIOData 结构
FLiveLinkOpenTrackIOData MyData;
MyData.Transforms.Add(FLiveLinkOpenTrackIOTransform()); // 填充变换数据
MyData.Transforms[0].Translation.X = 1.0f; // OpenTrackIO 中的 X (米)
MyData.Transforms[0].Translation.Y = 2.0f; // OpenTrackIO 中的 Y (米)
MyData.Transforms[0].Rotation.Pan = 45.0f; // OpenTrackIO 中的 Pan (度)

// 将 OpenTrackIO 坐标系转换为 Unreal 坐标系
FTransform UnrealXform = LiveLinkOpenTrackIOConversions::ToUnrealTransform(MyData.Transforms[0]);
// UnrealXform 的 Translation 将会是 (200, 100, 0) cm，Rotation 的 Yaw 将会是 -45 度。

// 将 OpenTrackIO 镜头数据转换为 Live Link 镜头帧数据
FLiveLinkLensFrameData LensFrameData;
LiveLinkOpenTrackIOConversions::ToUnrealLens(LensFrameData, &MyData.Lens, &MyData.Camera);
// LensFrameData 现在包含了适用于 Unreal 的镜头参数。
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何在 Actor 中接收并处理 Live Link OpenTrackIO 数据。

**MyOpenTrackIOActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkLensRole.h"
#include "MyOpenTrackIOActor.generated.h"

UCLASS()
class AMyOpenTrackIOActor : public AActor
{
    GENERATED_BODY()

public:
    AMyOpenTrackIOActor();

    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

private:
    // Live Link 相关
    FName LiveLinkSubjectName = FName(TEXT("YourSubjectNameHere")); // 替换为你的主题名
    FLiveLinkSubjectKey LiveLinkSubjectKey;
    TSubclassOf<ULiveLinkRole> LiveLinkRoleClass = ULiveLinkLensRole::StaticClass();

    // 缓存的数据
    FTransform CachedCameraTransform;
    float CachedFocalLength = 35.0f;
};
```

**MyOpenTrackIOActor.cpp**
```cpp
#include "MyOpenTrackIOActor.h"
#include "ILiveLinkClient.h"
#include "LiveLinkOpenTrackIOTypes.h"
#include "LiveLinkOpenTrackIOConversions.h"
#include "Engine/World.h"

AMyOpenTrackIOActor::AMyOpenTrackIOActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyOpenTrackIOActor::BeginPlay()
{
    Super::BeginPlay();
    LiveLinkSubjectKey.SubjectName = LiveLinkSubjectName;
}

void AMyOpenTrackIOActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    UWorld* World = GetWorld();
    if (!World) return;

    // 获取 Live Link Client (这是一个全局单例)
    IModuleInterface* LiveLinkModule = FModuleManager::Get().LoadModule(TEXT("LiveLink"));
    if (!LiveLinkModule) return;

    // 注意：在实际代码中，通过更直接的方式获取 Client 指针，例如通过 LiveLinkSubsystem。
    // 此处为简化演示。
    // ILiveLinkClient* Client = ...; // 获取客户端实例

    FLiveLinkSubjectFrameData FrameData;
    // 假设 Client 有效
    // if (Client && Client->EvaluateFrame_AnyThread(LiveLinkSubjectKey, LiveLinkRoleClass, FrameData))
    {
        if (const FLiveLinkOpenTrackIOFrameData* OpenTrackFrameData = FrameData.FrameData.Cast<FLiveLinkOpenTrackIOFrameData>())
        {
            const FLiveLinkOpenTrackIOData& OpenTrackData = OpenTrackFrameData->OpenTrackData;

            // 更新摄像机变换
            if (OpenTrackData.Transforms.Num() > 0)
            {
                CachedCameraTransform = LiveLinkOpenTrackIOConversions::ToUnrealTransform(OpenTrackData.Transforms[0]);
                // 可以在这里设置某个 Scene Component 的相对变换
                // SetActorTransform(CachedCameraTransform);
            }

            // 更新焦距
            if (OpenTrackData.Lens.FocalLength.IsSet())
            {
                CachedFocalLength = OpenTrackData.Lens.FocalLength.GetValue();
                // 可以在这里更新摄像机组件的焦距属性
            }
        }
    }
}
```

## 模块依赖

要使用本插件，你的模块（例如你的游戏模块或编辑器模块）需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 框架核心模块 |
| `LiveLinkInterface` | Live Link 接口定义 |
| `LiveLinkLens` | 提供 `ULiveLinkLensRole` 和相关数据结构 |
| `Serialization` | 用于 CBOR 等序列化格式的支持 |
| `Json` | 用于解析 OpenTrackIO 的 JSON payload |
| `Cbor` | 用于解析 OpenTrackIO 的 CBOR payload |

在你的模块的 `.Build.cs` 文件中，需要添加这些模块依赖：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "LiveLink",
    "LiveLinkInterface",
    "LiveLinkLens",
    "Serialization",
    "Json",
    "Cbor"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志格式说明符与参数位数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新的 `UE_LOGF` 宏。 |
| 2026-03-02 | `4a046668` | Remove the old tests that relied on hardcoded values that are no longer relevant. We have the pyt | 移除了依赖旧硬编码值的过时测试，并提到拥有 Python 测试。 |
| 2026-03-02 | `47f30f8a` | Always set the camera static data. This will allow users to provide the sensor information but not r | 始终设置摄像头静态数据，允许用户提供传感器信息但不再要求其完整。 |
| 2026-03-02 | `1d461220` | Make CameraData a non-optional type as that allows us to support the minimal OpenTrackIO spec. We d | 将 `CameraData` 改为非可选类型，以支持 OpenTrackIO 的最小规范。 |

### 维护评价

该插件创建于 **2025年4月**，非常年轻，目前仍处于 **测试阶段（IsBetaVersion=true）**。从 git 历史看，开发活动**近期（2026年3-4月）相当活跃**，主要集中在修复问题、优化数据结构和改进测试上。这表明 Epic Games 正在持续迭代和开发此功能。

**当前状态**：实验性早期开发，有活跃维护，但功能（如蓝图完全访问、自定义数据）和验证（如变换矩阵计算）尚未完全完成。

**使用建议**：
- 对于 **虚拟制作领域的早期探索者或技术预研项目**，非常值得尝试，它提供了一个标准化的接入方式。
- 对于 **生产环境**，鉴于其 Beta 状态和已知限制，建议在测试阶段充分验证，并准备好应对未来 API 的变化。
- 推荐关注其后续版本，特别是当它从 Experimental 目录迁移出来或标记为正式版时。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkOpenTrackIO)
- [OpenTrackIO 规范](https://opentrackio.org)