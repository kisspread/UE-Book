# LiveLinkOpenVR

> Live Link plugin for OpenVR (Not supported for native arm64.)

| 属性 | 值 |
|---|---|
| 中文名 | OpenVR 实时链接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOpenVR` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkOpenVR) | |

## 用途

该插件将 OpenVR（SteamVR）硬件的追踪数据注入到 Unreal Engine 的 LiveLink 框架中。它创建一个 LiveLink 源，能够实时读取 HMD、控制器、追踪器（Tracker Puck）以及基站（Tracking Reference）的位置、旋转和设备状态，并将这些数据以 LiveLink 主题（Subject）的形式广播出去。主要面向虚拟制作、混合现实和 LiveLinkHub 场景，允许 VR 硬件（如 Vive Tracker、Index 控制器）直接作为虚拟角色、相机或物体的驱动输入。

插件还支持将通过 OpenVR 输入（如按钮、摇杆）映射为 LiveLink 游戏手柄输入设备角色（`LiveLinkGamepadInputDevice`），从而实现 VR 控制器与游戏手柄输入系统的兼容。

## 使用场景

- **虚拟制作追踪**：在摄影棚中使用 SteamVR 基站和 Vive Tracker 追踪道具、相机位置，通过 LiveLink 将追踪数据实时同步到 UE 场景中的虚拟物体。
- **LiveLinkHub 集成**：设计用于 LiveLinkHub，可在其中添加 OpenVR 源，集中管理多个 VR 设备的追踪数据。
- **VR 控制器输入映射**：将 VR 控制器的扳机、摇杆等输入映射为标准的 LiveLink 游戏手柄输入，方便在蓝图中使用传统的输入节点处理 VR 交互。
- **混合现实演示**：将 HMD 或手持控制器作为 LiveLink 主体，驱动虚拟角色的手部或头部。

## 蓝图用法

该插件未暴露 BlueprintCallable 函数，其主要交互方式是通过 LiveLink 编辑器面板创建源，然后使用标准的 LiveLink 蓝图中操作主题和帧数据。

### 创建 LiveLinkOpenVR 源

在编辑器中，打开 **Window → Live Link** 面板。点击 **+ Source**，选择 **LiveLinkOpenVR**。此时会弹出连接设置面板，可配置以下选项：

| 参数 | 说明 |
|---|---|
| `LocalUpdateRateInHz` | 追踪数据读取频率（1~1000 Hz，默认 60） |
| `bTrackTrackers` | 是否跟踪所有 Tracker 设备（如 Vive Tracker） |
| `bTrackTrackingReferences` | 是否跟踪基站等参考设备 |
| `bTrackControllers` | 是否跟踪所有控制器（默认关闭） |
| `bTrackHMDs` | 是否跟踪头戴显示器（默认关闭） |

连接后，每个被追踪的设备将成为 LiveLink 的一个主题（Subject），名称格式为 `OpenVR_<DeviceClass>_<Index>`（如 `OpenVR_Controller_0`、`OpenVR_Tracker_1`）。

### 在蓝图中使用追踪数据

使用标准的 **LiveLink** 蓝图节点：

- **获取 LiveLink 主题数据**：`Get Live Link Subject Frame Data (Transform)` 或 `Get Live Link Subject Frame Data (Transform Array)` 来获取设备的位移和旋转。
- **获取游戏手柄输入**：如果开启了控制器追踪，可以使用 `Get Live Link Subject Frame Data (Gamepad Input Device)` 获取摇杆、按钮等输入。

### 使用示例（蓝图描述）

1. 确认 `LiveLink` 源已连接且主题已出现。
2. 在关卡蓝图中获取主题句柄：使用 `Get Live Link Subject` 节点，指定主题名称（如 `OpenVR_Tracker_0`）。
3. 将主题数据应用到 Actor：使用 `Apply Live Link Transform to Actor` 节点（或手动用 `Set Actor Transform` 将帧数据中的变换赋值）。
4. 对于控制器输入：使用 `Get Live Link Subject Frame Data (Gamepad Input Device)` 节点，输出可用于驱动角色动画或触发事件。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkOpenVRModule.h"      // 模块访问
#include "LiveLinkOpenVRSource.h"      // 源类
#include "LiveLinkOpenVRTypes.h"       // 设置结构体
```

### 基本用法：创建并启动一个 OpenVR 源

```cpp
// 构造连接设置
FLiveLinkOpenVRConnectionSettings ConnectionSettings;
ConnectionSettings.bTrackTrackers  = true;
ConnectionSettings.bTrackHMDs     = false;
ConnectionSettings.bTrackControllers = true;
ConnectionSettings.CommonSettings.LocalUpdateRateInHz = 60;

// 创建源
TSharedPtr<ILiveLinkSource> OpenVRSrc = MakeShared<FLiveLinkOpenVRSource>(ConnectionSettings);

// 假设你已有一个 ILiveLinkClient 指针（例如从 FLiveLinkModule 获取）
ILiveLinkClient* LiveLinkClient = ...;
FGuid SourceGuid;
LiveLinkClient->AddSource(OpenVRSrc, SourceGuid);
```

### 进阶用法：管理源设置

`ULiveLinkOpenVRSourceSettings` 继承了 `ULiveLinkSourceSettings`，可以在运行时通过 `FLiveLinkOpenVRSource::InitializeSettings()` 修改。但建议通过编辑器 UI 或直接修改设置对象的属性。

获取 VR 系统指针（用于高级操作）：

```cpp
FLiveLinkOpenVRModule& Module = FLiveLinkOpenVRModule::Get();
vr::IVRSystem* VrSystem = Module.GetVrSystem();
if (VrSystem)
{
    // 使用 SteamVR API 直接查询设备属性等
}
```

### 源工厂方式（推荐）

通常使用 `ULiveLinkOpenVRSourceFactory` 创建源，与编辑器添加源的行为一致：

```cpp
void CreateOpenVRSource(ILiveLinkClient* Client, FLiveLinkOpenVRConnectionSettings Settings)
{
    // 使用工厂（需要提前实例化或通过 CDO）
    ULiveLinkOpenVRSourceFactory* Factory = NewObject<ULiveLinkOpenVRSourceFactory>();
    Factory->CreateSourceFromSettings(Settings, FOnLiveLinkSourceCreated::CreateLambda(
        [Client](TSharedPtr<ILiveLinkSource> Source, FString ConnectionString)
        {
            FGuid Guid;
            Client->AddSource(Source, Guid);
        }
    ));
}
```

## Demo 示例

以下是一个最小 C++ 示例，展示如何通过控制台命令创建一个 LiveLinkOpenVR 源。

### LiveLinkOpenVRDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkOpenVRTypes.h"

UCLASS()
class ALiveLinkOpenVRDemoActor : public AActor
{
    GENERATED_BODY()

public:
    UFUNCTION(Exec)
    void CreateOpenVRLink();
};
```

### LiveLinkOpenVRDemo.cpp

```cpp
#include "LiveLinkOpenVRDemo.h"
#include "LiveLinkOpenVRSource.h"
#include "ILiveLinkClient.h"
#include "Modules/ModuleManager.h"

void ALiveLinkOpenVRDemoActor::CreateOpenVRLink()
{
    FLiveLinkOpenVRConnectionSettings Settings;
    Settings.bTrackTrackers = true;
    Settings.bTrackControllers = false;
    Settings.bTrackHMDs = false;
    Settings.CommonSettings.LocalUpdateRateInHz = 30;

    TSharedPtr<ILiveLinkSource> Source = MakeShared<FLiveLinkOpenVRSource>(Settings);

    // 获取 LiveLink 客户端（假设存在）
    // 注意：避免在 GameThread 之外使用，此处仅为演示
    IModularFeatures::Get().LockModularFeature("LiveLinkClient");
    ILiveLinkClient* LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>("LiveLinkClient");
    FGuid Guid;
    LiveLinkClient->AddSource(Source, Guid);
    IModularFeatures::Get().UnlockModularFeature("LiveLinkClient");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | LiveLink 源接口和客户端通信 |
| `OpenVR`（第三方） | SteamVR 运行时库，提供 VR 系统访问 |

此外，需要项目支持 `Engine/Plugins/Experimental` 且目标平台为 `Win64`（不支持原生 Arm64）。

**略过的常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, PropertyEditor, DeveloperSettings 等。

## 维护状态

### 近期更新

- 2025-06-03 `0a44e4b8` Plugin modules can be included & excluded on a per-architecture basis.（引擎架构更新）
- 2025-05-23 `f3063039` LiveLinkOpenVR disabled for arm64（禁用 Arm64 支持）
- 2024-11-22 `8ca76f71` LiveLinkOpenVR: Improved default bindings.（改进默认绑定）
- 2024-09-27 `9d145f1b` LiveLinkOpenVR: Marshal SteamVR Input into LiveLinkGamepadInputDevice role.（支持 SteamVR 输入映射为游戏手柄输入设备）
- 2024-09-10 `6d256cca` Add LiveLinkOpenVR plugin, intended for use in LiveLinkHub.（初始添加）

### 维护评价

该插件于 2024 年 9 月创建，主要面向 LiveLinkHub 场景。2025 年 5 月仍有实质性更新（禁用 arm64，改进绑定），说明团队仍在维护。目前功能基本完整，支持追踪器和控制器输入映射。**注意**：插件被标记为实验性（`IsExperimentalVersion=true`），且默认未启用，使用时需手动启用并仅在 Win64 上运行。已知限制：不支持原生 arm64（Apple Silicon）。整体推荐用于需要实时 OpenVR 追踪数据的项目中，但建议保持对引擎更新的关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkOpenVR)
- 官方文档：无（DocsURL 为空）
- 测试用例：无（未提供）