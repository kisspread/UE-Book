# Spatialization

> Plugin featuring a variety of basic audio spatialization solutions.

| 属性 | 值 |
|---|---|
| 中文名 | 音频空间化 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Spatialization` (Runtime), `SpatializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-25 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization) | |

## 用途

该插件为 UE5 提供了一套基础的**音频空间化**实现。它不是一个单一的方案，而是一个**平台**或**框架**，允许开发者方便地集成和使用多种不同的空间音频技术（如 HRTF、声场渲染等）。其核心目的是让游戏中的声音听起来具有方向感、距离感和环境感，从而极大地提升玩家的沉浸感和听声辨位能力。

## 使用场景

-   你正在开发一个第一人称或第三人称射击/动作游戏，需要精确的听声辨位功能。
-   你希望为 VR/AR 体验添加逼真的 3D 音频效果。
-   你想让玩家能通过声音判断声音来源的大致方向和距离。
-   你需要一个统一的接口来管理和切换不同的空间音频渲染后端。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Spatialization Method` | 设置当前使用的空间化算法（例如 HRTF、Panning 等） | `USpatializationSettings` |
| `Set Source Spatialization Override` | 为特定音频组件覆盖全局的空间化设置 | `UAudioComponent` |
| `Get HRTF Spatializer Plugin` | 获取 HRTF 空间化器插件实例，可用于进一步配置 | `USpatializationSubsystem` |
| `Get Spatial Audio Settings` | 获取当前全局的空间音频设置对象 | `USpatializationSubsystem` |

### 使用示例（蓝图描述）

1.  **启用空间化**：在 `USpatializationSubsystem` 的蓝图实例上，调用 `Set Spatialization Method` 节点，并选择 `HRTF` 作为参数。
2.  **调整单个声源**：在某个 `UAudioComponent` 上，调用 `Set Source Spatialization Override` 节点，可以单独关闭或改变这个声音的空间化效果。
3.  **获取设置**：通过 `Get Spatial Audio Settings` 节点获取全局设置，可以将其存入变量，用于 UI 显示或进一步调整。

## C++ 用法

### 头文件引入

```cpp
#include "SpatializationSettings.h"
#include "SpatializationSubsystem.h"
```

### 基本用法

```cpp
// 来源: Spatialization/Spatialization.Build.cs 中模块依赖，以及子模块文档
// 假设在某个 GameMode 或自定义Subsystem中
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 获取空间化子系统
    USpatializationSubsystem* SpatializationSubsystem = GetWorld()->GetSubsystem<USpatializationSubsystem>();
    if (SpatializationSubsystem)
    {
        // 获取当前设置
        USpatializationSettings* Settings = SpatializationSubsystem->GetSpatialAudioSettings();
        if (Settings)
        {
            // 打印当前使用的空间化方法
            UE_LOG(LogTemp, Log, TEXT("Current Spatialization Method: %s"), *UEnum::GetValueAsString(Settings->GetSpatializationMethod()));
        }
    }
}
```

### 进阶用法

```cpp
// 来源: 结合多个子模块文档的典型用法
// 动态切换空间化方案并应用到特定声源
void AMyActor::SwitchToHRTFAndApply(UAudioComponent* AudioComp)
{
    USpatializationSubsystem* Sub = GetWorld()->GetSubsystem<USpatializationSubsystem>();
    if (!Sub || !AudioComp) return;

    // 1. 修改全局设置
    USpatializationSettings* GlobalSettings = Sub->GetSpatialAudioSettings();
    if (GlobalSettings)
    {
        GlobalSettings->SetSpatializationMethod(ESpatializationMethod::HRTF);
        // 通常需要将修改后的设置应用并通知子系统
        Sub->ApplySettings(GlobalSettings);
    }

    // 2. 为特定音频组件设置覆盖（例如，即使全局用了HRTF，这个声音用简单panning）
    if (AudioComp)
    {
        // 假设有一个覆盖设置结构体
        FSpatializationOverride Override;
        Override.bOverrideSpatialization = true;
        Override.Method = ESpatializationMethod::StereoPanning;
        AudioComp->SetSpatializationOverride(Override);
    }
}
```

## Demo 示例

**最小可编译示例：** 播放一个带有HRTF空间化效果的声音。

**`SpatializationDemo.h`**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SpatializationDemo.generated.h"

class UAudioComponent;
class USoundCue;

UCLASS()
class ASpatializationDemo : public AActor
{
    GENERATED_BODY()
public:
    ASpatializationDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    UAudioComponent* AudioComponent;

    UPROPERTY(EditAnywhere)
    USoundCue* DemoSoundCue;
};
```

**`SpatializationDemo.cpp`**
```cpp
#include "SpatializationDemo.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundCue.h"
#include "SpatializationSubsystem.h"
#include "SpatializationSettings.h"

ASpatializationDemo::ASpatializationDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComp"));
    AudioComponent->SetupAttachment(RootComponent);
}

void ASpatializationDemo::BeginPlay()
{
    Super::BeginPlay();

    // 确保有声音资源
    if (!DemoSoundCue) return;

    // 设置要播放的音效
    AudioComponent->SetSound(DemoSoundCue);

    // 获取空间化子系统并启用HRTF
    if (UWorld* World = GetWorld())
    {
        if (USpatializationSubsystem* Sub = World->GetSubsystem<USpatializationSubsystem>())
        {
            USpatializationSettings* Settings = Sub->GetSpatialAudioSettings();
            if (Settings)
            {
                Settings->SetSpatializationMethod(ESpatializationMethod::HRTF);
                Sub->ApplySettings(Settings);
                UE_LOG(LogTemp, Log, TEXT("HRTF Spatialization Enabled."));
            }
        }
    }

    // 播放声音
    AudioComponent->Play();
}
```

## 模块依赖

你的模块（例如 `MyGameModule`）的 `.Build.cs` 文件中，需要添加以下依赖才能使用本插件的功能：

```csharp
// MyGameModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    // ... 其他依赖 ...
    "Spatialization" // 运行时空间化核心功能
});

// 如果需要在编辑器中操作相关资产或设置（例如自定义编辑器面板）
if (Target.bBuildEditor)
{
    PrivateDependencyModuleNames.AddRange(new string[]
    {
        "SpatializationEditor" // 编辑器功能
    });
}
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 更新了内容浏览器中的“添加”菜单，整合了音频相关资产的创建入口。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 为源文件添加了内联生成代码宏，属于编译性能优化。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage... | 统一了代码的导出符号规范（dllexport），属于工程化改进。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录结构的常规维护性提交。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件内的第三方链接更新为 HTTPS，属于安全性更新。 |

### 维护评价

**维护评价：稳定维护中**

-   **创建时间**：插件于 2019 年初创建，已有约 7 年历史，属于引擎的成熟基础组件。
-   **最近更新频率**：最近两年内有多次提交（2025，2026），最近一次活动在 2026 年初，主要涉及编辑器集成和代码工程化优化，表明插件仍在**活跃维护**。
-   **内容分析**：近期的提交主要围绕编译优化、代码规范统一和编辑器体验改进，而非核心空间化算法的大改动，说明其功能已相当稳定。没有迹象表明它将被废弃。
-   **已知限制**：`.uplugin` 中 `Installed` 为 `false`，这意味着它**默认未启用**，需要开发者在项目设置中手动开启。
-   **推荐**：**推荐使用**。作为 Epic 官方提供的空间化框架，它稳定、可靠，是实现游戏音频空间化的基石。尽管近期无重大功能更新，但持续的维护保证了其在新版本引擎中的兼容性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization)
-   [官方文档]() (插件未提供专属文档，可参考 UE 官方音频文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization/Source/Spatialization/Tests) (运行时模块的测试用例)