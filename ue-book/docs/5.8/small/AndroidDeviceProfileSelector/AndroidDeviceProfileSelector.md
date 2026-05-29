# Android Device Profile Selector

> Android Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 中文名 | 安卓设备配置选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidDeviceProfileSelector` (Editor), `AndroidDeviceProfileCommandlets` (Editor), `AndroidDeviceProfileSelectorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector) | |

## 用途

此插件是 Unreal Engine 设备配置文件（Device Profile）系统在 Android 平台的核心实现。其主要功能是在运行时根据当前 Android 设备的硬件特性（如 GPU 型号、OpenGL/Vulkan 版本、内存大小、芯片集等），通过一系列预定义的匹配规则，自动选择最合适的设备配置文件。

它解决了 Android 设备碎片化严重的问题。开发者无需为成百上千种设备手动编写配置，而是通过制定规则（如“当 GPU 为 Adreno 3xx 且内存小于 2GB 时，应用 LowQuality 配置”），让引擎在游戏启动时自动应用最佳画质和性能设置，从而优化用户体验并简化开发流程。

## 使用场景

-   当你正在开发一款需要在多种 Android 设备上运行的游戏，并希望根据设备性能自动调整画质、分辨率或功能开关时。
-   当你需要针对特定厂商或型号的设备（如三星 Galaxy、小米 Redmi 等）应用特殊的渲染或输入优化时。
-   当你希望在编辑器中预览不同 Android 设备的配置效果时（通过 `PIEPreviewDeviceSpecification` 模块）。

## 蓝图用法

此插件的核心逻辑主要通过 C++ 模块接口实现，未暴露大量蓝图节点。其主要作用发生在引擎启动时，对蓝图层面是透明的。开发者主要通过配置 `.ini` 文件来定义匹配规则。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDeviceProfileName` | 获取根据当前设备硬件匹配到的设备配置名称 | `FAndroidDeviceProfileSelectorModule` |
| `GetRuntimeDeviceProfileName` | 获取运行时使用的设备配置名称（通常与上者相同） | `FAndroidDeviceProfileSelectorModule` |

## C++ 用法

### 头文件引入

```cpp
#include "AndroidDeviceProfileSelector/AndroidDeviceProfileSelector.h"
```

### 基本用法

通过全局静态类 `FAndroidDeviceProfileSelector` 获取设备匹配结果或设置设备属性。

**来源**: `Public/AndroidDeviceProfileSelector.h`

```cpp
#include "AndroidDeviceProfileSelector/AndroidDeviceProfileSelector.h"

// 在某个时机（例如游戏模式初始化后），获取当前设备匹配到的配置名称
FString CurrentProfileName = FAndroidDeviceProfileSelector::FindMatchingProfile(TEXT("Android")); // FallbackProfileName 是未匹配到任何规则时的默认配置名

// 获取引擎收集到的设备属性（只读）
const TMap<FString, FString>& DeviceProperties = FAndroidDeviceProfileSelector::GetSelectorProperties();

// 通过预定义的属性名访问特定信息，例如 GPU 型号
const FString* GPUFamily = DeviceProperties.Find(FAndroidProfileSelectorSourceProperties::SRC_GPUFamily);
if (GPUFamily)
{
    UE_LOG(LogTemp, Log, TEXT("Device GPU Family: %s"), **GPUFamily);
}
```

### 进阶用法

**1. 手动设置设备属性（用于测试或特殊场景）**
```cpp
TMap<FString, FString> CustomProperties;
CustomProperties.Add(FAndroidProfileSelectorSourceProperties::SRC_GPUFamily, TEXT("Adreno (TM) 640"));
CustomProperties.Add(FAndroidProfileSelectorSourceProperties::SRC_TotalPhysicalGB, TEXT("8"));
// ... 设置其他属性
FAndroidDeviceProfileSelector::SetSelectorProperties(CustomProperties);

// 使用新属性重新匹配配置
FString CustomMatchedProfile = FAndroidDeviceProfileSelector::FindMatchingProfile(TEXT("Android"));
```

**2. 使用模块接口**
在编写编辑器扩展或工具时，可以直接获取 `IDeviceProfileSelectorModule` 接口。
```cpp
IDeviceProfileSelectorModule* SelectorModule = FModuleManager::GetModulePtr<IDeviceProfileSelectorModule>(TEXT("AndroidDeviceProfileSelector"));
if (SelectorModule)
{
    FString ProfileName = SelectorModule->GetDeviceProfileName();
    // ... 处理配置名称
}
```

## Demo 示例

一个最小化示例，展示如何在模块启动后查询 Android 设备配置。

**MyActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "AndroidDeviceProfileSelector/AndroidDeviceProfileSelector.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

#if PLATFORM_ANDROID
    // 等待引擎完成设备检测和配置选择（通常在 PreInit 很早阶段就完成了）
    const FString SelectedProfile = FAndroidDeviceProfileSelector::FindMatchingProfile(TEXT("Android"));
    UE_LOG(LogTemp, Log, TEXT("Applied Android Device Profile: %s"), *SelectedProfile);

    // 示例：读取总物理内存来决定某个功能
    const auto& Properties = FAndroidDeviceProfileSelector::GetSelectorProperties();
    if (const FString* RAMSizeStr = Properties.Find(FAndroidProfileSelectorSourceProperties::SRC_TotalPhysicalGB))
    {
        const int32 RAMSizeGB = FCString::Atoi(**RAMSizeStr);
        if (RAMSizeGB >= 6)
        {
            UE_LOG(LogTemp, Log, TEXT("Device has %d GB RAM, enabling high-res textures."), RAMSizeGB);
            // ... 启用高分辨率纹理
        }
    }
#endif
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AndroidDeviceDetection` | 用于检测和获取 Android 设备的详细硬件信息。 |
| `PIEPreviewDeviceSpecification` | 支持在编辑器中预览特定 Android 设备的配置效果。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`，为日志系统升级做准备。 |
| 2026-03-02 | `f2f207d7` | [AndroidDeviceProfileSelectorRuntime] | 对运行时模块进行维护更新（信息未详细说明，可能为编译修复或清理）。 |
| 2026-03-01 | `1d115ca4` | Changed codegen to only create one Z_Construct_<Type> function but with a bool as inparam to decide | 优化了代码生成逻辑，减少了生成函数的数量，提升了编译效率。 |
| 2026-02-18 | `f5a10b68` | Add Preview json Versioning | 为预览 JSON 文件添加了版本控制，增强了编辑器预览功能的可维护性。 |
| 2026-02-13 | `bbbd7847` | Add ConfigRules to Android Preview Json | 在 Android 预览 JSON 中支持配置规则，使编辑器预览更贴近真实设备行为。 |

### 维护评价

该插件创建于 2014 年，历史悠久，是 Android 平台适配的基石模块。从最近的提交记录（2026 年 2-4 月）来看，它仍处于**活跃维护**状态。近期的更新主要集中在性能优化（代码生成）、功能增强（预览 JSON 版本化和规则支持）以及工程现代化（日志系统迁移）上，没有出现废弃标记。

由于其在 Android 开发中的核心地位和持续的更新，**强烈推荐使用**。开发者应确保项目中的设备匹配规则 `.ini` 文件得到妥善维护，以利用最新的硬件检测能力。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidDeviceProfileSelector)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/AndroidDeviceProfileSelectorTests) (推测路径)