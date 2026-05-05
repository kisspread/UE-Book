# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DecoupledOutputProvider.build` (Runtime), `PixelStreamingVCam` (Runtime), `VCamBlueprintNodes.build` (Runtime), `VCamCore` (Runtime), `VCamCoreEditor.build` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

VirtualCameraCore 是 Unreal Engine 虚拟制片工具链的核心运行时框架。它解决的核心问题是**将物理设备（如 iPad、iPhone）的输入数据与引擎内的虚拟摄像机解耦**，并提供一个标准化的架构来管理虚拟摄像机的输出。

其主要存在意义在于：
1.  **解耦架构**：通过 `UDecoupledOutputProvider` 和 `IOutputProviderLogic` 的设计模式，将输出提供者的数据（属性）与逻辑（行为）分离。这使得数据可以在所有平台上安全加载（避免打包时的 `LoadPackage` 警告），而实际的逻辑（如像素流、ARKit 追踪）仅在支持的平台上实例化和执行。
2.  **标准化接口**：为虚拟摄像机的输入（来自 LiveLink 等）和输出（到视口、像素流等）提供统一的基类和接口，便于扩展和集成。
3.  **蓝图友好**：提供大量可配置的蓝图属性和节点，让设计师和技术美术无需编写 C++ 代码即可快速搭建和调整虚拟摄像机工作流。

## 使用场景

-   你正在使用 **iPad 或 iPhone 上的 LiveLink VCAM 应用** 来实时控制 Unreal Editor 或游戏中的 CineCamera Actor。
-   你需要将虚拟摄像机的视图通过 **Pixel Streaming** 实时推送到远程设备（如 iPad）上，供导演或摄影师监看。
-   你希望在虚拟制片流程中，**将设备的 ARKit 追踪数据直接映射到场景中的摄像机**，实现增强现实预览。
-   你需要一个**可扩展的框架**，以便未来集成新的输入设备或输出目标，而无需重写核心摄像机控制逻辑。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bMatchRemoteResolution` | 是否使流式传输的 UE 视口分辨率与远程设备匹配 | `UVCamPixelStreamingSession` |
| `EnableARKitTracking` | 是否启用 ARKit 追踪来控制关联的 CineCamera | `UVCamPixelStreamingSession` |
| `PreventEditorIdle` | 当编辑器非前台应用时，是否防止输入变得迟钝 | `UVCamPixelStreamingSession` |
| `bAutoSetLiveLinkSubject` | 启用时，是否自动将所属 VCam 组件的 LiveLink 主题设置为本提供者创建的主题 | `UVCamPixelStreamingSession` |
| `bOverrideStreamerName` | 是否使用自定义的流媒体 ID 名称 | `UVCamPixelStreamingSession` |
| `StreamerId` | 自定义的流媒体 ID 名称，用于向信令服务器报告 | `UVCamPixelStreamingSession` |

### 使用示例（蓝图描述）

1.  **创建像素流会话**：在场景中放置一个 `VCamActor` 或拥有 `VCamComponent` 的 Actor。在其“输出提供者”数组中，添加一个 `Pixel Streaming Provider` 类型的元素。
2.  **配置输出**：在新添加的 `UVCamPixelStreamingSession` 属性中：
    *   勾选 `bMatchRemoteResolution` 以确保远程设备获得最佳画质。
    *   勾选 `EnableARKitTracking` 以允许设备运动控制摄像机。
    *   勾选 `PreventEditorIdle` 以保证在编辑器后台运行时输入响应流畅。
    *   如果需要自定义流名称，勾选 `bOverrideStreamerName` 并在 `StreamerId` 中输入唯一名称。
3.  **连接设备**：在支持的设备（如 iPad）上打开 LiveLink VCAM 应用，连接到运行 Unreal Engine 的电脑。应用将自动发现并连接到配置好的像素流会话，开始传输追踪数据和接收视频流。

## C++ 用法

### 头文件引入

```cpp
#include "DecoupledOutputProvider.h"
#include "IOutputProviderLogic.h"
#include "IDecoupledOutputProviderModule.h"
```

### 基本用法：继承输出提供者

创建一个自定义的输出提供者，它只包含数据，逻辑由外部模块提供。

```cpp
// MyCustomOutputProvider.h
#pragma once
#include "DecoupledOutputProvider.h"
#include "MyCustomOutputProvider.generated.h"

UCLASS(BlueprintType)
class MYMODULE_API UMyCustomOutputProvider : public UDecoupledOutputProvider
{
    GENERATED_BODY()
public:
    // 自定义数据属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Settings")
    float MyCustomValue = 1.0f;
};
```

### 进阶用法：实现输出提供者逻辑

在支持的平台上，为自定义提供者实现具体的逻辑。

```cpp
// MyCustomOutputProviderLogic.h
#pragma once
#include "IOutputProviderLogic.h"

class FMyCustomOutputProviderLogic : public UE::DecoupledOutputProvider::IOutputProviderLogic
{
public:
    virtual void OnActivate(UE::DecoupledOutputProvider::IOutputProviderEvent& Args) override
    {
        // 当提供者被激活时执行的逻辑
        Args.ExecuteSuperFunction(); // 调用基类实现
        // ... 初始化自定义资源
    }

    virtual void OnTick(UE::DecoupledOutputProvider::IOutputProviderEvent& Args, const float DeltaTime) override
    {
        // 每帧更新逻辑
        auto& Provider = static_cast<UMyCustomOutputProvider&>(Args.GetOutputProvider());
        float Value = Provider.MyCustomValue; // 读取提供者数据
        // ... 使用 Value 进行计算
    }
};
```

在模块启动时注册逻辑工厂。

```cpp
// MyModule.cpp
#include "IDecoupledOutputProviderModule.h"
#include "MyCustomOutputProvider.h"
#include "MyCustomOutputProviderLogic.h"

void FMyModule::StartupModule()
{
    auto& DOPModule = UE::DecoupledOutputProvider::IDecoupledOutputProviderModule::Get();
    DOPModule.RegisterLogicFactory(
        UMyCustomOutputProvider::StaticClass(),
        UE::DecoupledOutputProvider::FOutputProviderLogicFactoryDelegate::CreateLambda(
            [](const UE::DecoupledOutputProvider::FOutputProviderLogicCreationArgs& Args)
            {
                return MakeShared<FMyCustomOutputProviderLogic>();
            }
        )
    );
}
```

## Demo 示例

一个最小的自定义输出提供者及其逻辑实现。

**MyMinimalOutputProvider.h**
```cpp
#pragma once
#include "DecoupledOutputProvider.h"
#include "MyMinimalOutputProvider.generated.h"

UCLASS()
class UMyMinimalOutputProvider : public UDecoupledOutputProvider
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere)
    bool bEnableDebugDraw = false;
};
```

**MyMinimalOutputProviderLogic.h**
```cpp
#pragma once
#include "IOutputProviderLogic.h"

class FMyMinimalOutputProviderLogic : public UE::DecoupledOutputProvider::IOutputProviderLogic
{
public:
    virtual void OnTick(UE::DecoupledOutputProvider::IOutputProviderEvent& Args, const float DeltaTime) override
    {
        auto& Provider = static_cast<UMyMinimalOutputProvider&>(Args.GetOutputProvider());
        if (Provider.bEnableDebugDraw)
        {
            // 执行一些调试绘制逻辑
        }
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelEditor` | `PixelStreamingVCam` 模块依赖，用于编辑器集成 |
| `UnrealEd` | `PixelStreamingVCam` 模块依赖，用于编辑器功能 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

-   2025-10-03 958272d22131 移除 VPUtilities 和 VCamCore 对旧 composure 插件的使用
-   2025-09-15 676a92779b53 为 IOutputProviderLogic 添加 PreEditChange 事件
-   2025-08-20 84fb9763dc2f 像素流输出提供者现在默认将其 StreamId 设置为所属 Actor 的标签。用户可以通过新引入的 UVCamPixelStreamingSession::bOverrideStreamerName 字段覆盖该名称

### 维护评价

VirtualCameraCore 是一个相对年轻（约2年）且处于**活跃维护**状态的插件。从近期提交记录看，Epic Games 团队正在持续对其进行功能增强（如添加新的事件、优化默认行为）和清理（移除对旧插件的依赖）。由于其标记为 `IsBetaVersion: true`，表明它仍在积极开发和迭代中，API 可能会有变动。

**推荐使用**：对于虚拟制片项目，特别是需要使用 LiveLink VCAM 应用或像素流进行远程监看的场景，此插件是官方推荐的核心解决方案。尽管是 Beta 版，但其架构清晰，功能完整，是构建相关工作流的基础。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore/Tests)