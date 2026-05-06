# Pixel Streaming HMD

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流头显模块 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreamingHMD` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingHMD) | |

---

## 用途

PixelStreamingHMD 是 Pixel Streaming 插件中的头戴显示器（HMD）支持模块。它实现了一个虚拟的 XR 跟踪系统，使得远程浏览器可以通过 WebRTC 接收到的头部运动数据（如旋转、位置、眼间距等）驱动虚幻引擎中的摄像机视角，从而在像素流传输场景中实现 VR/AR 体验。该模块负责：

- 将远程客户端的 HMD 姿态（位置、旋转、视野、瞳距等）映射到虚幻引擎的渲染管线。
- 提供多眼渲染（立体视觉）支持，包括投影矩阵计算。
- 通过控制台变量（CVars）配置 HMD 参数，如视野、眼偏移、投影偏移等。
- 与其他 Pixel Streaming 模块（如 PixelStreamingInput）协作，从网络通道获取输入数据。

## 使用场景

- **云端 VR 游戏/应用**：将 UE 渲染的画面通过 WebRTC 流式传输到 VR 头显（如 HTC Vive、Oculus Quest），用户佩戴头显转动头部时，服务器端的摄像机跟随旋转。
- **远程 XR 协作**：多用户远程观看同一虚拟场景，每个用户拥有独立的 HMD 姿态，通过该模块实现各自视点。
- **移动端 VR 浏览器**：用户通过手机或 VR 眼镜访问网页，点击启动像素流链接，UE 自动适配 HMD 输入。

## 蓝图用法

PixelStreamingHMD 模块本身不直接暴露任何蓝图可调用函数或可设置属性。所有 HMD 参数通过控制台变量（CVars）在 C++ 端配置，或由像素流输入通道驱动。若需要在蓝图中启用/禁用 HMD 或设置参数，请使用 **PixelStreamingBlueprint** 模块中的节点（如 `Enable Pixel Streaming HMD`、`Set Pixel Streaming HMD Transform` 等）。

### 核心控制台变量（可在蓝图用 `Execute Console Command` 节点调用）

| 变量名 | 说明 | 默认值 |
|---|---|---|
| `PixelStreaming.EnableHMD` | 启用/禁用 HMD 渲染 | `false` |
| `PixelStreaming.HMDMatchAspectRatio` | 是否匹配浏览器宽高比 | `true` |
| `PixelStreaming.HMDApplyEyePosition` | 是否应用眼位置偏移 | `true` |
| `PixelStreaming.HMDApplyEyeRotation` | 是否应用眼旋转偏移 | `true` |
| `PixelStreaming.HMDHFOV` | 水平视野（度） | `90.0` |
| `PixelStreaming.HMDVFOV` | 垂直视野（度） | `60.0` |
| `PixelStreaming.HMDIPD` | 瞳距（厘米） | `6.4` |
| `PixelStreaming.HMDProjectionOffsetX` | 投影偏移 X | `0.0` |
| `PixelStreaming.HMDProjectionOffsetY` | 投影偏移 Y | `0.0` |

在蓝图中，可用 `Execute Console Command` 节点来设置这些变量，例如：`r.PixelStreaming.EnableHMD 1`。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingHMD.h"
#include "IPixelStreamingHMDModule.h"
```

### 基本用法

通过模块接口获取 `FPixelStreamingHMD` 实例，然后可以直接设置变换或获取当前姿态。

```cpp
// 获取模块单例
IPixelStreamingHMDModule& HMDModule = IPixelStreamingHMDModule::Get();

// 获取 HMD 对象
FPixelStreamingHMD* HMD = HMDModule.GetPixelStreamingHMD();

// 设置 HMD 变换（例如从远程输入接收到的 Pose）
FTransform NewTransform;
NewTransform.SetLocation(FVector(0, 0, 0));
NewTransform.SetRotation(FQuat::Identity);
HMD->SetTransform(NewTransform);

// 设置双眼视图（左眼、右眼的变换和投影矩阵）
FTransform LeftEye, RightEye;
FMatrix LeftProj, RightProj;
// 从输入数据填充 ...
HMD->SetEyeViews(LeftEye, LeftProj, RightEye, RightProj, HMDTransform);

// 启用立体渲染
HMD->EnableStereo(true);
```

### 进阶用法：自定义 XR 系统后端

`PixelStreamingHMD` 实现了 `IXRTrackingSystem`，可以替换默认的 VR 系统。插件启动时自动注册，可在项目设置中通过 `PixelStreamingXRSystem` 枚举选择后端（HTCVive / Quest / Unknown）。获取当前 XR 系统类型：

```cpp
EPixelStreamingXRSystem ActiveSystem = HMDModule.GetActiveXRSystem();
if (ActiveSystem == EPixelStreamingXRSystem::Quest)
{
    // 应用 Oculus 特定的参数
}
```

## Demo 示例

### 最小可编译示例：加载模块并输出 HMD 信息

**PixelStreamingHMDDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PixelStreamingHMDDemo.generated.h"

UCLASS()
class APixelStreamingHMDDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

**PixelStreamingHMDDemo.cpp**

```cpp
#include "PixelStreamingHMDDemo.h"
#include "IPixelStreamingHMDModule.h"
#include "PixelStreamingHMD.h"
#include "Engine/Engine.h"

void APixelStreamingHMDDemo::BeginPlay()
{
    Super::BeginPlay();

    // 检查模块是否可用
    if (!IPixelStreamingHMDModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("PixelStreamingHMD module is not loaded."));
        return;
    }

    IPixelStreamingHMDModule& HMDModule = IPixelStreamingHMDModule::Get();
    FPixelStreamingHMD* HMD = HMDModule.GetPixelStreamingHMD();
    if (HMD)
    {
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming HMD initialized. System Name: %s"), *HMD->GetSystemName().ToString());

        // 启用立体渲染
        HMD->EnableStereo(true);

        // 输出当前瞳距
        float IPD = HMD->GetInterpupillaryDistance();
        UE_LOG(LogTemp, Log, TEXT("Current IPD: %f"), IPD);

        // 重置方向
        HMD->ResetOrientationAndPosition();
    }
}
```

## 模块依赖

PixelStreamingHMD 依赖的独特模块（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | 提供 `FHeadMountedDisplayBase` 基类和 `IXRTrackingSystem` 接口，使该模块能够注册为虚拟 XR 系统 |
| `RHI` | 用于渲染管线接口（如 `RHICreateTexture`） |
| `RenderCore` | 渲染核心模块，用于场景视图扩展等 |
| `PixelStreaming` | 共享部分公共类型和基础设施（可选，实际上未在头文件中引用，但运行时需要） |

> **说明**：该模块在运行时需要 `PixelStreaming` 主模块提供网络输入，但编译期无硬依赖。若希望独立编译，可忽略最后一项。

## 维护状态

### 近期更新

- 2025-09-30 `4bfe7f55` — Updating the infra scripts to point to the new release branch.
- 2025-09-25 `1fdac7d5` — [PixelCapture, PS, PS2] Fix: MediaCapture could get into a bad state due to use of queues and prayin
- 2025-09-23 `30db91bd` — [PS1, PS2] Fix: Internal signalling server hitting an ensure during creation due FTickableGameObject
- 2025-09-23 `cc062cea` — [PS1, PS2] Fix a crash in editor when setting the streamID on the command line
- 2025-08-29 `32884de4` — Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.

### 维护评价

PixelStreamingHMD 是 Pixel Streaming 插件的一部分，该插件在 UE5 中持续活跃维护。近期（2025 年 9 月）仍有多次修复提交，涉及稳定性、编辑器崩溃等问题，表明开发团队正在积极修复和优化。尽管该模块创建于 2025 年 8 月（约 1 个月前），但已具备基础功能，并随 Pixel Streaming 整体更新而演进。当前版本稳定，推荐用于需要远程 VR 渲染的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingHMD)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingHMD/Private)（模块内自带测试逻辑不明确，建议参考 PixelStreaming 整体测试）