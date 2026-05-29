# Live Link Preston MDR

> Live Link support for the Preston MDR-3 Motor Driver

| 属性 | 值 |
|---|---|
| 中文名 | Preston 镜头控制 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Live Link 源工厂、设置资产） |
| 模块 | `LiveLinkPrestonMDR` (Runtime), `LiveLinkPrestonMDREditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR) | |

## 用途

本插件为 Unreal Engine 的 **Live Link** 系统提供了一个源（Source），用于连接和接收 **Preston MDR-3** 马达驱动器的实时数据。Preston MDR-3 是电影摄影中常用的 FIZ（Focus, Iris, Zoom）镜头马达控制系统。

该插件的核心功能是通过网络套接字（Socket）与 MDR-3 设备通信，按照其私有协议解析数据包，提取镜头参数（焦距、光圈、变焦）、马达状态和时间码，并将这些数据转换为 UE 的 `FLiveLinkCameraFrameData` 格式，通过 Live Link 框架广播给引擎内的其他系统（如虚拟摄影机、动画蓝图等）。

它的存在使得在**虚拟制片（Virtual Production）**流程中，能够将实拍摄影机镜头的实时转动参数精确地同步到虚拟场景中，实现虚实画面的匹配和合成。

## 使用场景

- **虚拟制片 LED 墙**：在 LED 墙前进行实拍时，将 Preston 控制的摄影机镜头参数实时传递给 UE 内的虚拟摄影机，确保虚拟背景的透视和焦点与实拍画面完全同步。
- **动作捕捉与虚拟摄影机**：使用 Preston 手轮（Hand Unit）控制虚拟摄影机的焦点、光圈和变焦，进行实时预览和录制。
- **后期合成预览**：在拍摄现场，将实拍镜头的元数据实时发送到 UE，用于在合成软件或引擎内初步查看合成效果。
- **机器人摄影机控制**：结合 Motion Control 系统，使用 MDR-3 数据驱动虚拟或实拍摄影机的镜头运动。

## 蓝图用法

该插件的数据通过 Live Link 角色和数据结构暴露给蓝图。

### 核心数据结构

| 结构体 | 说明 |
|---|---|
| `FLiveLinkPrestonMDRStaticData` | 承载 Preston MDR 主题的静态数据（继承自相机静态数据）。 |
| `FLiveLinkPrestonMDRFrameData` | 承载每帧的动态数据，除了标准的 Transform 和相机参数外，还包含原始的 FIZ 马达编码器值。 |
| `FLiveLinkPrestonMDRBlueprintData` | 便于在蓝图中操作的完整数据包，包含上述静态和帧数据。 |

### 关键蓝图属性

在 `FLiveLinkPrestonMDRFrameData` 中：

| 属性 (BlueprintReadWrite) | 类型 | 说明 |
|---|---|---|
| `RawFocusEncoderValue` | `uint16` | 焦点马达的原始编码器值 |
| `RawIrisEncoderValue` | `uint16` | 光圈马达的原始编码器值 |
| `RawZoomEncoderValue` | `uint16` | 变焦马达的原始编码器值 |

### 使用示例（蓝图描述）

1.  **接收数据**：在任意蓝图中，使用 **Live Link** 节点（如 `Get Live Link Data` 或在动画蓝图中评估 Live Link 主题）来获取绑定了“Preston MDR Role”的主体数据。数据将以 `FLiveLinkPrestonMDRBlueprintData` 结构体的形式返回。
2.  **提取参数**：从返回的数据结构中，你可以直接访问 `FrameData.Transform`（获取虚拟摄影机位置/旋转）和 `FrameData.FieldOfView`（焦距换算值），以及自定义的 `RawFocusEncoderValue` 等原始值。
3.  **应用到虚拟摄影机**：将获取的 Transform 和 FieldOfView 数据设置给场景中的虚拟摄影机组件（CineCameraComponent），即可实现控制。

## C++ 用法

在 C++ 中，你可以更直接地与 Live Link 框架交互来消费此插件的数据。

### 头文件引入

```cpp
#include "LiveLinkPrestonMDRTypes.h" // 如果使用自定义结构体
#include "Roles/LiveLinkCameraRole.h" // 标准 Live Link 相机角色
#include "ILiveLinkClient.h"
```

### 基本用法 (从 Live Link 获取数据)

```cpp
// 假设你已经有一个 Live Link 主体密钥 (FLiveLinkSubjectKey) 指向你的 Preston MDR 源
FLiveLinkSubjectKey SubjectKey;

// 获取 Live Link 客户端单例 (通常在模块或子系统中)
ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get();

if (LiveLinkClient && LiveLinkClient->IsSubjectValid(SubjectKey))
{
    // 获取最新的静态数据
    FLiveLinkPrestonMDRStaticData StaticData;
    if (LiveLinkClient->EvaluateFrame_AnyThread(SubjectKey, StaticData))
    {
        // 处理静态数据 (相机的LensSettings, FocusDistance等)
    }

    // 获取最新的动态帧数据
    FLiveLinkPrestonMDRFrameData FrameData;
    if (LiveLinkClient->EvaluateFrame_AnyThread(SubjectKey, FrameData))
    {
        // 在这里使用数据
        FVector CameraLocation = FrameData.Transform.GetLocation();
        FRotator CameraRotation = FrameData.Transform.Rotator();
        float FocusValue = FrameData.FocusDistance;
        float IrisValue = FrameData.Aperture;

        // 访问自定义的原始值
        uint16 RawFocus = FrameData.RawFocusEncoderValue;
        // ... 驱动你的虚拟摄影机或其他系统
    }
}
```

### 进阶用法 (直接监听源状态)

你也可以通过 `FLiveLinkPrestonMDRSource` 暴露的委托来监听连接状态变化，但这需要对源对象有直接引用，通常通过自定义的 Live Link 源面板或编辑器扩展来实现。

## Demo 示例

以下是一个最小化的 C++ 类，演示如何从 Live Link 中轮询获取 Preston MDR 的数据并输出到日志。

**.h 文件 (MyPrestonDataMonitor.h)**
```cpp
// MyPrestonDataMonitor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkPrestonMDRTypes.h" // 引入自定义结构体
#include "LiveLinkTypes.h"
#include "ILiveLinkClient.h"

#include "MyPrestonDataMonitor.generated.h"

UCLASS()
class MYPROJECT_API AMyPrestonDataMonitor : public AActor
{
    GENERATED_BODY()

public:
    AMyPrestonDataMonitor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    // 指定要监听的 Live Link 主体名 (可在编辑器中设置)
    UPROPERTY(EditAnywhere, Category="Live Link")
    FName SubjectName = "Preston MDR";

private:
    FLiveLinkSubjectKey CachedSubjectKey;
    ILiveLinkClient* LiveLinkClient = nullptr;

    void FindAndCacheLiveLinkSubject();
    void QueryPrestonData();
};
```

**.cpp 文件 (MyPrestonDataMonitor.cpp)**
```cpp
// MyPrestonDataMonitor.cpp
#include "MyPrestonDataMonitor.h"
#include "LiveLinkSubsystem.h"

AMyPrestonDataMonitor::AMyPrestonDataMonitor()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.1f; // 每秒查询10次
}

void AMyPrestonDataMonitor::BeginPlay()
{
    Super::BeginPlay();
    FindAndCacheLiveLinkSubject();
}

void AMyPrestonDataMonitor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    QueryPrestonData();
}

void AMyPrestonDataMonitor::FindAndCacheLiveLinkSubject()
{
    // 获取 Live Link 子系统以访问客户端
    ULiveLinkSubsystem* LiveLinkSubsystem = GEngine->GetEngineSubsystem<ULiveLinkSubsystem>();
    if (LiveLinkSubsystem)
    {
        LiveLinkClient = LiveLinkSubsystem->GetClient();
    }

    if (LiveLinkClient)
    {
        // 将用户定义的 FName 转换为 Live Link 的主体键
        CachedSubjectKey = FLiveLinkSubjectKey(FLiveLinkSourceKey(FName("Preston MDR")), SubjectName);
        UE_LOG(LogTemp, Log, TEXT("开始监听 Live Link 主体: %s"), *SubjectName.ToString());
    }
}

void AMyPrestonDataMonitor::QueryPrestonData()
{
    if (!LiveLinkClient || !LiveLinkClient->IsSubjectValid(CachedSubjectKey))
    {
        return;
    }

    // 查询帧数据
    FLiveLinkPrestonMDRFrameData FrameData;
    if (LiveLinkClient->EvaluateFrame_AnyThread(CachedSubjectKey, FrameData))
    {
        UE_LOG(LogTemp, Log, TEXT("Preston MDR Data - Focus: %f, Iris: %f, Zoom: %f, RawFocus: %u"),
               FrameData.FocusDistance, FrameData.Aperture, FrameData.FocalLength,
               FrameData.RawFocusEncoderValue);
    }
}
```

## 模块依赖

根据插件的功能（Live Link 源、网络通信、自定义数据类型）推断，你的模块可能需要依赖以下模块。**具体依赖关系请以插件自身的 `LiveLinkPrestonMDR.Build.cs` 文件为准。**

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架，用于注册源、传输数据。 |
| `LiveLinkInterface` | Live Link 的接口定义，包括 `ILiveLinkSource` 和角色基类。 |
| `Sockets` | 用于创建 TCP/UDP 套接字与 MDR-3 硬件通信。 |
| `Networking` | 网络基础支持。 |

*注意：标准依赖如 `Core`, `Engine` 等已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 格式，无功能变化。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码的错误，为编译器警告维护。 |
| 2024-01-25 | `f43fc1d7` | Fixed up more bool-taking calls to take EAllowShrinking instead. | 更新接口调用，将布尔参数替换为枚举类型，无功能变化。 |
| 2023-11-20 | `763a6119` | Fix C4072 warnings | 修复 C4072 编译器警告。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | (提交信息不完整，可能为大规模插件重构或更新的一部分) |

### 维护评价

- **创建时间**：2021 年 3 月，已有 5 年历史。
- **最近更新频率**：近 2 年的提交均为**编译器警告修复**或**引擎代码风格迁移**，**没有新增功能或重要错误修复**。
- **活跃度**：**维护不活跃**。最后一次有实质意义的更新可能早于 2023 年。
- **状态与建议**：该插件被标记为 `IsBetaVersion` 且默认不启用，结合其更新历史，**很可能处于实验性或低优先级维护状态**。它能完成基本的连接和数据接收功能，但可能存在未修复的边缘情况 bug 或兼容性问题。对于新项目，可以评估使用；如果项目长期维护，需注意其可能停止维护的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中发现)