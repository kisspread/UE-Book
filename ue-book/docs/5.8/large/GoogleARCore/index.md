# Google ARCore

> Support for Google's AR platform.

| 属性 | 值 |
|---|---|
| 中文名 | 谷歌ARCore |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置与资产） |
| 模块 | `GoogleARCoreBase` (Runtime), `GoogleARCoreRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-28 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore) | |

## 用途

本插件的核心目的是在 Unreal Engine 项目中集成谷歌的 ARCore SDK。它为 Android 平台提供了完整的 AR 功能支持，使得开发者能够在支持 ARCore 的 Android 设备上创建增强现实应用。插件封装了 ARCore 的核心能力，如运动跟踪、环境理解（平面检测）、光照估计等，并将其无缝接入 UE 的 `UARSessionConfig` 和 AR 系统框架中。

## 使用场景

- 你需要为 Android 设备开发一个增强现实（AR）应用。
- 你的项目需要在现实世界中放置虚拟物体，并需要稳定的运动追踪和表面识别。
- 你希望利用设备的摄像头和传感器来估计现实世界的光照，以便让虚拟物体的光影效果更真实。
- 你需要一个标准化的接口来管理 AR 会话的配置和生命周期。

## 蓝图用法

在蓝图中使用 Google ARCore 主要围绕配置 `UGoogleARCoreSessionConfig` 资产和调用会话功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get ARCore Session` | 获取当前的 ARCore 会话实例 | `UGoogleARCoreBlueprintLibrary` |
| `Start AR Session` | 使用指定配置启动 AR 会话 | `UARSessionConfig` (继承) |
| `Get ARCore Device Orientation` | 获取设备的当前朝向（用于相机配置） | `UGoogleARCoreBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **配置**：在内容浏览器中创建一个新的 `GoogleARCoreSessionConfig` 资产。在此资产中，你可以勾选“Plane Detection”来启用平面检测，或调整光照估计模式。
2.  **启动会话**：在你的主逻辑蓝图（如 `GameMode` 或 `PlayerController`）中，调用 `Start AR Session` 节点，并将你的 `GoogleARCoreSessionConfig` 资产作为输入。
3.  **使用功能**：会话启动后，可以通过 `Get ARCore Session` 节点获取会话对象，进而查询检测到的平面、获取光照信息等。

## C++ 用法

在 C++ 中使用需要链接相应的模块并处理平台特定的逻辑。

### 头文件引入

```cpp
#include "GoogleARCoreSessionConfig.h"
#include "GoogleARCoreFunctionLibrary.h"
```

### 基本用法

```cpp
// 创建并配置一个 ARCore 会话配置对象
UGoogleARCoreSessionConfig* ARConfig = NewObject<UGoogleARCoreSessionConfig>();
ARConfig->bEnablePlaneDetection = true;

// 启动 AR 会话 (通常在合适的生命周期函数中调用)
UARSessionConfig* BaseConfig = ARConfig;
UARBlueprintLibrary::StartARSession(BaseConfig);

// 在后续逻辑中查询 AR 功能
TArray<UARTrackedGeometry*> TrackedGeometries = UARBlueprintLibrary::GetAllGeometries();
```

### 进阶用法

组合使用 `GoogleARCoreRendering` 模块中的类，可以自定义 AR 相机的渲染后处理效果，例如应用特定的材质来处理 AR 相机画面的色调或添加滤镜。

## Demo 示例

一个最小的 C++ 示例，展示如何配置并启动一个基本的 ARCore 会话。

**MyARActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyARActor.generated.h"

class UGoogleARCoreSessionConfig;

UCLASS()
class AMyARActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyARActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UGoogleARCoreSessionConfig* SessionConfig;
};
```

**MyARActor.cpp**
```cpp
#include "MyARActor.h"
#include "GoogleARCoreSessionConfig.h"
#include "ARBlueprintLibrary.h"

AMyARActor::AMyARActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyARActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建配置资产
    SessionConfig = NewObject<UGoogleARCoreSessionConfig>();
    SessionConfig->bEnablePlaneDetection = true;

    // 启动 AR 会话
    if (UARBlueprintLibrary::IsARSupported())
    {
        UARBlueprintLibrary::StartARSession(SessionConfig);
        UE_LOG(LogTemp, Log, TEXT("ARCore session started."));
    }
}
```

## 模块依赖

要在你的项目中使用此插件的功能，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GoogleARCoreBase` | 核心 AR 功能、配置和蓝图库 |
| `GoogleARCoreRendering` | AR 相机的渲染和后处理相关功能 |
| `AugmentedReality` | UE 的 AR 抽象层和基础功能 |
| `AndroidPermission` | 在 Android 上处理 ARCore 运行时所需的权限 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中可能导致错误输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32 位格式说明符与 64 位参数不匹配导致的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移到 UE_LOGF |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复不可达代码的编译警告 |
| 2026-03-19 | `7662e97c` | Fix incorrect scene texture sampling uv in postprocess materials after TSR. | 修复 TSR 后在后处理材质中场景纹理采样 UV 不正确的问题 |

### 维护评价

**活跃维护**。尽管插件创建于2019年，但近期的 git 历史显示更新非常频繁（最近一次更新在2026年4月）。这些更新主要是**代码质量改进、平台兼容性修复和引擎内部接口迁移**（如 UE_LOG 到 UE_LOGF），表明 Epic 仍在积极维护此插件以确保其与最新引擎版本兼容。

作为平台特定的插件，它的功能相对稳定。**推荐在 Android AR 项目中使用**，但需注意：
1.  **默认未启用**：必须在项目的插件设置中手动启用。
2.  **平台限制**：仅支持 Android 平台。
3.  **持续维护**：虽然更新频繁，但多为内部优化，核心 AR API 较为稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore)
- [官方文档](https://developers.google.com/ar/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore/Tests)