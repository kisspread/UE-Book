# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置文件、处理管线） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具套件，用于将真实演员的面部表演数据（如 iPhone 深度摄像头录制的视频）转换为高保真的 MetaHuman 角色动画。它解决的核心问题是**从原始视频素材到可驱动数字角色的动画数据的自动化生产流程**。该插件包含从数据导入、面部特征点追踪、深度生成、动画求解到最终在引擎中驱动 MetaHuman 角色的完整管线。`MetaHumanPlatform` 模块是其中的一个基础模块，主要负责**平台硬件检测**，确保运行环境满足 MetaHuman 处理的最低硬件要求（如 GPU 的 LUID 和 VRAM）。

## 使用场景

- 你正在为游戏或影视项目创建数字人角色，并希望使用 iPhone 拍摄的演员表演视频来驱动 MetaHuman 角色 → 使用 MetaHuman Animator 的完整流程。
- 你需要批量处理大量面部表演数据，将其转换为动画资产 → 使用 `MetaHumanBatchProcessor` 模块。
- 你需要在项目启动时或处理前，检查用户的硬件是否满足 MetaHuman 处理的最低要求（例如，确保有足够的 VRAM 进行深度生成和求解） → 使用 `MetaHumanPlatform` 模块中的 `FMetaHumanMinSpec` 和 `FMetaHumanPhysicalDeviceProvider`。

## 蓝图用法

`MetaHumanPlatform` 模块主要提供 C++ 静态函数用于硬件查询，未暴露 `BlueprintCallable` 节点。其功能通常在插件内部或其他 C++ 模块中被调用，以进行硬件兼容性检查。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanPhysicalDeviceProvider.h"
#include "MetaHumanMinSpec.h"
```

### 基本用法

检查当前平台是否满足 MetaHuman Animator 的最低硬件规格，并获取 GPU 信息。

```cpp
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPlatform/Public/MetaHumanMinSpec.h
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPlatform/Public/MetaHumanPhysicalDeviceProvider.h

// 1. 检查硬件是否支持
bool bIsSupported = FMetaHumanMinSpec::IsSupported();
if (!bIsSupported)
{
    FText MinSpecText = FMetaHumanMinSpec::GetMinSpec();
    UE_LOG(LogTemp, Warning, TEXT("当前硬件不满足 MetaHuman Animator 的最低要求: %s"), *MinSpecText.ToString());
    // 可以向用户显示警告或禁用相关功能
}

// 2. 获取 GPU 信息（用于调试或高级配置）
FString UELUID;
TArray<FString> AllLUIDs;
if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(UELUID, AllLUIDs))
{
    UE_LOG(LogTemp, Log, TEXT("UE 使用的 GPU LUID: %s"), *UELUID);
    for (const FString& LUID : AllLUIDs)
    {
        UE_LOG(LogTemp, Log, TEXT("系统可用 GPU LUID: %s"), *LUID);
    }
}

int32 VRAMInMB = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
UE_LOG(LogTemp, Log, TEXT("主 GPU 显存: %d MB"), VRAMInMB);
```

### 进阶用法

在应用程序启动或进入 MetaHuman 相关功能模块前，进行一次完整的硬件兼容性检查，并根据结果决定后续流程。

```cpp
// 假设在一个管理器类中
void UMetaHumanManager::Initialize()
{
    // 步骤 1: 检查最低规格
    if (!FMetaHumanMinSpec::IsSupported())
    {
        FText Reason = FMetaHumanMinSpec::GetMinSpec();
        ShowUserWarning(NSLOCTEXT("MetaHuman", "MinSpecFail", "您的硬件不支持 MetaHuman 功能。"), Reason);
        bMetaHumanFeaturesEnabled = false;
        return;
    }

    // 步骤 2: 获取并记录详细的硬件信息（用于崩溃报告或技术支持）
    FString PrimaryLUID;
    TArray<FString> AllLUIDs;
    FMetaHumanPhysicalDeviceProvider::GetLUIDs(PrimaryLUID, AllLUIDs);
    int32 VRAM = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();

    UE_LOG(LogMetaHuman, Log, TEXT("MetaHuman 硬件检查通过。主GPU LUID: %s, VRAM: %dMB"), *PrimaryLUID, VRAM);

    // 步骤 3: 根据 VRAM 可以调整处理质量或启用/禁用某些特性
    if (VRAM < 8000) // 例如，低于 8GB 显存
    {
        UE_LOG(LogMetaHuman, Warning, TEXT("显存较低，将使用优化后的处理管线。"));
        // 设置一个较低的质量预设
    }

    bMetaHumanFeaturesEnabled = true;
}
```

## Demo 示例

一个最小的控制台程序示例，用于检查并输出 MetaHuman Animator 的硬件要求。

**MetaHumanPlatformCheck.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMetaHumanPlatformCheck
{
public:
    static void RunCheck();
};
```

**MetaHumanPlatformCheck.cpp**
```cpp
#include "MetaHumanPlatformCheck.h"
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"
#include "Misc/MessageDialog.h"

void FMetaHumanPlatformCheck::RunCheck()
{
    UE_LOG(LogTemp, Display, TEXT("=== MetaHuman Animator 硬件检查 ==="));

    // 检查最低规格
    bool bSupported = FMetaHumanMinSpec::IsSupported();
    FText MinSpec = FMetaHumanMinSpec::GetMinSpec();

    if (bSupported)
    {
        UE_LOG(LogTemp, Display, TEXT("✅ 硬件满足最低要求。"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("❌ 硬件不满足最低要求: %s"), *MinSpec.ToString());
        FMessageDialog::Open(EAppMsgType::Ok, MinSpec);
        return;
    }

    // 获取详细硬件信息
    FString UELUID;
    TArray<FString> AllLUIDs;
    if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(UELUID, AllLUIDs))
    {
        UE_LOG(LogTemp, Display, TEXT("UE 使用的 GPU LUID: %s"), *UELUID);
    }

    int32 VRAM = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
    UE_LOG(LogTemp, Display, TEXT("主 GPU 显存: %d MB"), VRAM);

    UE_LOG(LogTemp, Display, TEXT("=== 检查完成 ==="));
}
```

## 模块依赖

`MetaHumanPlatform` 模块本身依赖非常基础，主要用于平台抽象和硬件查询。

| 模块 | 用途 |
|---|---|
| `RHI` | 访问渲染硬件接口，获取 GPU 设备信息（LUID， VRAM） |

## 维护状态

### 近期更新

```
- b016e6885759 [UBT][CppCompileWarnings] engine compliance - wundef
- 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
- 717bd7019d0f [Backout] - CL41136011 [FYI] jon.cook #rnx Original CL Desc ----------------------------------------------------------------- Tech debt relating to MetaHuman plugin move #rb Jane.Haslam
```

### 维护评价

`MetaHumanPlatform` 模块创建于 2024 年 2 月，属于较新的模块。从近期的 git 提交记录来看，最近的更新主要集中在**编译警告修复、代码规范统一和技术债务清理**上，没有新的功能添加。这表明该模块功能已趋于稳定，目前处于**维护状态**，但并非活跃开发。作为 MetaHuman Animator 这个大型工具链的基础组件，其稳定性至关重要。鉴于其功能单一且明确（硬件检测），且最近的维护性更新保证了其与最新引擎版本的兼容性，**推荐使用**。但需注意，其核心功能高度依赖底层 RHI 的实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPlatform)