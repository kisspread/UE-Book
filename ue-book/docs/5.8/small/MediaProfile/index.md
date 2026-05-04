# Media Profile

> This plugin contains the Media Profile asset and related entities, which help manage media sources and outputs

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体配置文件资产） |
| 模块 | `MediaProfile` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile) | |

## 用途

Media Profile 插件的核心功能是提供一个名为 `UMediaProfile` 的资产，用于集中管理项目的媒体输入（源）、输出、时间码提供者（Timecode Provider）和自定义时间步长（Genlock）。它解决的核心问题是：在不同环境（如开发、测试、现场制作、最终渲染）下，需要快速、一致地切换整套媒体配置，而无需手动修改多个分散的设置。

该插件引入了“代理”（Proxy）概念，通过 `UProxyMediaSource` 和 `UProxyMediaOutput` 类。这些代理资产在项目中被引用，但它们内部指向实际的媒体源/输出。通过切换当前激活的 `UMediaProfile`，可以一次性替换所有代理指向的真实媒体设备或文件，实现了媒体配置的模块化和快速切换。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙拍摄中，需要根据拍摄场景快速切换不同的摄像机输入源（如实时渲染画面、预录制视频）和渲染输出目标。使用 Media Profile 可以将一套完整的输入输出配置保存为一个资产，在不同拍摄场景间一键切换。
- **直播与广播制作**：管理多个摄像机、视频文件、网络流等媒体源，以及多个监视器、编码器等媒体输出。通过 Media Profile 可以预设不同的节目（如新闻、体育、访谈）配置，并在直播过程中安全切换。
- **开发与测试**：在开发阶段使用测试视频文件作为媒体源，在测试阶段切换到真实的硬件设备输入，而无需修改蓝图或代码中对媒体源的引用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Proxy Valid` | 检查代理媒体源/输出是否已关联到一个有效的实际媒体源/输出。 | `UProxyMediaSource`, `UProxyMediaOutput` |
| `Get Media Source (Index)` | 根据索引获取当前媒体配置文件中配置的媒体源。 | `UMediaProfile` |
| `Get Media Output (Index)` | 根据索引获取当前媒体配置文件中配置的媒体输出。 | `UMediaProfile` |
| `Get Media Source Count` | 获取当前媒体配置文件中配置的媒体源数量。 | `UMediaProfile` |
| `Get Media Output Count` | 获取当前媒体配置文件中配置的媒体输出数量。 | `UMediaProfile` |

### 使用示例（蓝图描述）

1.  **资产准备**：在内容浏览器中，右键创建 `Media Profile` 资产。在该资产的细节面板中，配置 `Inputs`（媒体源数组）和 `Outputs`（媒体输出数组），并可以覆盖项目的 `Timecode Provider` 和 `Genlock` 设置。
2.  **使用代理**：在需要引用媒体源/输出的地方（如 `Media Player` 组件的 `Media Source` 属性），不直接引用具体的媒体文件或设备，而是引用一个 `Proxy Media Source` 或 `Proxy Media Output` 资产。
3.  **运行时切换**：在游戏逻辑或编辑器工具中，通过 `Media Profile Manager`（通过 `IMediaProfileModule::GetProfileManager()` 获取）的 `Set Current Media Profile` 函数，将当前激活的配置文件切换为另一个已准备好的 `Media Profile` 资产。所有引用了代理的组件将自动开始使用新配置文件中定义的实际媒体源/输出。

## C++ 用法

### 头文件引入

```cpp
#include "IMediaProfileModule.h"
#include "Profile/IMediaProfileManager.h"
#include "Profile/MediaProfile.h"
#include "MediaAssets/ProxyMediaSource.h"
#include "MediaAssets/ProxyMediaOutput.h"
```

### 基本用法

获取 Media Profile 管理器并监听配置文件切换事件。
（来源：`Source/MediaProfile/Public/Profile/IMediaProfileManager.h`）

```cpp
// 获取 Media Profile 模块接口
IMediaProfileModule& MediaProfileModule = FModuleManager::GetModuleChecked<IMediaProfileModule>(TEXT("MediaProfile"));
IMediaProfileManager& ProfileManager = MediaProfileModule.GetProfileManager();

// 绑定配置文件变更委托
ProfileManager.OnMediaProfileChanged().AddLambda([](UMediaProfile* Previous, UMediaProfile* New)
{
    UE_LOG(LogTemp, Log, TEXT("Media Profile changed from %s to %s"),
        Previous ? *Previous->GetName() : TEXT("None"),
        New ? *New->GetName() : TEXT("None"));
});

// 设置当前配置文件
UMediaProfile* MyProfile = LoadObject<UMediaProfile>(nullptr, TEXT("/Game/MediaProfiles/MyProfile"));
ProfileManager.SetCurrentMediaProfile(MyProfile);
```

### 进阶用法

通过代理类动态替换媒体源，并获取其最终指向的实际媒体源。
（来源：`Source/MediaProfile/Public/MediaAssets/ProxyMediaSource.h`）

```cpp
// 假设我们有一个代理媒体源资产的引用
UProxyMediaSource* ProxySource = LoadObject<UProxyMediaSource>(nullptr, TEXT("/Game/Media/ProxyCameraInput"));

if (ProxySource && ProxySource->IsProxyValid())
{
    // 获取代理链末端的真实媒体源
    UMediaSource* ActualSource = ProxySource->GetLeafMediaSource();
    if (ActualSource)
    {
        UE_LOG(LogTemp, Log, TEXT("Proxy is pointing to actual source: %s"), *ActualSource->GetName());
        // 可以用 ActualSource 去打开 Media Player
    }
}

// 在编辑器工具中，可以动态设置代理指向
#if WITH_EDITOR
    UMediaSource* NewSource = LoadObject<UMediaSource>(nullptr, TEXT("/Game/Media/NewCameraFeed"));
    ProxySource->SetMediaSource(NewSource); // 仅编辑器下可用
#endif
```

## Demo 示例

一个最小示例，展示如何创建一个简单的媒体配置文件管理器类，并应用配置文件。

**MediaProfileDemoManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MediaProfileDemoManager.generated.h"

class UMediaProfile;

UCLASS(BlueprintType)
class UMediaProfileDemoManager : public UObject
{
    GENERATED_BODY()

public:
    UMediaProfileDemoManager();

    /** 应用指定的媒体配置文件 */
    UFUNCTION(BlueprintCallable, Category = "Media Profile Demo")
    void ApplyMediaProfile(UMediaProfile* NewProfile);

    /** 获取当前配置文件 */
    UFUNCTION(BlueprintCallable, Category = "Media Profile Demo")
    UMediaProfile* GetCurrentProfile() const;

private:
    UPROPERTY()
    TObjectPtr<UMediaProfile> CurrentProfile;
};
```

**MediaProfileDemoManager.cpp**
```cpp
#include "MediaProfileDemoManager.h"
#include "IMediaProfileModule.h"
#include "Profile/IMediaProfileManager.h"
#include "Profile/MediaProfile.h"

UMediaProfileDemoManager::UMediaProfileDemoManager()
{
}

void UMediaProfileDemoManager::ApplyMediaProfile(UMediaProfile* NewProfile)
{
    // 通过模块接口获取全局管理器
    IMediaProfileModule& Module = FModuleManager::GetModuleChecked<IMediaProfileModule>(TEXT("MediaProfile"));
    IMediaProfileManager& Manager = Module.GetProfileManager();

    // 设置新的配置文件，这将触发所有代理的更新
    Manager.SetCurrentMediaProfile(NewProfile);
    CurrentProfile = NewProfile;

    UE_LOG(LogTemp, Log, TEXT("Applied Media Profile: %s"), NewProfile ? *NewProfile->GetName() : TEXT("None"));
}

UMediaProfile* UMediaProfileDemoManager::GetCurrentProfile() const
{
    return CurrentProfile;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaSource`, `UMediaOutput`, `UMediaPlayer`, `UMediaTexture` 等基础媒体资产类。 |
| `MediaFrameworkUtilities` | 提供媒体框架相关的工具类和函数，可能被代理类内部使用。 |

## 维护状态

### 近期更新

- 2026-04-24 `2f25a66f` MediaProfile：修复了将 UMediaProfile 迁移至独立插件时出现的问题
- 2026-04-24 `6dbb0e93` [MediaProfile] - 修复了加载启动媒体配置文件时的崩溃问题
- 2026-04-23 `43d97726` MediaProfile：将 UMediaProfile 及相关实体移至独立插件，以避免对 OpenCVDistortion 的依赖

### 维护评价

该插件近期维护非常活跃，在短短两天内进行了三次提交，内容集中于关键的架构重构（独立化）和稳定性修复。这表明插件正处于快速迭代和优化阶段，维护团队响应及时，致力于解决依赖和崩溃问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的源码中发现)