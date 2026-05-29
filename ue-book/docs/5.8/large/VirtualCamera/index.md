# VirtualCamera

> Content for VirtualCameraCore which adds actors, components, and utilities for controlling and viewing cameras via physical devices.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟摄像机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、组件） |
| 模块 | `VCamExtensions` (Runtime), `VCamExtensionsEditor` (Runtime), `VirtualCamera` (Runtime), `VirtualCameraEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera) | |

## 用途
VirtualCamera 插件旨在为 Unreal Engine 的虚拟制片 (Virtual Production) 工作流提供一套完整的虚拟摄像机解决方案。它解决了导演和摄影师在虚拟场景中通过物理设备（如 iPad、专用手柄或动作捕捉设备）像操作真实摄影机一样控制、预览和录制虚拟摄像机镜头的核心需求。此插件是 **VirtualCameraCore** 的内容扩展，提供了蓝图友好的 Actor、组件和输入设备映射系统，是虚拟摄像机功能的实际应用层。

## 使用场景
- **电影/电视虚拟制片**：在 LED 幕墙或绿幕前，导演使用手持设备实时操控虚拟摄像机，决定最终拍摄画面。
- **虚拟制片棚 (StageCraft)**：在 ICVFX（In-Camera VFX）流程中，精确控制虚拟背景摄像机的位置和运动。
- **预演 (Previs) 与技术预览**：使用直观的物理设备快速搭建和演练复杂镜头序列。
- **动画与内容创作**：利用物理设备为虚拟场景创建流畅、自然的摄像机动画路径。

## 蓝图用法
该插件的核心在于将物理设备输入映射到虚拟摄像机的控制上，并通过 Actor 和组件提供场景内的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Virtual Camera` | 在场景中生成一个配置好的虚拟摄像机 Actor | `UVirtualCameraBlueprintLibrary` |
| `Set Input Device Mapping` | 将当前的输入设备（如 iPad）映射到指定的虚拟摄像机 | `UVirtualCameraSubsystem` |
| `Set Camera Settings` | 设置虚拟摄像机的焦距、光圈等参数 | `AVirtualCameraActor` |
| `Start/Stop Recording` | 开始或停止录制虚拟摄像机的运动数据 | `AVirtualCameraActor` |
| `Get Active Viewport` | 获取当前虚拟摄像机正在查看的视口信息 | `AVirtualCameraActor` |

### 使用示例（蓝图描述）
1.  **生成与控制**：在关卡蓝图或Actor蓝图中，使用 `Spawn Virtual Camera` 节点生成一个虚拟摄像机 Actor。然后，通过 `Set Input Device Mapping` 节点将其与运行在 iPad 上的 Unreal Remote App 或其他支持的输入源连接。
2.  **实时预览**：虚拟摄像机 Actor 会自动将其视图输出到指定的输出端口（如用于 LED 墙的 nDisplay 集群）。在 iPad 上移动设备，虚拟摄像机视角将实时同步变化。
3.  **录制镜头**：在蓝图中调用 `Start Recording` 开始录制。导演在 iPad 上进行拍摄操作，完成后调用 `Stop Recording`，录制的摄像机动画数据将被保存。

## C++ 用法
在 C++ 中，可以更精细地控制虚拟摄像机系统，例如创建自定义的输入处理逻辑或扩展摄像机功能。

### 头文件引入
```cpp
#include "VirtualCameraSubsystem.h"
#include "VirtualCameraActor.h"
#include "VirtualCameraComponent.h"
```

### 基本用法
生成并配置一个虚拟摄像机 Actor。
```cpp
// 获取虚拟摄像机子系统
UVirtualCameraSubsystem* VCamSubsystem = GEngine->GetEngineSubsystem<UVirtualCameraSubsystem>();

// 定义生成参数
FActorSpawnParameters SpawnParams;
SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

// 在指定位置生成虚拟摄像机 Actor
AVirtualCameraActor* SpawnedCamera = GetWorld()->SpawnActor<AVirtualCameraActor>(
    AVirtualCameraActor::StaticClass(),
    FTransform(FRotator::ZeroRotator, FVector(0, 0, 200)),
    SpawnParams);

if (SpawnedCamera)
{
    // 访问并修改其组件设置
    UVirtualCameraComponent* VCamComp = SpawnedCamera->GetVirtualCameraComponent();
    if (VCamComp)
    {
        // 设置焦距等
        VCamComp->SetFieldOfView(50.f);
    }
}
```

### 进阶用法
监听虚拟摄像机子系统的设备连接和输入事件。
```cpp
// 在某个类（如 GameInstance）的初始化中
UVirtualCameraSubsystem* VCamSubsystem = GEngine->GetEngineSubsystem<UVirtualCameraSubsystem>();
if (VCamSubsystem)
{
    // 绑定设备状态变化事件
    VCamSubsystem->OnInputDeviceConnectionChanged.AddDynamic(this, &UMyClass::HandleDeviceConnectionChanged);
}

// 事件处理函数
void UMyClass::HandleDeviceConnectionChanged(bool bIsConnected, const FVirtualCameraInputDeviceHandle& DeviceHandle)
{
    if (bIsConnected)
    {
        UE_LOG(LogTemp, Log, TEXT("Virtual Camera Input Device Connected: %s"), *DeviceHandle.ToString());
        // 可以在这里自动将新设备绑定到默认摄像机
    }
}
```

## Demo 示例
一个最小化的虚拟摄像机 Actor 子类，用于演示如何在 C++ 中扩展。
```cpp
// MyCustomVCamActor.h
#pragma once
#include "VirtualCameraActor.h"
#include "MyCustomVCamActor.generated.h"

UCLASS()
class AMyCustomVCamActor : public AVirtualCameraActor
{
    GENERATED_BODY()

public:
    AMyCustomVCamActor();

    // 覆盖默认设置
    virtual void BeginPlay() override;

    // 自定义的蓝图可调用函数
    UFUNCTION(BlueprintCallable, Category = "Custom VCam")
    void ApplyCinematicPreset();
};

// MyCustomVCamActor.cpp
#include "MyCustomVCamActor.h"
#include "VirtualCameraComponent.h"

AMyCustomVCamActor::AMyCustomVCamActor()
{
    // 在构造函数中获取并修改默认设置
    if (UVirtualCameraComponent* VCamComp = GetVirtualCameraComponent())
    {
        VCamComp->SetFilmbackSettings(FVector2D(24.0f, 13.5f)); // 设置电影画幅
    }
}

void AMyCustomVCamActor::BeginPlay()
{
    Super::BeginPlay();
    // 在游戏开始时应用自定义逻辑
    UE_LOG(LogTemp, Log, TEXT("Custom Virtual Camera Actor is active."));
}

void AMyCustomVCamActor::ApplyCinematicPreset()
{
    if (UVirtualCameraComponent* VCamComp = GetVirtualCameraComponent())
    {
        VCamComp->SetFieldOfView(35.f);
        VCamComp->SetFocusDistance(300.f);
        VCamComp->SetAperture(2.8f);
        UE_LOG(LogTemp, Log, TEXT("Cinematic preset applied."));
    }
}
```

## 模块依赖
你的项目需要依赖此插件，如果要在自己的 C++ 模块中深度集成，需在 `.Build.cs` 文件中添加：

| 模块 | 用途 |
|---|---|
| `VirtualCamera` | 核心运行时逻辑，提供虚拟摄像机 Actor、组件和子系统 |
| `VCamExtensions` | 提供额外的组件、蓝图库和输入设备映射等扩展功能 |
| `EnhancedInput` | **关键依赖**。插件使用增强输入系统处理来自物理设备的复杂输入映射和转换 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 对虚拟制片资产进行了分类调整和迁移，属于内容管理优化。 |
| 2026-04-20 | `9de9532f` | VCam: update transform track mask based on constraint filter | 根据约束过滤器更新了变换轨道掩码，增强了动画录制的精度。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新式的 UE_LOGF 宏，是代码现代化的一部分。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次提交中错误的全局替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的某次更改，通常是为了修复引入的严重问题。 |

### 维护评价
**积极维护**。该插件创建于 2024 年初，且 **近期更新非常频繁**（2026 年 5 月仍有实质性提交），表明 Epic Games 对其作为虚拟制片核心工具之一正在持续开发和优化。虽然目前仍标记为 `IsBetaVersion: true` 和 `EnabledByDefault: false`，但其活跃的代码提交（包括功能增强、重构和bug修复）强烈暗示它正朝着正式版本迈进。对于正在或计划开展虚拟制片项目的团队，**推荐密切关注并评估使用**，但需注意其 Beta 状态可能带来的 API 变更。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera)
- [官方文档]() （暂无，可关注 Epic 官方虚拟制片文档更新）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera/Source/VirtualCamera/Private/Tests) （可能存在）