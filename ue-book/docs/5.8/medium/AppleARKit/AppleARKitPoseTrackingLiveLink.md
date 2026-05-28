# Apple ARKit

> Support for Apple's ARKit augmented reality system

| 属性 | 值 |
|---|---|
| 中文名 | 苹果ARKit |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `AppleARKit` (Runtime), `AppleARKitPoseTrackingLiveLink` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit) | |

## 用途

本插件为 Apple 的 ARKit 增强现实系统提供支持。具体而言，它专注于将 ARKit 采集的人体 3D 姿态（骨骼）数据通过 Unreal Engine 的 **LiveLink** 系统进行传输，使动画蓝图能够实时接收并应用这些来自真实世界的运动数据。这主要解决 iOS 设备上 ARKit 动作捕捉数据与 UE5 动画系统的无缝集成问题。

## 使用场景

-   你在开发一款需要实时捕捉真人动作来驱动虚拟角色的 iOS AR 应用。
-   你需要将 iPhone 或 iPad 上 ARKit 捕捉的全身骨骼数据，通过 LiveLink 传输到 PC 端的 Unreal 编辑器或打包程序中，用于动画预览、虚拟制片或实时互动体验。
-   你正在使用 LiveLink 构建一个统一的动作捕捉数据流，而 ARKit 是你的数据源之一。

## 蓝图用法

本插件的核心功能通过 LiveLink 和 AR 子系统暴露，而非直接的蓝图函数。直接相关的蓝图资产（`UDEPRECATED_AppleARKitPoseTrackingLiveLinkRemapAsset`）已被废弃。实际使用中，开发者通常在蓝图中操作 LiveLink 主题，或通过 AR 会话配置来启用姿态追踪。

### 核心节点
（基于 LiveLink 和 AR 系统的通用蓝图节点）
| 节点 | 说明 | 所在类/系统 |
|---|---|---|
| `Get Live Link Subsystem` | 获取 LiveLink 子系统，用于管理源和主题。 | `ULiveLinkSubsystem` |
| `Get AR Session Config` | 获取当前 AR 会话的配置，用于启用姿态追踪。 | `UARSessionConfig` (需其他 AR 插件) |

### 使用示例（蓝图描述）
1.  **数据接收端蓝图**：在您的动画蓝图或角色蓝图中，使用 `Live Link` 节点连接到相应的 ARKit Pose Tracking 主题，将实时骨骼变换数据应用到角色的骨骼网格体上。
2.  **配置端**：在项目的 `UARSessionConfig` 资产中，需要启用人体追踪相关设置（此部分配置通常由其他核心 AR 插件提供，如 `AppleARKit` 模块）。

## C++ 用法

### 头文件引入
```cpp
#include "AppleARKitPoseTrackingLiveLinkModule.h" // 核心模块接口
```

### 基本用法
获取并初始化 LiveLink 姿态追踪源。通常，此操作在模块启动时由 `FAppleARKitPoseTrackingLiveLinkImpl` 内部完成，应用开发者较少直接调用。
```cpp
// 来源: Private/AppleARKitPoseTrackingLiveLinkImpl.h 及相关实现
// 创建 LiveLink 源工厂并初始化
TSharedPtr<ILiveLinkSourceARKitPoseTracking> LiveLinkSource = FAppleARKitPoseTrackingLiveLinkSourceFactory::CreateLiveLinkSource();
if (LiveLinkSource.IsValid())
{
    // 源会自动向 LiveLink 客户端注册
}
```

### 进阶用法
实现自定义的重定向逻辑。虽然 `UDEPRECATED_AppleARKitPoseTrackingLiveLinkRemapAsset` 已被废弃，但新逻辑通过 `IARLiveLinkRetargetingLogic` 接口和 `UARLiveLinkRetargetAsset` 实现。
```cpp
// 来源: Private/AppleARKitPoseTrackingLiveLinkModule.h
// FAppleARKitPoseTrackingLiveLinkModule 实现了 IARLiveLinkRetargetingLogic
// 你可以在自定义的重定向资产中覆盖 BuildPoseFromAnimationData 函数，
// 来调整从 ARKit 骨骼空间到你项目角色骨骼空间的变换。
class UMyCustomARRetargetAsset : public UARLiveLinkRetargetAsset
{
    // ... 覆盖构建姿态的逻辑
};
```

## Demo 示例

一个最小的示例，展示如何在模块中集成并响应 ARKit 姿态数据。

**MyPoseTrackingComponent.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "AppleARKitPoseTrackingLiveLinkModule.h" // 包含插件核心头文件

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyPoseTrackingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    // 持有对 LiveLink 姿态追踪模块的引用
    FAppleARKitPoseTrackingLiveLinkModule* PoseTrackingModule;
};
```

**MyPoseTrackingComponent.cpp**
```cpp
#include "MyPoseTrackingComponent.h"
#include "AppleARKitPoseTrackingLiveLinkModule.h"

void UMyPoseTrackingComponent::BeginPlay()
{
    Super::BeginPlay();
    // 获取已加载的 PoseTracking 模块实例
    PoseTrackingModule = FModuleManager::GetModulePtr<FAppleARKitPoseTrackingLiveLinkModule>(TEXT("AppleARKitPoseTrackingLiveLink"));
    if (PoseTrackingModule)
    {
        // 模块已初始化，其内部的 LiveLink 源已开始工作。
        // 你可以在动画蓝图中直接订阅 LiveLink 主题来接收数据。
        UE_LOG(LogTemp, Log, TEXT("ARKit Pose Tracking LiveLink module is active."));
    }
}

void UMyPoseTrackingComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理引用
    PoseTrackingModule = nullptr;
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `AppleARKitPoseTrackingLiveLink.Build.cs` 分析得出。要使用此插件，你的模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `IOSRuntimeSettings` | 获取 iOS 平台相关的运行时配置，ARKit 功能高度依赖于此。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位格式说明符不匹配的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 调用迁移到新的 `UE_LOGF` 宏。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或屏蔽了不可达代码的编译器警告。 |
| 2026-04-10 | `e18acf19` | More unreachable code warning fixes | 继续修复不可达代码警告。 |
| 2026-03-19 | `7662e97c` | Fix incorrect scene texture sampling uv in postprocess materials after TSR. This also caused incorre... | (部分信息) 修复了TSR后处理材质中场景纹理采样UV错误的问题。 |

### 维护评价
- **年龄**：插件创建于 2020 年，已存在约 6 年。
- **近期更新**：最近的几次提交（截至2026年）主要是编译器警告修复和代码清理，属于维护性更新，未涉及新功能。
- **维护频率**：更新不频繁，属于维护中但非活跃开发状态。
- **状态评估**：该插件功能稳定，专注于解决 ARKit 姿态追踪与 LiveLink 集成这一特定问题。由于底层 ARKit 和 LiveLink 系统持续维护，此插件也随之进行必要的适配和清理。**可以正常使用**，但预期不会有重大新功能。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit)
- 测试用例：未在提供的源码路径下发现专用测试文件。