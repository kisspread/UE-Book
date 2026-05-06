# Pixel Streaming 2HMD

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流HMD模块 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2HMD` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2HMD) | |

## 用途

PixelStreaming2HMD 是 Pixel Streaming 2 插件中用于处理**头戴显示器（HMD）输入**的模块。它允许远程客户端（如浏览器中的 VR 玩家）将头戴设备的位姿、眼位、投影矩阵等信息通过 WebRTC 传输到 Unreal 引擎，从而实现 VR/XR 画面的像素流推送。该模块实现了 `IXRTrackingSystem`、`IHeadMountedDisplay`、`IStereoRendering` 等接口，使得 Unreal 可以像使用本地头显一样使用外部输入的 HMD 数据。

**解决的问题**：标准的像素流不支持立体渲染（VR），只能发送单眼画面；而 VR 应用需要左右眼分开渲染并正确投影。本模块提供了将远程 HMD 追踪数据注入引擎的桥接机制，并与 PixelStreaming 2 的视频/音频流配合，实现远程 VR 体验。

## 使用场景

- 你正在开发一个 VR 应用（例如建筑漫游、远程协作），需要将画面流到 Web 浏览器，并且希望远程用户佩戴 VR 头显获得完全沉浸式的 3D 体验。
- 你在云端或服务器上运行 Unreal 应用，客户端通过浏览器访问，且客户端使用 VR 头显（如 Quest、Vive）进行交互。
- 你希望将 Unreal 的 VR 输出以自定义方式注入引擎追踪系统，而不依赖本地物理头显。

## 蓝图用法

本模块主要提供 C++ 接口供代码驱动，暂未开放直接调用的蓝图节点。但你可以通过蓝图调用与模块交互的方式获取和设置 HMD 数据：

### 核心函数（通过蓝图节点）

由于 `IPixelStreaming2HMD` 接口不继承自 UObject，无法直接在蓝图调用。但 `IPixelStreaming2HMDModule` 提供了静态访问，可通过 `GetPixelStreaming2HMD()` 返回的指针类型在 C++ 中调用。蓝图开发者应使用自定义 C++ 函数进行桥接。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPixelStreaming2HMDModule` | 获取 HMD 模块单例（C++ 静态函数，可封装为蓝图节点） | `IPixelStreaming2HMDModule` |
| `SetTransform` | 设置 HMD 变换（位置/旋转） | `IPixelStreaming2HMD` |
| `SetEyeViews` | 分别设置左右眼位和投影矩阵 | `IPixelStreaming2HMD` |
| `GetActiveXRSystem` / `SetActiveXRSystem` | 查询/设置当前使用的 XR 系统类型（Quest / HTCVive / Unknown） | `IPixelStreaming2HMDModule` |

### 使用示例（蓝图描述）

1. **在关卡蓝图中获取 HMD 模块**：使用自定义事件或 C++ 函数节点（如 `Get Pixel Streaming 2 HMD Module`）获得模块对象。
2. **设置 HMD 位姿**：连接 `GetPixelStreaming2HMD` → `Set Transform`，传入从网络接收的 `Transform`（来自远程 VR headset 的追踪数据）。
3. **设置双眼视图**：调用 `SetEyeViews`，传入左眼 Transform 与投影矩阵、右眼 Transform 与投影矩阵、以及 HMD 整体的 Transform。这些数据通常从 WebRTC 信令中解析得到。

**注意**：由于网络延迟和帧同步，务必在游戏线程更新 HMD 数据。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2HMDModule.h"
#include "IPixelStreaming2HMD.h"
```

### 基本用法

从网络或数据源获取 HMD 数据后，通过模块接口设置到引擎。

```cpp
// 获取模块实例
IPixelStreaming2HMDModule& HMDModule = IPixelStreaming2HMDModule::Get();

// 获取 HMD 对象
IPixelStreaming2HMD* HMD = HMDModule.GetPixelStreaming2HMD();
if (HMD)
{
    // 设置 HMD 的世界变换（位置+旋转）
    FTransform WorldTransform(FRotator::ZeroRotator, FVector(100.f, 0.f, 50.f));
    HMD->SetTransform(WorldTransform);

    // 设置左右眼视图
    FTransform LeftEye(FRotator(0.f, -2.f, 0.f), FVector(-3.f, 0.f, 0.f));
    FMatrix LeftProj = FReversedZPerspectiveMatrix(90.f, 1.78f, 1.f, 10.f);
    FTransform RightEye(FRotator(0.f, 2.f, 0.f), FVector(3.f, 0.f, 0.f));
    FMatrix RightProj = FReversedZPerspectiveMatrix(90.f, 1.78f, 1.f, 10.f);
    FTransform HMDTransform(FRotator::ZeroRotator, FVector(0.f, 0.f, 0.f));
    HMD->SetEyeViews(LeftEye, LeftProj, RightEye, RightProj, HMDTransform);

    // 可选：设置当前 XR 系统类型（例如来源是 Oculus Quest）
    HMDModule.SetActiveXRSystem(EPixelStreaming2XRSystem::Quest);
}
```
*来源：头文件 `Public/IPixelStreaming2HMD.h`、`Public/IPixelStreaming2HMDModule.h`*

### 进阶用法

与 PixelStreaming 2 的其他模块配合，在接收到 WebRTC 数据通道消息时更新 HMD。

```cpp
// 假设在某个消息处理函数中
void OnHMDDataReceived(const FString& JSONData)
{
    // 解析 JSON 得到左右眼 Transform 和投影（省略解析细节）
    FTransform LeftEye = /*...*/;
    FMatrix LeftProj = /*...*/;
    FTransform RightEye = /*...*/;
    FMatrix RightProj = /*...*/;
    FTransform HMDTransform = /*...*/;

    if (IPixelStreaming2HMDModule::IsAvailable())
    {
        IPixelStreaming2HMDModule& Module = IPixelStreaming2HMDModule::Get();
        IPixelStreaming2HMD* HMD = Module.GetPixelStreaming2HMD();
        if (HMD)
        {
            HMD->SetTransform(HMDTransform);
            HMD->SetEyeViews(LeftEye, LeftProj, RightEye, RightProj, HMDTransform);
        }
    }
}
```

**注意**：所有 `Set` 函数应在游戏线程调用，如 `GameThread`。

## Demo 示例

一个简单的 `AHMDDataSourceActor`，演示如何在 Actor 中设置 HMD 数据。

### PixelStreaming2HMDDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PixelStreaming2HMDDemo.generated.h"

UCLASS()
class APixelStreaming2HMDDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "PixelStreaming2HMD")
    void UpdateHMD(const FTransform& InHMDTransform,
                   const FTransform& InLeftEye,
                   const FMatrix& InLeftProj,
                   const FTransform& InRightEye,
                   const FMatrix& InRightProj);
};
```

### PixelStreaming2HMDDemo.cpp

```cpp
#include "PixelStreaming2HMDDemo.h"
#include "IPixelStreaming2HMDModule.h"
#include "IPixelStreaming2HMD.h"

void APixelStreaming2HMDDemo::BeginPlay()
{
    Super::BeginPlay();
    // 示例：在开始时设置默认 HMD 数据
    FTransform DefaultHMD(FVector(0.f, 0.f, 100.f));
    FTransform DefaultLeft(FVector(-3.f, 0.f, 0.f));
    FMatrix DefaultProj = FReversedZPerspectiveMatrix(90.f, 1.78f, 1.f, 10.f);
    UpdateHMD(DefaultHMD, DefaultLeft, DefaultProj, DefaultLeft, DefaultProj);
}

void APixelStreaming2HMDDemo::UpdateHMD(const FTransform& InHMDTransform,
                                         const FTransform& InLeftEye,
                                         const FMatrix& InLeftProj,
                                         const FTransform& InRightEye,
                                         const FMatrix& InRightProj)
{
    if (IPixelStreaming2HMDModule::IsAvailable())
    {
        IPixelStreaming2HMDModule& Module = IPixelStreaming2HMDModule::Get();
        IPixelStreaming2HMD* HMD = Module.GetPixelStreaming2HMD();
        if (HMD)
        {
            HMD->SetTransform(InHMDTransform);
            HMD->SetEyeViews(InLeftEye, InLeftProj, InRightEye, InRightProj, InHMDTransform);
        }
    }
}
```

在使用时，将该 Actor 放置到关卡中，并可通过蓝图调用 `UpdateHMD` 以响应远程数据。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | 提供 XR 系统基类 `FHeadMountedDisplayBase` 和 `IHeadMountedDisplay` 接口 |
| `Renderer` | 提供 `ISceneViewExtension` 接口用于扩展场景渲染 |
| `RHI` | 提供图形接口（如 `FMatrix` 运算） |
| `PixelStreaming2Core` | 提供 PixelStreaming 2 核心基础设施（可能用于数据通道） |

注意：`Core`、`CoreUObject`、`Engine` 等标准模块在本模块中默认依赖，未列出。

## 维护状态

| 日期 | 提交哈希 | commit 解读 |
|---|---|---|
| 2026-01-23 | a9928676 | [NVCodecs, PixelStreaming2] Fixes: 修复与 NVIDIA 编码器的兼容性问题 |
| 2025-11-18 | d7a4d160 | [AVCodecs, PixelStreaming2] Fixes: 修复音视频编解码相关问题 |
| 2025-10-28 | b1db9444 | [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread 修复线程死锁 |
| 2025-10-17 | 5c2f039d | [PS2] Fix: Non-functional public API 修复公开接口失效问题 |
| 2025-10-13 | 0de4d465 | [PS2] Bug Fixes for 5.7 初始版本 Bug 修复 |

### 维护评价

PixelStreaming2HMD 模块作为 Pixel Streaming 2 插件的一部分，自 2025 年 10 月创建以来持续活跃维护，最近一次更新为 2026 年 1 月。提交以修复问题和稳定性优化为主，功能基本稳定。模块非常年轻且仍处于积极开发期，推荐在需要远程 VR 的项目中使用。无已知废弃风险。

## 相关链接

- [源码 (PixelStreaming2 插件根目录)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档 (Pixel Streaming)](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例 (PixelStreaming2 测试目录)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Tests)