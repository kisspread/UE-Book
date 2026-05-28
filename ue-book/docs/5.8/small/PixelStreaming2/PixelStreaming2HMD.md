# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Unreal Engine 的下一代像素流送插件，旨在将引擎的实时渲染画面和音频通过 WebRTC 协议低延迟地传输到网页浏览器或其他 WebRTC 兼容客户端。它本质上是一个完整的远程渲染与交互解决方案，允许用户无需在本地安装 UE 应用即可体验高保真、交互式的 3D 内容。

该插件的存在解决了以下核心问题：
1.  **云游戏与远程渲染**：将渲染负载从客户端转移到服务器，让移动设备、低配置电脑也能运行高品质的 UE 应用。
2.  **无需安装的即时体验**：用户只需一个浏览器链接即可访问复杂的 UE 应用，极大降低了分发和体验门槛。
3.  **实时交互**：不仅传输音视频，还支持将用户的键盘、鼠标、触摸等输入事件回传至服务器，实现双向交互。
4.  **跨平台**：基于 WebRTC 标准，理论上支持所有现代浏览器。
5.  **XR 集成**：通过专门的 `PixelStreaming2HMD` 模块，支持将流送内容适配至 VR/AR 头显，实现远程 XR 体验。

## 使用场景

-   **云游戏平台**：你需要构建一个云游戏服务，让用户在网页上就能玩到 UE 开发的大型 3A 游戏。
-   **虚拟展示与产品配置器**：你开发了一款高端的汽车或建筑可视化应用，希望通过网页链接让客户进行实时查看和交互，无需下载庞大的客户端。
-   **远程协作与评审**：团队需要远程审阅 UE 项目场景或动画，评审者可以通过浏览器实时查看并控制视角。
-   **XR 应用（远程）**：你希望将 UE 内容流送到移动 VR 设备（如 Quest）或 AR 眼镜上，作为远程渲染方案，减轻设备本身的计算压力。

## 蓝图用法

Pixel Streaming 2 的核心功能通常通过配置文件和启动参数进行设置，而非直接的蓝图节点。其主要接口在 C++ 层提供。对于 HMD 集成，模块暴露了 `IPixelStreaming2HMD` 接口，但通常由引擎系统内部调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *（无公开蓝图节点）* | 该模块主要功能通过配置和C++接口控制。 | - |

### 使用示例（蓝图描述）

由于该模块主要处理底层的视频编码、网络传输和 HMD 适配，不提供可视化的蓝图节点。用户通常通过以下方式配置和启动像素流送：
1.  在 `DefaultEngine.ini` 中配置信令服务器地址等参数。
2.  在启动 UE 应用时，使用 `-PixelStreamingURL`, `-RenderOffScreen` 等命令行参数。
3.  通过 C++ 代码在应用启动时设置流送相关选项。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2HMDModule.h"
#include "IPixelStreaming2HMD.h"
```

### 基本用法

获取 Pixel Streaming HMD 模块的单例并检查其可用性。来源文件：`Public/IPixelStreaming2HMDModule.h`。
```cpp
// 获取模块单例
IPixelStreaming2HMDModule& HMDModule = IPixelStreaming2HMDModule::Get();

// 检查模块是否已加载
if (IPixelStreaming2HMDModule::IsAvailable())
{
    // 获取 HMD 对象
    IPixelStreaming2HMD* HMD = HMDModule.GetPixelStreaming2HMD();
    if (HMD)
    {
        // 使用 HMD 接口...
    }
}
```

### 进阶用法

设置 HMD 的变换和眼视图信息。这通常由上游 XR 系统或输入处理模块调用，以更新远程客户端的姿态。来源文件：`Public/IPixelStreaming2HMD.h`。
```cpp
if (IPixelStreaming2HMD* HMD = /* 获取 HMD 对象 */)
{
    // 设置 HMD 整体变换（位置和旋转）
    FTransform HMDTransform;
    // ... 设置变换数据 ...
    HMD->SetTransform(HMDTransform);

    // 设置左右眼的视图变换和投影矩阵
    FTransform LeftEyeTransform;
    FMatrix LeftProjectionMatrix;
    FTransform RightEyeTransform;
    FMatrix RightProjectionMatrix;
    // ... 从 XR 系统获取或计算双眼数据 ...
    HMD->SetEyeViews(LeftEyeTransform, LeftProjectionMatrix, RightEyeTransform, RightProjectionMatrix, HMDTransform);
}
```

## Demo 示例

一个展示如何初始化 HMD 模块并设置基础数据的最小示例。

**PixelStreaming2HMDDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "IPixelStreaming2HMDModule.h"
#include "IPixelStreaming2HMD.h"

class FPixelStreaming2HMDDemo
{
public:
    void Init();
    void Update();

private:
    IPixelStreaming2HMD* CachedHMD = nullptr;
    bool bInitialized = false;
};
```

**PixelStreaming2HMDDemo.cpp**
```cpp
#include "PixelStreaming2HMDDemo.h"
#include "Engine/Engine.h" // 用于获取引擎实例

void FPixelStreaming2HMDDemo::Init()
{
    if (IPixelStreaming2HMDModule::IsAvailable())
    {
        IPixelStreaming2HMDModule& Module = IPixelStreaming2HMDModule::Get();
        CachedHMD = Module.GetPixelStreaming2HMD();
        bInitialized = (CachedHMD != nullptr);
    }
}

void FPixelStreaming2HMDDemo::Update()
{
    if (!bInitialized || !CachedHMD)
    {
        return;
    }

    // 模拟一个简单的 HMD 位于 (0, 170, 0) 的站立姿态
    const float WorldToMeters = 100.0f;
    FTransform HMDTransform(FRotator(0, 0, 0), FVector(0, 170.0f / WorldToMeters, 0));
    CachedHMD->SetTransform(HMDTransform);

    // 模拟左右眼视图（简化：无旋转，投影矩阵使用标准透视）
    FTransform EyeTransform = FTransform::Identity; // 假设眼位在HMD原点
    FMatrix ProjectionMatrix = FReversedZPerspectiveMatrix(
        FMath::DegreesToRadians(90.0f), // 水平视场角
        16.0f / 9.0f,                  // 宽高比
        1.0f,                          // 近平面
        10000.0f                       // 远平面
    );
    CachedHMD->SetEyeViews(EyeTransform, ProjectionMatrix, EyeTransform, ProjectionMatrix, HMDTransform);
}
```

## 模块依赖

该插件自身模块依赖关系复杂，但对使用者而言，主要关注其提供的接口。

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | 用于通过 Vulkan 进行 GPU 编码（如果使用该编码器）。 |
| **无特殊依赖（仅标准 Core/Engine/Slate 等）** | 使用 `IPixelStreaming2HMD` 等公共接口时，无需额外链接特殊模块。 |

*注意：`PixelStreaming2HMD` 模块内部依赖于 `PixelStreaming2Core` 等其他插件模块，但这些是插件内部的构建依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量转浮点产生的警告代码 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将多个 VP 资产移至不同资产分类并进行了迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的范围枚举可能导致垃圾输出的问题 |

### 维护评价

-   **创建时间**：插件于 2024 年 9 月创建，相对较新。
-   **更新频率**：最近（2026年5月）有连续的提交，表明仍在**活跃维护**中。更新内容包括功能修复、代码清理和与虚拟制作工作流的集成。
-   **活跃度**：基于近期提交记录，该项目处于活跃开发状态，不断进行优化和问题修复。
-   **已知限制**：作为 `EnabledByDefault=false` 的插件，表明它可能需要额外的服务器端组件（如信令服务器）配合使用，且配置相对复杂，不适合开箱即用。
-   **推荐**：**推荐使用**。对于需要构建像素流送、云游戏或远程 XR 应用的团队，这是 Epic Games 提供的官方解决方案，正处于积极维护中。应关注其官方文档以获取详细的集成和配置指南。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
-   [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests) *(路径为推测，请根据实际情况查找)*