# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime), `VCamBlueprintNodes` (Runtime), `VCamCore` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

`VirtualCameraCore` 是一套用于构建虚拟制片中相机控制系统的核心框架。它提供了管理虚拟相机的 Actor、组件以及通过物理设备（如 iPad）控制和查看相机视图的基础架构。该插件本身不包含具体内容资产（如蓝图、材质），而是提供底层代码和 API，供其他插件（如 `VirtualCamera`）或项目使用。当前文档聚焦于其 `DecoupledOutputProvider` 模块，该模块的核心设计目标是将输出提供者（Output Provider）的**数据**（可在所有平台加载）与其**运行时逻辑**（仅在特定平台如支持Pixel Streaming的设备上加载）解耦，从而避免在打包（Cooking）过程中因逻辑模块缺失而导致的警告或错误。

## 使用场景

-   你正在开发一个虚拟制片（Virtual Production）项目，需要通过 iPad 或其他移动设备远程控制 UE5 中的 CineCamera Actor。
-   你的项目需要将 UE5 视窗实时串流（Pixel Streaming）到移动设备上，并接收设备的跟踪数据（如 ARKit）来驱动相机运动。
-   你希望定义自定义的“输出提供者”，但需要确保其核心数据资产能在所有目标平台（包括不支持特定运行时逻辑的平台）上安全加载和编辑。

## 蓝图用法

`UDecoupledOutputProvider` 及其子类（如 `UVCamPixelStreamingSession`）的属性可在蓝图中编辑，从而配置虚拟相机的输出行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bMatchRemoteResolution` | 勾选后，UE 串流视窗的分辨率将自动匹配远程设备的分辨率。 | `UVCamPixelStreamingSession` |
| `EnableARKitTracking` | 启用后，可通过 LiveLink 应用接收的 ARKit 跟踪数据来控制对应的 CineCamera。 | `UVCamPixelStreamingSession` |
| `PreventEditorIdle` | 启用可防止编辑器在非前台运行时进入空闲状态，避免虚拟相机控制响应迟钝。 | `UVCamPixelStreamingSession` |
| `bAutoSetLiveLinkSubject` | 启用后，当此输出提供者激活时，会自动将所属 VCam 组件的 LiveLink 主体设置为由本提供者创建的主体。 | `UVCamPixelStreamingSession` |
| `bOverrideStreamerName` | 是否使用自定义的串流名称。 | `UVCamPixelStreamingSession` |
| `StreamerId` | 在 `bOverrideStreamerName` 为 true 时生效，设置此串流器报告给信令服务器的唯一标识。 | `UVCamPixelStreamingSession` |

### 使用示例（蓝图描述）

1.  在 `VCam Actor` 或其组件的详情面板中，找到 `Output Provider` 属性。
2.  创建或分配一个 `VCam Pixel Streaming Session` 资产。
3.  在该资产的属性面板中，根据需求勾选 `Match Remote Resolution`、`Enable ARKit Tracking` 等选项。
4.  在 `VCam` 组件上，通常可以设置 `Live Link Subject Name`，如果启用了 `bAutoSetLiveLinkSubject`，该名称将被自动覆盖。
5.  当在移动设备上打开对应的 Pixel Streaming 应用并连接时，这些蓝图属性设置将控制虚拟相机的输出和输入行为。

## C++ 用法

通过继承 `UDecoupledOutputProvider` 并实现 `IOutputProviderLogic` 接口，可以创建自定义的、与数据解耦的输出提供者逻辑。

### 头文件引入

```cpp
#include "DecoupledOutputProvider.h"
#include "IOutputProviderLogic.h"
#include "IDecoupledOutputProviderModule.h"
```

### 基本用法

创建自定义的输出提供者逻辑类并注册其工厂函数。

**来源：** 基于 `IOutputProviderLogic.h` 和 `IDecoupledOutputProviderModule.h` 的接口设计。

```cpp
// MyCustomProviderLogic.h
#pragma once
#include "IOutputProviderLogic.h"

class FMyCustomProviderLogic : public UE::DecoupledOutputProvider::IOutputProviderLogic
{
public:
    virtual void OnInitialize(UE::DecoupledOutputProvider::IOutputProviderEvent& Args) override;
    virtual void OnTick(UE::DecoupledOutputProvider::IOutputProviderEvent& Args, const float DeltaTime) override;
    // ... 其他需要重写的事件
};

// MyCustomProvider.h
#pragma once
#include "DecoupledOutputProvider.h"
#include "MyCustomProvider.generated.h"

UCLASS(Blueprintable)
class UMyCustomProvider : public UDecoupledOutputProvider
{
    GENERATED_BODY()
public:
    // 可以添加自定义的数据属性（UPROPERTY）
    // 这些数据将安全地存在于所有平台
};
```

```cpp
// MyModule.cpp (在你的模块 StartupModule 中)
#include "IDecoupledOutputProviderModule.h"
#include "MyCustomProvider.h"
#include "MyCustomProviderLogic.h"

void FMyModule::StartupModule()
{
    // 确保 DecoupledOutputProvider 模块可用
    if (UE::DecoupledOutputProvider::IDecoupledOutputProviderModule::IsAvailable())
    {
        auto& Module = UE::DecoupledOutputProvider::IDecoupledOutputProviderModule::Get();
        // 为我们的自定义提供者类注册逻辑工厂
        Module.RegisterLogicFactory(
            UMyCustomProvider::StaticClass(),
            UE::DecoupledOutputProvider::FOutputProviderLogicFactoryDelegate::CreateLambda(
                [](const UE::DecoupledOutputProvider::FOutputProviderLogicCreationArgs& Args)
                {
                    // 创建并返回逻辑对象的共享指针
                    return MakeShared<FMyCustomProviderLogic>();
                }
            )
        );
    }
}
```

### 进阶用法

在逻辑对象中处理更复杂的生命周期事件，并利用 `IOutputProviderEvent` 与基础的 `UDecoupledOutputProvider` 数据对象交互。

**来源：** 基于 `IOutputProviderLogic.h` 和 `IOutputProviderEvent` 类的设计。

```cpp
// 在 FMyCustomProviderLogic 实现中
#include "MyCustomProvider.h"

void FMyCustomProviderLogic::OnInitialize(UE::DecoupledOutputProvider::IOutputProviderEvent& Args)
{
    // 通过事件参数访问关联的数据对象
    UMyCustomProvider& DataProvider = static_cast<UMyCustomProvider&>(Args.GetOutputProvider());
    
    // 读取数据属性
    if (DataProvider.bShouldActivateSpecialMode)
    {
        // 执行初始化特定模式的逻辑
    }

    // 调用基类实现（如果需要）
    Args.ExecuteSuperFunction();
}

void FMyCustomProviderLogic::OnTick(UE::DecoupledOutputProvider::IOutputProviderEvent& Args, const float DeltaTime)
{
    // 例如，从设备接收输入数据并驱动相机
    UMyCustomProvider& DataProvider = static_cast<UMyCustomProvider&>(Args.GetOutputProvider());
    
    // 假设 DataProvider 有一个指向相机的引用
    if (AActor* ControlledCamera = DataProvider.ControlledCameraActor.Get())
    {
        // 根据设备输入更新相机变换...
        // ControlledCamera->SetActorTransform(...);
    }
}

void FMyCustomProviderLogic::OnActivate(UE::DecoupledOutputProvider::IOutputProviderEvent& Args)
{
    // 当提供者被激活时，可能需要启动网络连接或初始化传感器
    UE_LOG(LogTemp, Log, TEXT("Custom Output Provider Activated"));
}
```

## Demo 示例

一个最小化的自定义输出提供者实现，演示数据与逻辑的解耦。

```cpp
// SimpleDecoupledProvider.h
#pragma once
#include "DecoupledOutputProvider.h"
#include "SimpleDecoupledProvider.generated.h"

/** 一个简单的、只包含数据的解耦输出提供者。 */
UCLASS(Blueprintable)
class USimpleDecoupledProvider : public UDecoupledOutputProvider
{
    GENERATED_BODY()
public:
    /** 一个简单的数据属性，可在所有平台安全地序列化。 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Simple Provider")
    FString ProviderName = TEXT("Default");
};

// SimpleProviderLogic.h
#pragma once
#include "IOutputProviderLogic.h"

/** 为 USimpleDecoupledProvider 实现的逻辑类。 */
class FSimpleProviderLogic : public UE::DecoupledOutputProvider::IOutputProviderLogic
{
public:
    virtual void OnInitialize(UE::DecoupledOutputProvider::IOutputProviderEvent& Args) override
    {
        USimpleDecoupledProvider& Provider = static_cast<USimpleDecoupledProvider&>(Args.GetOutputProvider());
        UE_LOG(LogTemp, Log, TEXT("Simple Logic Initialized for Provider: %s"), *Provider.ProviderName);
    }

    virtual void OnTick(UE::DecoupledOutputProvider::IOutputProviderEvent& Args, const float DeltaTime) override
    {
        // 此处可以放置每帧需要执行的逻辑，例如处理输入、发送数据等。
        // 因为这是一个示例，所以留空。
    }
};

// SimpleProviderModule.cpp (在你的插件或模块中)
#include "IDecoupledOutputProviderModule.h"
#include "SimpleDecoupledProvider.h"
#include "SimpleProviderLogic.h"

void FSimpleProviderModule::StartupModule()
{
    if (UE::DecoupledOutputProvider::IDecoupledOutputProviderModule::IsAvailable())
    {
        auto& Module = UE::DecoupledOutputProvider::IDecoupledOutputProviderModule::Get();
        Module.RegisterLogicFactory(
            USimpleDecoupledProvider::StaticClass(),
            UE::DecoupledOutputProvider::FOutputProviderLogicFactoryDelegate::CreateLambda(
                [](const UE::DecoupledOutputProvider::FOutputProviderLogicCreationArgs& Args)
                {
                    return MakeShared<FSimpleProviderLogic>();
                }
            )
        );
    }
}
```

## 模块依赖

根据模块的典型功能推断，使用者可能需要依赖 `VCamCore` 以访问虚拟相机的核心类型（如 `UVCamOutputProviderBase`）。具体依赖请参考你项目中 `Build.cs` 的 `PublicDependencyModuleNames`。

| 模块 | 用途 |
|---|---|
| `VCamCore` | 提供虚拟相机系统的核心基类、接口和功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复了在 PIE（播放中编辑）和模拟模式下运行时的崩溃问题。 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复了当引擎资产定义插件未包含时，虚拟制片相关功能产生的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将虚拟制片相关资产迁移至不同的资产分类目录。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF` 格式。 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏控件迁移到一个新的非实验性插件中。 |

### 维护评价

-   **活跃维护**：从提交历史看，该插件在2026年仍有频繁的更新和Bug修复，表明其处于**活跃维护**状态。
-   **实验性**：`.uplugin` 文件明确标记为 `IsBetaVersion: true`，属于**实验性**插件，API 和功能可能在未来版本中发生变化。
-   **推荐使用**：适用于正在开发虚拟制片项目、特别是需要跨平台输出或 Pixel Streaming 功能的团队。由于其处于Beta阶段，建议在生产环境中谨慎评估，并准备好应对可能的API变动。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore)
-   测试用例：暂未在插件目录中发现标准测试文件。