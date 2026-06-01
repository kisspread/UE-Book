# IOS Device Profile Selector

> IOS Device Profile Selector used show selection of device profiles on hardware（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | IOS 设备配置文件选择器 |
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `IOSDeviceProfileSelector` (RuntimeNoCommandlet), `IOSPreviewDeviceProfileSelector` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSDeviceProfileSelector) | |

## 用途

此插件是一个 **设备配置文件选择器**，专门用于 Apple 的 iOS、tvOS 和 visionOS 平台。它的核心功能是**根据当前运行游戏的 Apple 设备型号，自动选择并加载一个预设的“设备配置文件”**。

设备配置文件是 Unreal Engine 中用于统一管理特定设备硬件（如 iPhone 13 Pro, iPad Air 5 等）性能设置（如画质等级、分辨率缩放、特效开关等）的资产。通过此插件，开发者可以为不同档次的 Apple 设备配置不同的性能预设，游戏启动时，插件会查询硬件信息并自动应用最匹配的配置，无需玩家手动选择。这解决了移动端硬件碎片化带来的性能适配问题，是实现 iOS 平台画质分级和性能优化的基础。

## 使用场景

- 你的游戏计划发布在 iPhone 和 iPad 上，并且需要针对不同型号（如 iPhone SE 3 与 iPhone 15 Pro Max）设置不同的默认画质等级。
- 你需要在运行时动态检测设备型号，为高、中、低配置设备分别加载“高画质”、“均衡画质”和“流畅画质”配置文件。
- 你使用了 `DeviceProfiles` 插件管理画质预设，现在需要为其在 iOS 平台上添加自动选择的逻辑。

## 蓝图用法

本插件不包含可直接在蓝图中调用的节点。它是一个系统级模块，其逻辑（根据设备硬件选择配置文件）在引擎启动时由 **设备配置文件系统** 自动调用。开发者需要做的是在编辑器中为不同的 iOS 设备型号创建和配置 `DeviceProfile` 资产，插件会负责运行时的匹配。

## C++ 用法

### 头文件引入

```cpp
// 需要包含设备配置文件系统的基础接口
#include "DeviceProfiles/IDeviceProfileSelectorModule.h"
```

### 基本用法

此插件主要通过 `IOSDeviceProfileSelector` 模块实现 `IDeviceProfileSelectorModule` 接口。引擎的设备配置文件管理器会调用 `GetRuntimeDeviceProfileName` 方法来获取当前设备的配置文件名称。以下是如何在代码中获取这个选择器模块并查询配置文件名的示例。

```cpp
// 来源：基于 Private/IOSDeviceProfileSelectorModule.h 推断的典型用法
#include "Modules/ModuleManager.h"
#include "DeviceProfiles/IDeviceProfileSelectorModule.h"

// 获取 IOS 设备配置文件选择器模块
FModuleManager& ModuleManager = FModuleManager::Get();
IDeviceProfileSelectorModule* SelectorModule = ModuleManager.GetModulePtr<IDeviceProfileSelectorModule>(TEXT("IOSDeviceProfileSelector"));

if (SelectorModule)
{
    // 获取根据当前运行设备硬件所匹配的设备配置文件名称
    FString DeviceProfileName = SelectorModule->GetRuntimeDeviceProfileName();
    UE_LOG(LogTemp, Log, TEXT("为当前设备选择的配置文件: %s"), *DeviceProfileName);
    
    // 通常，这个 Name 会被设备配置文件系统用于加载对应的 UDeviceProfile 资产。
    // 开发者很少直接调用此方法，而是依赖系统自动处理。
}
```

### 进阶用法

在自定义的设备配置文件选择器或性能管理系统中，你可能需要复用其设备检测逻辑。虽然插件本身不直接暴露设备型号字符串，但你可以结合 `IOSDeviceProfileSelector` 模块的自动选择机制和 `DeviceProfiles` 插件的 API，构建更复杂的画质管理策略。

例如，你可以监听配置文件加载完成的事件，然后在此基础上叠加一些不基于设备型号的动态画质调整（如根据电量、温度）。

## Demo 示例

这是一个最小的、用于演示如何在运行时访问和验证 IOS 设备配置文件选择器模块的 C++ 类。

```cpp
// MyIOSProfileVerifier.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyIOSProfileVerifier.generated.h"

UCLASS()
class MYGAME_API AMyIOSProfileVerifier : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};

// MyIOSProfileVerifier.cpp
#include "MyIOSProfileVerifier.h"
#include "Modules/ModuleManager.h"
#include "DeviceProfiles/IDeviceProfileSelectorModule.h"

void AMyIOSProfileVerifier::BeginPlay()
{
    Super::BeginPlay();

    // 尝试获取 IOS 设备配置文件选择器模块
    if (IDeviceProfileSelectorModule* Selector = FModuleManager::GetModulePtr<IDeviceProfileSelectorModule>(TEXT("IOSDeviceProfileSelector")))
    {
        const FString ProfileName = Selector->GetRuntimeDeviceProfileName();
        UE_LOG(LogTemp, Warning, TEXT("IOS 设备配置文件选择器已加载。当前设备匹配的配置文件: %s"), *ProfileName);
        // 预期输出类似: "IOS_IPhone14,5" 或 "IOS_IPad13,18"
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("IOS 设备配置文件选择器模块未加载。这可能发生在非 iOS 平台，或插件被禁用。"));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新的 UE_LOGF 宏，是代码库现代化的维护性改动。 |
| 2026-02-24 | `6fa9a99f` | Add Aspect Ratio to IOS Preview Json | 为 iOS 预览器的 JSON 配置添加了宽高比属性，改进了编辑器预览功能。 |
| 2026-02-18 | `f5a10b68` | Add Preview json Versioning | 为预览 JSON 添加了版本控制，便于未来配置格式的升级和管理。 |
| 2026-02-13 | `bbbd7847` | Add ConfigRules to Android Preview Json | 此提交与本 iOS 插件无关，是针对 Android 预览器的改动。 |
| 2026-02-11 | `87fe38ca` | Fix RTTI Linux | 修复了 Linux 平台上的 RTTI (运行时类型信息) 问题，是跨平台兼容性修复。 |

### 维护评价

- **状态**: 维护中。
- **分析**: 该插件创建于 2014 年，是 UE 的元老级组件。虽然其核心逻辑稳定，但近期的 Git 记录（截至 2026 年 2 月）显示仍有活跃的维护活动，主要集中在 **编辑器预览工具** (`IOSPreviewDeviceProfileSelector` 模块) 的增强和 **日志、构建系统的现代化** 上。这表明 Epic 仍在确保其功能的正常和现代化，但并未进行功能的大规模重构或添加。
- **建议**: **可以放心使用**。这是 Unreal Engine 官方为 iOS 平台提供的设备适配标准解决方案，稳定可靠。对于绝大多数需要为不同 iOS 设备提供差异化性能设置的游戏项目，此插件是推荐甚至必需的基础设施。唯一的注意事项是，它的运行时逻辑高度集成在引擎内部，自定义扩展性较低。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSDeviceProfileSelector)
- [官方文档](https://docs.unrealengine.com) (无独立文档，功能属于 Device Profiles 系统的一部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/IOSDeviceProfileSelector) (无独立测试目录)