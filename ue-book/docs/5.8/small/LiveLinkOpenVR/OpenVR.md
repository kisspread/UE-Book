# LiveLinkOpenVR

> Live Link plugin for OpenVR (Not supported for native arm64.)

| 属性 | 值 |
|---|---|
| 中文名 | OpenVR LiveLink源 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOpenVR` (Runtime), `OpenVR` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-10 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkOpenVR) | |

## 用途

本插件通过 LiveLink 框架提供对 SteamVR（OpenVR）跟踪数据的多进程消费能力。其核心目的是解决 LiveLinkXR 插件在多进程工作流中暴露的问题，专门为 **LiveLinkHub** 场景设计。

该插件通过内置 OpenVR SDK v1.5.17 直接与 SteamVR 交互，获取 HMD、控制器和通用追踪器的位姿数据，并将其映射为 LiveLink Subject 供其他进程（如 LiveLinkHub）订阅。它还支持将 SteamVR 输入系统（按钮、摇杆等）编组到 `LiveLinkGamepadInputDevice` 角色中，实现控制器输入数据的跨进程传输。

简而言之：当你需要在**另一个进程**（而非运行 VR 的主进程）中使用 SteamVR 追踪数据时，用这个插件代替 LiveLinkXR。

## 使用场景

- 你使用 LiveLinkHub 在独立进程中接收 SteamVR 的 HMD/控制器追踪数据 → 用本插件作为 LiveLink 源
- 你的虚拟制片流程中，渲染进程和追踪数据消费进程分离 → 用本插件跨进程获取 VR 位姿
- 你需要将 SteamVR 控制器的按钮/摇杆输入通过 LiveLink 传到其他应用 → 本插件支持 GamepadInputDevice 角色

> **注意**：仅支持 Win64 平台，不支持 Win64 arm64 架构。插件默认未启用（`EnabledByDefault=false`），需手动在插件管理器中启用。

## 蓝图用法

本插件作为 LiveLink 数据源工作，启用后会自动注册 OpenVR 源。在蓝图中主要通过标准的 LiveLink 节点消费数据，插件本身不暴露额外的 BlueprintCallable 函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 标准 LiveLink Subject 订阅 | 通过 LiveLink 面板订阅 OpenVR 源产生的 Subject | LiveLink 通用框架 |
| Controller Input 映射 | SteamVR 输入自动映射为 GamepadInputDevice 角色 | 内部自动处理 |

### 使用示例（蓝图描述）

1. 在项目设置 → 插件中启用 `LiveLinkOpenVR`
2. 打开 LiveLink 面板（Window → Live Link），在 Sources 中可以看到自动注册的 OpenVR 源
3. 在蓝图中使用 `Evaluate Live Link Frame` 或 `Get Live Link Subject Data` 节点，选择对应的 OpenVR Subject
4. 获取到的 Transform 数据即为 SteamVR 设备的实时位姿

## C++ 用法

本插件的 C++ 接口主要面向内部 LiveLink 框架集成，使用者通常通过 LiveLink 标准接口消费数据。

### 头文件引入

```cpp
#include "LiveLinkOpenVR.h"
```

### 基本用法

通过 LiveLink 框架订阅 OpenVR 源的 Subject 数据：

```cpp
#include "LiveLinkClient.h"
#include "Roles/LiveLinkTransformRole.h"

// 获取 LiveLink 客户端
FLiveLinkClient* LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);

// 枚举所有可用的 Subject
TArray<FLiveLinkSubjectKey> SubjectKeys = LiveLinkClient->GetSubjects(true, true);

// 查找 OpenVR 源的 Subject
for (const FLiveLinkSubjectKey& Key : SubjectKeys)
{
    if (Key.SubjectName.ToString().Contains(TEXT("OpenVR")))
    {
        // 订阅该 Subject 并获取最新的 Transform 数据
        FLiveLinkSubjectFrameData FrameData;
        if (LiveLinkClient->EvaluateFrame_AnyThread(Key.SubjectName, ULiveLinkTransformRole::StaticClass(), FrameData))
        {
            const FTransform& DeviceTransform = FrameData.Transforms[0];
            // 使用设备位姿数据
        }
    }
}
```

### 进阶用法

通过 LiveLink 轮询获取控制器输入（GamepadInputDevice 角色）：

```cpp
// 查询 OpenVR 控制器的输入数据
// SteamVR 输入会被自动编组到 LiveLinkGamepadInputDevice 角色中
#include "Roles/LiveLinkGamepadInputDeviceRole.h"

FLiveLinkSubjectFrameData FrameData;
if (LiveLinkClient->EvaluateFrame_AnyThread(SubjectName, ULiveLinkGamepadInputDeviceRole::StaticClass(), FrameData))
{
    // 解析控制器按钮和摇杆状态
    // 具体的输入映射取决于 SteamVR 的输入配置
}
```

## Demo 示例

一个最小的 OpenVR 追踪数据监听器组件：

```cpp
// OpenVRLiveLinkListener.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LiveLinkClient.h"
#include "OpenVRLiveLinkListener.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UOpenVRLiveLinkListener : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "LiveLink")
    FName SubjectName;

    UPROPERTY(BlueprintReadOnly, Category = "LiveLink")
    FTransform CurrentDevicePose;

    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;
};
```

```cpp
// OpenVRLiveLinkListener.cpp
#include "OpenVRLiveLinkListener.h"
#include "Roles/LiveLinkTransformRole.h"
#include "ILiveLinkClient.h"
#include "ModularFeatures.h"

void UOpenVRLiveLinkListener::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    ILiveLinkClient* Client = IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(
        ILiveLinkClient::ModularFeatureName);
    if (!Client) return;

    FLiveLinkSubjectFrameData FrameData;
    if (Client->EvaluateFrame_AnyThread(SubjectName,
        ULiveLinkTransformRole::StaticClass(), FrameData))
    {
        if (FrameData.Transforms.Num() > 0)
        {
            CurrentDevicePose = FrameData.Transforms[0];
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | LiveLink 核心接口定义 |
| `LiveLink` | LiveLink 客户端运行时（消费端） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis. | 支持按架构粒度控制模块的包含与排除 |
| 2025-05-23 | `f3063039` | LiveLinkOpenVR disabled for arm64 | 在 arm64 架构上禁用该插件 |
| 2024-11-22 | `8ca76f71` | LiveLinkOpenVR: Improved default bindings. | 改进默认输入绑定配置 |
| 2024-09-27 | `9d145f1b` | LiveLinkOpenVR: Marshal SteamVR Input into LiveLinkGamepadInputDevice role. | 将 SteamVR 输入映射到 LiveLinkGamepadInputDevice 角色 |

### 维护评价

该插件创建于 2024 年 9 月，属于较新的实验性插件，约 2 年历史。从 commit 记录来看：

- **功能完善中**：2024 年底到 2025 年持续有功能改进（输入绑定、arm64 兼容性处理）
- **架构适配**：2025 年中完成了平台架构级别的模块管理支持
- **维护活跃**：2026 年 4 月仍有日志宏迁移更新，说明持续维护中
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，API 可能发生变化
- **平台限制**：仅 Win64，明确排除 arm64，OpenVR SDK 不支持原生 ARM 架构

**建议**：如果你的虚拟制片流程确实需要跨进程消费 SteamVR 追踪数据，可以使用此插件，但需注意其实验性状态。如果只需在单进程中使用 VR 追踪，标准的 OpenXR 或 LiveLinkXR 可能更稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkOpenVR)
- [OpenVR SDK](https://github.com/ValveSoftware/openvr)（内嵌 v1.5.17）