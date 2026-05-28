# Pixel Streaming 2 HMD

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送HMD模块 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2HMD` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

`PixelStreaming2HMD` 是 `PixelStreaming2` 插件的一个子模块，专门为支持远程渲染的虚拟现实 (VR) / 扩展现实 (XR) 应用设计。其主要功能是**将本地 HMD（头戴显示器，如 VR 头显）的输入与远程的 Pixel Streaming 会话桥接起来**。

当用户在浏览器中访问通过 Pixel Streaming 传输的 Unreal Engine 应用时，如果该用户佩戴了本地 VR 设备（如 HTC Vive 或 Oculus Quest），`PixelStreaming2HMD` 模块负责：
1.  将本地 HMD 的位姿（位置、旋转）数据实时同步到远程的 Unreal Engine 实例。
2.  接收并应用来自远程实例的立体渲染视图参数（左/右眼视图矩阵、投影矩阵）。
3.  使远程引擎实例像处理本地 HMD 一样处理输入和渲染输出，从而实现远程的、高保真的 VR 体验。

它解决了 Pixel Streaming 场景下，如何让远程客户端的 VR 头显与云或另一台机器上的引擎无缝交互的问题。

## 使用场景

-  你需要通过网络（如互联网）为用户提供一个高配、高质量的 VR 应用体验，而用户只拥有一个消费级 VR 头显和一台普通电脑。
-  你正在开发一个云端 VR 渲染农场或远程工作站解决方案，需要将 Unreal Engine 的渲染结果流式传输到用户的 VR 设备。
-  你在构建一个虚拟制作 (Virtual Production) 系统，需要通过网络远程控制和查看 VR 摄像机视角。

## 蓝图用法

此模块主要提供 C++ 接口，蓝图中通常不直接使用，而是通过 `PixelStreaming2` 插件的整体流程间接生效。若需在蓝图中查询 HMD 状态，可使用模块接口的静态方法。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IPixelStreaming2HMDModule::Get` | 获取 Pixel Streaming HMD 模块的单例。 | `IPixelStreaming2HMDModule` |
| `IPixelStreaming2HMDModule::IsAvailable` | 检查 Pixel Streaming HMD 模块是否已加载。 | `IPixelStreaming2HMDModule` |
| `IPixelStreaming2HMDModule::GetPixelStreaming2HMD` | 获取 Pixel Streaming HMD 对象实例。 | `IPixelStreaming2HMDModule` |
| `IPixelStreaming2HMDModule::GetActiveXRSystem` | 获取当前激活的 XR 系统类型（如 HTC Vive, Quest）。 | `IPixelStreaming2HMDModule` |
| `IPixelStreaming2HMDModule::SetActiveXRSystem` | 设置当前激活的 XR 系统类型。 | `IPixelStreaming2HMDModule` |

### 使用示例（蓝图描述）

1.  **检查 HMD 是否可用**：
    - 在蓝图中，首先调用 `IPixelStreaming2HMDModule::IsAvailable`，判断返回的布尔值。如果为 `true`，说明 Pixel Streaming HMD 模块已加载。
2.  **获取并设置 XR 系统**：
    - 调用 `IPixelStreaming2HMDModule::Get` 获取模块接口。
    - 使用该接口调用 `GetActiveXRSystem` 来查询当前系统（例如，返回 `EPixelStreaming2XRSystem::Quest`）。
    - 或者调用 `SetActiveXRSystem` 来明确指定远程用户使用的设备类型，以便引擎进行针对性优化。

## C++ 用法

### 头文件引入

```cpp
// 访问模块接口
#include "IPixelStreaming2HMDModule.h"
// 访问 HMD 核心接口（通常由上层框架使用）
#include "IPixelStreaming2HMD.h"
// 枚举类型
#include "PixelStreaming2HMDEnums.h"
```

### 基本用法

1.  **检查模块可用性并获取接口**
    (来源: `Public/IPixelStreaming2HMDModule.h`)

    ```cpp
    if (IPixelStreaming2HMDModule::IsAvailable())
    {
        // 获取模块单例
        IPixelStreaming2HMDModule& HMDModule = IPixelStreaming2HMDModule::Get();
        
        // 获取活跃的 XR 系统类型
        EPixelStreaming2XRSystem ActiveSystem = HMDModule.GetActiveXRSystem();
        
        // 如果是为 Quest 设备优化，可以设置它
        if (ActiveSystem != EPixelStreaming2XRSystem::Quest)
        {
            HMDModule.SetActiveXRSystem(EPixelStreaming2XRSystem::Quest);
        }
        
        // 获取 HMD 对象（通常由 Pixel Streaming 框架内部使用）
        IPixelStreaming2HMD* HMDInterface = HMDModule.GetPixelStreaming2HMD();
    }
    ```

2.  **HMD 核心接口的使用（通常由 Pixel Streaming 输入/输出处理类调用）**
    (来源: `Public/IPixelStreaming2HMD.h`)

    ```cpp
    // 假设已经通过 IPixelStreaming2HMDModule 获取到了 IPixelStreaming2HMD* 指针
    // 这些函数通常在接收到远程客户端的 VR 输入数据后调用。
    
    // 设置 HMD 的全局变换（头部位置和旋转）
    FTransform HMDTransform = /* 从 WebRTC 数据通道解析得到 */;
    HMDInterface->SetTransform(HMDTransform);
    
    // 设置双眼的视图参数，这是实现立体渲染的关键
    FTransform LeftEyeTransform = /* 从数据解析得到 */;
    FMatrix LeftProjectionMatrix = /* 从数据解析得到 */;
    FTransform RightEyeTransform = /* 从数据解析得到 */;
    FMatrix RightProjectionMatrix = /* 从数据解析得到 */;
    
    // 调用此函数一次性设置所有视图参数
    HMDInterface->SetEyeViews(
        LeftEyeTransform, LeftProjectionMatrix,
        RightEyeTransform, RightProjectionMatrix,
        HMDTransform // 可以传入同一个 HMDTransform
    );
    ```

### 进阶用法

结合 `PixelStreaming2Input` 模块，处理来自 WebRTC 数据通道的原始 HMD 输入数据，并驱动 HMD 接口。
（此过程通常由 `PixelStreaming2` 插件的 `VideoInput` 和 `AudioInput` 等组件自动完成，开发者一般无需直接处理。）

## Demo 示例

以下示例展示如何在自己的游戏模块中访问 `PixelStreaming2HMD` 模块并设置 HMD 视图。

```cpp
// MyVRStreamingGameMode.h
#pragma once
#include "GameFramework/GameModeBase.h"
#include "IPixelStreaming2HMD.h" // 引入HMD接口
#include "MyVRStreamingGameMode.generated.h"

UCLASS()
class AMyVRStreamingGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    // 假设有一个函数被定时调用，或者在网络数据包到达时调用
    void UpdateHMDFromRemoteData(const FTransform& InHMDTransform,
                                 const FTransform& InLeftEyeTransform,
                                 const FMatrix& InLeftProjection,
                                 const FTransform& InRightEyeTransform,
                                 const FMatrix& InRightProjection);
};
```

```cpp
// MyVRStreamingGameMode.cpp
#include "MyVRStreamingGameMode.h"
#include "IPixelStreaming2HMDModule.h"

void AMyVRStreamingGameMode::UpdateHMDFromRemoteData(
    const FTransform& InHMDTransform,
    const FTransform& InLeftEyeTransform,
    const FMatrix& InLeftProjection,
    const FTransform& InRightEyeTransform,
    const FMatrix& InRightProjection)
{
    // 检查模块是否可用
    if (IPixelStreaming2HMDModule::IsAvailable())
    {
        // 获取 HMD 接口
        IPixelStreaming2HMD* HMD = IPixelStreaming2HMDModule::Get().GetPixelStreaming2HMD();
        if (HMD)
        {
            // 更新 HMD 和双眼视图
            HMD->SetTransform(InHMDTransform);
            HMD->SetEyeViews(InLeftEyeTransform, InLeftProjection,
                             InRightEyeTransform, InRightProjection,
                             InHMDTransform);
        }
    }
}
```

## 模块依赖

从 `PixelStreaming2HMD.build.cs` 分析，该模块有以下独特依赖：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2Core` | 提供 `PixelStreaming2` 插件的核心类型、接口和基础功能，是此模块运行的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复了输入处理器从错误方法获取默认目标窗口的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，代码因双精度常量截断为浮点而产生警告的问题。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将各种 VP 资产移至不同的资产类别，并将其迁移至... |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了 FJsonObject 以支持 FString 和 UE::FSharedString。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的强作用域枚举可能导致输出乱码的问题。 |

### 维护评价

- **活跃度**：`PixelStreaming2` 插件（包含此模块）自 2024 年 9 月创建以来，近期（2026年4-5月）有多次提交，表明仍在积极维护中。
- **更新内容**：近期的提交主要是**问题修复**（输入处理、编译警告、数据格式化）和**内部重构**（资产管理、JSON），没有涉及 `PixelStreaming2HMD` 模块核心接口或功能的重大变更。这说明该模块已经趋于稳定。
- **推荐使用**：作为 Epic Games 官方推出的下一代 Pixel Streaming 解决方案的一部分，此模块是**官方推荐**的用于在 Pixel Streaming 中支持 XR 设备的途径。虽然它标记为 `EnabledByDefault: false`（默认未启用），这是因为它依赖于实际的 VR/XR 硬件和特定的 Pixel Streaming 设置，需要开发者根据项目需求手动启用。**推荐在需要构建远程 VR 体验的项目中使用此模块。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- 测试用例：该模块的测试集成在 `PixelStreaming2` 整体的自动化测试中，没有单独的测试文件。可参考 [Pixel Streaming 测试目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)。