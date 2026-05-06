# LiveLinkOpenVR

> Live Link plugin for OpenVR (Not supported for native arm64.)

| 属性 | 值 |
|---|---|
| 中文名 | OpenVR 直播链接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOpenVR` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkOpenVR) | |

## 用途

LiveLinkOpenVR 将 SteamVR（OpenVR）头戴式显示器（HMD）及控制器等追踪设备的实时位姿、输入数据，通过 Unreal Engine 的 [LiveLink](https://docs.unrealengine.com/5.7/zh-CN/live-link-overview/) 框架传入引擎。使得 VR 设备可以像其他 LiveLink 来源（如动捕系统、面部捕捉）一样，作为动画、摄像机、虚拟片场的实时数据源。

该插件解决了以下问题：

- 在虚拟制作（Virtual Production）工作流中，需要将物理 VR 设备的追踪数据无缝融入 UE 的动画蓝图或场景摄像机。
- 需要将 SteamVR 的控制器按钮、摇杆等输入映射为 LiveLink 的 Gamepad Input Device 角色，从而在 UE 中通过绑定使用。
- 配合 LiveLinkHub 实现多源数据混合与重定向。

## 使用场景

- 你正在搭建一个 VR 虚拟摄像机系统，希望用 VR 控制器在实时场景中操控摄像机的轨道和角度。
- 你需要在虚拟片场内让演员佩戴的 VR 追踪器（如 HTC Vive Tracker）驱动虚拟角色的根骨骼或身体位置。
- 你想要将 SteamVR 控制器的扳机、触摸板等输入作为 LiveLink 动画曲线的触发条件。

## 蓝图用法

> **重要**：LiveLinkOpenVR 本身不暴露直接的蓝图调用节点。它的功能通过标准的 LiveLink 机制提供：启用插件后，在 LiveLink 面板中选择 OpenVR 作为 Source，即可接收追踪数据。以下节点属于 LiveLink 通用节点，可用于处理 OpenVR 数据。

### 获取 OpenVR Subject 数据

在 LiveLink 中，每个追踪设备（头显、左手控制器、右手控制器等）会自动注册为一个 Subject（主题）。通过以下方式获取其位姿：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Subject Data` | 获取指定 Subject 的最新数据（位置、旋转、速度等） | `ULiveLinkBlueprintLibrary` |
| `Get Subject Frames` | 获取指定 Subject 的多个帧数据（可指定时间范围） | `ULiveLinkBlueprintLibrary` |
| `Get Subject Name` | 获取所有活跃的 OpenVR Subject 的名称列表 | `ULiveLinkBlueprintLibrary` |

### 处理输入设备

OpenVR 控制器的按钮、摇杆状态被映射为 `LiveLinkGamepadInputDevice` 角色。你可以使用 LiveLink 的 Gamepad Input 相关节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Gamepad Input Device Data` | 从 LiveLink Subject 数据中提取游戏手柄输入（按钮、轴） | `ULiveLinkBlueprintLibrary` |
| `Is Gamepad Button Pressed` | 检查指定按钮是否被按下 | `ULiveLinkBlueprintLibrary` |
| `Get Gamepad Analog Value` | 获取指定模拟轴（摇杆、扳机）的值 | `ULiveLinkBlueprintLibrary` |

### 使用示例（蓝图描述）

1. **驱动摄像机位置**：在关卡蓝图中，每 Tick 调用 `Get Subject Data`，Subject 名称填写 `"LeftController"`（或 `"RightController"`），将返回的 `Transform` 连接到摄像机（或弹簧臂）的 `Set World Transform`。
2. **映射按钮事件**：在动画蓝图中，使用 `Get Gamepad Input Device Data` 从指定 Subject 获取输入数据，再通过 `Is Gamepad Button Pressed` 判断按钮状态，驱动混合空间或蒙太奇播放。

## C++ 用法

> **注意**：以下示例基于公开的 LiveLink 框架 API 与 git 历史中的测试代码风格推测。实际使用时请参照插件源码（`Source/LiveLinkOpenVR/Private/`）。

### 头文件引入

```cpp
#include "LiveLinkOpenVRSourceFactory.h"  // 工厂类头
#include "LiveLinkClient.h"                // LiveLink 客户端
#include "Features/IModularFeatures.h"     // 用于注册 Source
```

### 基本用法：获取 OpenVR 数据源

```cpp
// 通过模块特征获取 LiveLink 客户端
ILiveLinkClient* LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
if (LiveLinkClient)
{
    // 创建一个 OpenVR Source（通常在插件初始化时自动创建）
    // 或者通过 LiveLinkHub 手动添加
    TSharedPtr<ILiveLinkSource> OpenVRSource = MakeShared<FLiveLinkOpenVRSource>();
    LiveLinkClient->AddSource(OpenVRSource);
}
```

### 读取 Subject 数据

```cpp
// 假设已存在的 OpenVR Subject 名称
FLiveLinkSubjectKey SubjectKey(TEXT("OpenVR"), TEXT("HMD")); // SubjectName 例如 "HMD", "LeftController"

FLiveLinkSubjectFrameData FrameData;
if (LiveLinkClient->EvaluateFrame(SubjectKey, ULiveLinkTypes::StaticStruct(), FrameData))
{
    // 获取位姿
    FLiveLinkBaseData& BaseData = FrameData;
    const FTransform& Pose = BaseData.Transforms[0];
    // 获取输入（如果是控制器）
    const FLiveLinkGamepadInputDeviceFrameData* GamepadData = FrameData.GamepadInputDevice.GetPtr<FLiveLinkGamepadInputDeviceFrameData>();
    if (GamepadData)
    {
        float AxisX = GamepadData->LeftAnalogX;
        bool bAPressed = GamepadData->IsButtonPressed(EGamepadButton::A);
    }
}
```

### 进阶用法：自定义角色绑定

可通过 LiveLink 的 `FLiveLinkSubjectFrameData` 扩展自定义处理，或创建 `ULiveLinkRole` 子类接收数据。但 OpenVR 默认使用 `LiveLinkAnimationRole`（位姿）和 `LiveLinkGamepadInputDeviceRole`（输入）。

## Demo 示例

以下为一个最小 C++ Actor 示例，用于在运行时监听 HMD 数据。

**`MyOpenVRListener.h`**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkClient.h"
#include "MyOpenVRListener.generated.h"

UCLASS()
class AMyOpenVRListener : public AActor
{
    GENERATED_BODY()

public:
    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

private:
    ILiveLinkClient* LiveLinkClient = nullptr;
};
```

**`MyOpenVRListener.cpp`**

```cpp
#include "MyOpenVRListener.h"
#include "Features/IModularFeatures.h"
#include "LiveLinkDataCache.h"
#include "Roles/LiveLinkAnimationRole.h"

void AMyOpenVRListener::BeginPlay()
{
    Super::BeginPlay();
    // 获取 LiveLink 客户端（插件需启用）
    LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
}

void AMyOpenVRListener::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (LiveLinkClient == nullptr) return;

    FLiveLinkSubjectKey SubjectKey(TEXT("OpenVR"), TEXT("HMD"));
    FLiveLinkSubjectFrameData FrameData;
    if (LiveLinkClient->EvaluateFrame(SubjectKey, ULiveLinkAnimationRole::StaticClass(), FrameData))
    {
        const FLiveLinkAnimationFrameData* AnimData = FrameData.AnimationData.GetPtr<FLiveLinkAnimationFrameData>();
        if (AnimData && AnimData->Transforms.Num() > 0)
        {
            FTransform HMDPose = AnimData->Transforms[0];
            // 将 HMD 位置应用到 Actor 自身
            SetActorTransform(HMDPose);
        }
    }
}
```

## 模块依赖

### LiveLinkOpenVR 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 LiveLink 框架 |
| `OpenVR` | 第三方库，封装 SteamVR API |
| `LiveLinkGamepadInputDevice` | 将 OpenVR 输入映射为游戏手柄输入角色（推测） |

### 第三方库 OpenVR 模块（外部）

OpenVR 库本身无需其他 UE 模块依赖，它存放于 `Source/ThirdParty/OpenVR`，编译时自动链接 OpenVR SDK（版本 `1.5.17`）。

若要在 C++ 项目中直接调用 OpenVR API（不建议，应通过 LiveLinkOpenVR 模块），需手动包含头文件：

```cpp
#include "openvr.h"
```

并链接对应平台的动态库（在插件内部已处理）。

## 维护状态

### 近期更新

- 2025-06-03 `0a44e4b8` — Plugin modules can be included & excluded on a per-architecture basis.
- 2025-05-23 `f3063039` — LiveLinkOpenVR disabled for arm64
- 2024-11-22 `8ca76f71` — LiveLinkOpenVR: Improved default bindings.
- 2024-09-27 `9d145f1b` — LiveLinkOpenVR: Marshal SteamVR Input into LiveLinkGamepadInputDevice role.
- 2024-09-10 `6d256cca` — Add LiveLinkOpenVR plugin, intended for use in LiveLinkHub.

### 维护评价

- **创建时间**：2024-09-10，距今约 1 年，属于较新插件。
- **近期更新**：截止 2025-06-03 仍有活跃提交，最近一次是体系结构排除支持，属于编译配置调整；2024-11 和 09 月有功能性更新（默认绑定、输入角色映射）。
- **活跃度**：整体活跃，属于维护中的实验性插件。
- **已知限制**：标注为实验性，禁用 arm64 原生支持，仅支持 Win64。
- **推荐使用**：若需要将 SteamVR 数据集成到 LiveLink 工作流（尤其是 LiveLinkHub），该插件是最简洁的方案。注意其实验性状态，建议在正式项目前进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkOpenVR)
- [LiveLink 官方文档](https://docs.unrealengine.com/5.7/zh-CN/live-link-overview/)
- [OpenVR SDK 文档](https://github.com/ValveSoftware/openvr)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkOpenVR/Source/LiveLinkOpenVR/Private/Tests)（可能位于 `Private/Tests` 目录，但未在提供信息中确认）