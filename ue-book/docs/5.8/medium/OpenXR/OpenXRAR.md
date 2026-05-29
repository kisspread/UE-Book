# OpenXR

> OpenXR is an open VR/AR standard（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 开放扩展现实 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（AR系统与接口） |
| 模块 | `OpenXRHMD` (Runtime), `OpenXRInput` (Runtime), `OpenXRAR` (Runtime), `OpenXREditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-04-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR) | |

## 用途

**OpenXR** 是 Khronos Group 制定的用于 VR/AR 应用开发的开放标准，旨在统一不同硬件厂商（如 Oculus、SteamVR、Windows Mixed Reality 等）的 API。这个 Unreal Engine 插件是 OpenXR 标准的 **运行时实现**。

它的核心作用是充当 **中间抽象层**。开发者不再需要为每种头显或平台编写特定的代码，而是通过 Unreal Engine 统一的 VR/AR 框架（如 `IXRTrackingSystem`）调用 OpenXR 提供的接口，OpenXR 运行时会负责与底层的具体硬件进行通信。这使得应用程序能够实现一次开发，运行在多个支持 OpenXR 的平台上。

## 使用场景

-   **开发跨平台 VR 游戏或应用**：你希望你的 VR 应用能在 Meta Quest、Valve Index、HTC Vive 等多种头显上运行，而无需维护多套硬件抽象代码。
-   **创建混合现实（MR）或增强现实（AR）应用**：需要利用设备的空间追踪、网格重建、平面识别等现实世界感知功能（例如 `OpenXRAR` 模块提供的功能）。
-   **将现有项目移植到新的 OpenXR 兼容头显**：通过切换到 OpenXR 插件，快速获得对新硬件的支持。
-   **使用统一的输入系统处理控制器交互**：通过 `OpenXRInput` 模块与 UE 的增强输入系统（Enhanced Input）集成，处理不同手柄的按键和动作映射。

## 蓝图用法

OpenXR 的核心功能（如 HMD 管理、底层输入）通常在引擎层自动处理。`OpenXRAR` 模块为 AR 功能提供了蓝图可访问的接口，但这些接口主要由 UE 的 AR 子系统（`UARBlueprintLibrary`）在底层调用，开发者通常不直接在蓝图中调用 `OpenXRAR` 的类。

对于开发者而言，更常见的是通过 **UE 的标准 VR/AR 蓝图节点** 来使用 OpenXR 的能力，因为这些节点会路由到已激活的 XR 系统（如果 OpenXR 是激活的 HMD 插件，则为 OpenXR）。例如：

1.  **启动/停止 AR 会话**：使用 `Start AR Session` 和 `Stop AR Session` 节点。
2.  **射线检测**：使用 `Line Trace Tracked Objects` 节点检测现实世界中的表面。
3.  **获取跟踪的几何体**：使用 `Get All Geometries`、`Get All Planes` 等节点获取环境信息。
4.  **将组件固定到现实世界**：使用 `Pin Component to AR Pin` 节点。

这些节点的具体行为将取决于当前激活的 AR 系统（如果是 OpenXR，则由 `FOpenXRARSystem` 实现）。

## C++ 用法

主要涉及配置 OpenXR 以及扩展其 AR 功能。

### 头文件引入

```cpp
// 使用 HMD 核心功能
#include "OpenXRHMD.h"

// 使用 AR 扩展功能（如空间网格、QR码）
#include "IOpenXRARTrackedGeometryHolder.h"
```

### 基本用法

典型的 VR 应用启动后，OpenXR 系统会自动初始化。开发者主要需要处理 AR 相关的配置和数据获取。

```cpp
// 示例：在你的游戏模式中，请求并处理 AR 空间网格数据
// 来源：引擎源码 OpenXRAR 模块的设计模式

void AMyGameMode::SetupAREnvironment()
{
    // 1. 检查 AR 系统是否可用
    if (UARBlueprintLibrary::GetARSessionStatus().Status != EARSessionStatus::Running)
    {
        // 2. 创建并配置 AR 会话
        UARSessionConfig* Config = NewObject<UARSessionConfig>();
        // 启用平面检测和空间网格生成
        Config->SetPlaneDetectionMode(EARPlaneDetectionMode::Horizontal);
        Config->bGenerateMeshDataForTrackedObjects = true;
        
        // 3. 启动 AR 会话（这会触发 OpenXR AR 系统的 OnStartARSession）
        UARBlueprintLibrary::StartARSession(Config);
    }
}

void AMyGameMode::UpdateEnvironmentData()
{
    // 4. 获取所有跟踪到的网格几何体
    TArray<UARTrackedGeometry*> Geometries = UARBlueprintLibrary::GetAllGeometries();
    for (UARTrackedGeometry* Geo : Geometries)
    {
        if (UARTrackedMesh* Mesh = Cast<UARTrackedMesh>(Geo))
        {
            // 5. 使用网格数据（例如生成碰撞体或渲染）
            UE_LOG(LogTemp, Log, TEXT("Mesh Found: %s"), *Mesh->GetName());
            // 获取网格顶点和索引用于生成动态网格...
        }
    }
}
```

### 进阶用法

你可以通过实现 `IOpenXRARTrackedGeometryHolder` 接口来接收自定义的几何体更新事件，或者与 OpenXR 扩展交互。

```cpp
// 示例：自定义一个类来监听特定的 AR 对象（如 QR 码）更新
// 来源：IOpenXRARTrackedGeometryHolder.h

class FMyQRCodeTracker : public IOpenXRARTrackedGeometryHolder
{
public:
    FMyQRCodeTracker()
    {
        // 将自己注册为模块功能，以便 OpenXR 系统可以找到并通知我们
        IModularFeatures::Get().RegisterModularFeature(GetModularFeatureName(), this);
    }

    ~FMyQRCodeTracker()
    {
        IModularFeatures::Get().UnregisterModularFeature(GetModularFeatureName(), this);
    }

    // 接口实现：当新的 QR 码被添加到 AR 场景中时调用
    virtual void ARTrackedGeometryAdded(TSharedPtr<FOpenXRARTrackedGeometryData> InData) override
    {
        // 检查数据是否是 QR 码类型
        if (InData->DataType == FOpenXRARTrackedGeometryData::EDataType::QRCode)
        {
            // 强制转换为 QR 码数据结构
            FOpenXRQRCodeData* QRData = static_cast<FOpenXRQRCodeData*>(InData.Get());
            UE_LOG(LogTemp, Warning, TEXT("QR Code Found: %s"), *QRData->QRCode);
            // 处理 QR 码内容...
        }
    }

    // 其他接口方法留空或简单实现
    virtual void ARTrackedGeometryUpdated(TSharedPtr<FOpenXRARTrackedGeometryData> InData) override {}
    virtual void ARTrackedGeometryRemoved(TSharedPtr<FOpenXRARTrackedGeometryData> InData) override {}
    // ... 其他重载
};
```

## Demo 示例

一个最小化的例子，展示如何通过代码启用 OpenXR AR 功能并检查空间网格。

**OpenXRARDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OpenXRARDemo.generated.h"

UCLASS()
class YOURPROJECT_API AOpenXRARDemo : public AActor
{
    GENERATED_BODY()
    
public:    
    AOpenXRARDemo();

protected:
    virtual void BeginPlay() override;

    // 用于存储找到的 AR 网格
    UPROPERTY(VisibleAnywhere)
    TArray<AActor*> SpawnedMeshActors;

    // 配置 AR 会话
    UPROPERTY(EditAnywhere)
    TObjectPtr<UARSessionConfig> ARConfig;

    // 每帧检查网格的计时器
    FTimerHandle MeshCheckTimerHandle;

    void CheckForNewMeshes();
};
```

**OpenXRARDemo.cpp**
```cpp
#include "OpenXRARDemo.h"
#include "ARBlueprintLibrary.h"
#include "ARSessionConfig.h"
#include "ARTrackedMesh.h"

AOpenXRARDemo::AOpenXRARDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AOpenXRARDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 检查设备是否支持所需特性
    bool bMeshingSupported = UARBlueprintLibrary::IsSessionTrackingFeatureSupported(
        EARSessionType::World, 
        EARSessionTrackingFeature::SceneUnderstanding_Meshes
    );

    if (!bMeshingSupported)
    {
        UE_LOG(LogTemp, Warning, TEXT("当前设备或 AR 系统不支持空间网格功能。"));
        return;
    }

    // 2. 创建并配置会话，启用网格生成
    ARConfig = NewObject<UARSessionConfig>();
    ARConfig->SetSessionTrackingFeatureToEnable(EARSessionTrackingFeature::SceneUnderstanding_Meshes);
    ARConfig->bGenerateMeshDataForTrackedObjects = true;

    // 3. 启动 AR 会话
    UARBlueprintLibrary::StartARSession(ARConfig);

    // 4. 设置一个定时器，每秒检查一次是否有新的网格出现
    GetWorldTimerManager().SetTimer(MeshCheckTimerHandle, this, &AOpenXRARDemo::CheckForNewMeshes, 1.0f, true);
}

void AOpenXRARDemo::CheckForNewMeshes()
{
    // 5. 获取当前所有跟踪的几何体
    TArray<UARTrackedGeometry*> Geometries = UARBlueprintLibrary::GetAllGeometries();

    for (UARTrackedGeometry* Geometry : Geometries)
    {
        // 6. 筛选出是网格且处于正在跟踪状态的对象
        UARTrackedMesh* TrackedMesh = Cast<UARTrackedMesh>(Geometry);
        if (TrackedMesh && TrackedMesh->GetTrackingState() == EARTrackingState::Tracking)
        {
            // 在实际项目中，这里会调用 TrackedMesh->GetStaticMeshComponent() 获取网格体
            // 并用于生成可碰撞的静态网格体 Actor。这里仅做日志输出。
            UE_LOG(LogTemp, Log, TEXT("检测到环境网格，名称：%s"), *TrackedMesh->GetName());
        }
    }
}
```

## 模块依赖

要使用此插件的特定功能，你的模块需要添加以下依赖。

| 模块 | 用途 |
|---|---|
| `OpenXRHMD` | 访问核心的 VR HMD 管理功能，如果你只做标准 VR 开发，通常不需要直接引用。 |
| `OpenXRAR` | 访问增强现实功能，如空间网格、QR码检测。这是实现 MR 功能的主要模块。 |
| `EnhancedInput` | `OpenXRInput` 模块的依赖，用于处理控制器输入映射。 |

*注意：插件本身依赖 `XRBase` 和 `EnhancedInput`，但使用标准 VR 功能通常无需在你的 Build.cs 中手动添加这些，它们会由引擎自动处理。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `0421053e` | [OpenXR][Vulkan] Request TRANSFER_DST_BIT for XR render target swapchains | 修复 Vulkan 后端下 OpenXR 渲染目标交换链的标志位问题，确保正确渲染。 |
| 2026-05-14 | `a57c6062` | Stereolayers with Supports Depth wobble: prevent dangling next-chain pointers in CompositionDepthTest | 修复立体层深度支持中的指针悬空问题，提升渲染稳定性。 |
| 2026-04-30 | `da4fc827` | PR #14037: Fix no audio when xrGetAudioOutputDeviceGuidOculus returns failure | 修复在 Oculus 平台获取音频设备失败时导致游戏没有声音的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中枚举类型使用不当可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复日志格式化字符串中 32 位与 64 位格式说明符不匹配的问题。 |

### 维护评价

OpenXR 插件是 **Epic Games 官方维护的核心 VR/AR 标准实现**。从创建时间（2019年）来看，它已经是一个成熟的插件。近期的 git 提交记录（最新到 2026 年）显示它仍在 **持续、活跃地维护**，更新内容涵盖新功能支持（如 Vulkan 优化）、平台兼容性修复（如 Oculus 音频）以及底层稳定性改进。

该插件是 Unreal Engine 官方推荐的 VR/AR 开发路径，且默认状态为禁用（`EnabledByDefault: false`），这符合其作为标准运行时选项的定位。它没有标记为实验性，表明已经足够稳定用于生产环境。

**推荐使用**。如果你的目标平台支持 OpenXR（几乎所有现代 VR/MR 头显都支持），那么这是构建跨平台 VR/AR 应用最可靠和未来-proof 的方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR)