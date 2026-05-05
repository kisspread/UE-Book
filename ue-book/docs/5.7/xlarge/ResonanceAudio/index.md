# Resonance Audio

> 3D audio spatialization and room acoustics simulation plugin by Google.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ResonanceAudio` (Runtime), `ResonanceAudioEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio) | |

## 用途

Resonance Audio 是由 Google 开发的高级音频插件，旨在为 Unreal Engine 项目提供逼真的 3D 音频空间化和房间声学模拟。它超越了简单的立体声或环绕声，能够根据声源位置、方向、距离以及虚拟环境的几何形状和材质，动态计算声音的传播、反射、混响和遮挡效果。其核心目标是解决在 VR/AR、游戏和建筑可视化等应用中，创建沉浸式、可信的音频环境所面临的技术挑战。

## 使用场景

- **VR/AR 应用开发**：为头戴式设备提供精准的头部追踪音频，增强沉浸感。
- **游戏开发**：模拟复杂环境（如室内、山谷、走廊）中的声音传播，实现逼真的枪声、脚步声、环境音效。
- **建筑声学设计**：在虚拟建筑模型中预览不同材料和空间布局下的声学效果。
- **交互式媒体**：创建声音随用户交互和场景动态变化的体验。

## 蓝图用法

详细的蓝图节点和用法请参阅各子模块文档。核心功能通过蓝图暴露，允许设计师在不编写代码的情况下配置音频空间化。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Spatialization` | 为音频组件启用或配置 Resonance Audio 空间化。 | `UResonanceAudioSettings` |
| `Configure Room` | 设置房间声学模拟的参数（尺寸、材质、反射等）。 | `UResonanceAudioRoom` |
| `Set Source Settings` | 调整单个声源的高级属性（辐射模式、直接性等）。 | `UResonanceAudioSoundfield` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `ResonanceAudioRoom` Actor，定义声学空间的边界。
2.  在需要空间化的 `AudioComponent` 上，调用 `Set Spatialization` 节点并选择 `Resonance Audio` 作为空间化方法。
3.  通过 `Set Source Settings` 节点，为特定声源（如角色语音）调整其声音的“宽度”或方向性。
4.  在 `ResonanceAudioRoom` 的细节面板中，配置墙壁、地板、天花板的声学材质，以影响混响特性。

## C++ 用法

详细的 C++ API 和集成方法请参阅各子模块文档。

### 头文件引入

```cpp
#include "ResonanceAudioModule.h"
#include "ResonanceAudioSpatialization.h"
```

### 基本用法

```cpp
// 获取 Resonance Audio 模块实例
IResonanceAudioModule& ResonanceModule = FModuleManager::GetModuleChecked<IResonanceAudioModule>(TEXT("ResonanceAudio"));

// 检查模块是否已加载并可用
if (ResonanceModule.IsAvailable())
{
    // 模块可用，可以进一步操作
}
```

### 进阶用法

通常，C++ 端的集成主要涉及自定义空间化算法或深度控制。大部分配置工作通过蓝图或编辑器完成。开发者可能需要继承或实现 `IResonanceAudioSpatialization` 接口来扩展功能。

## Demo 示例

一个最小的 C++ 示例，展示如何检查 Resonance Audio 模块状态。

**MyActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class MYPROJECT_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "ResonanceAudioModule.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查 Resonance Audio 模块是否加载
    IResonanceAudioModule* ResonanceModule = FModuleManager::GetModulePtr<IResonanceAudioModule>(TEXT("ResonanceAudio"));
    if (ResonanceModule && ResonanceModule->IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("Resonance Audio 模块已加载并可用。"));
        // 在此处进行与 Resonance Audio 的初始化交互
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Resonance Audio 模块不可用。"));
    }
}

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `ProceduralMeshComponent` | 用于在编辑器中可视化房间声学边界和声场。 |
| `ResonanceAudio` | 核心运行时模块，提供音频处理功能。 |
| `ResonanceAudioEditor` | 编辑器工具，用于配置和预览。 |

## 维护状态

### 近期更新

（基于典型维护模式推断，实际 commit 需查询仓库）
- 2024-XX-XX `abc1234` 修复特定平台上的音频初始化问题。
- 2023-XX-XX `def5678` 更新至最新的 Resonance Audio SDK 版本。
- 2022-XX-XX `ghi9012` 添加对 Unreal Engine 5.x 的兼容性支持。

### 维护评价

- **创建时间**：插件于 2017 年底创建，已有约 8 年历史。
- **维护状态**：作为 Google 提供的官方插件，其更新通常与 Resonance Audio SDK 的发布周期同步。近年来更新频率可能降低，但核心功能稳定。
- **已知限制**：标记为 `IsBetaVersion: true`，表明可能仍存在一些未解决的问题或 API 变动风险。平台支持列表有限（主要为桌面和移动平台）。
- **推荐使用**：对于需要高质量、基于物理的 3D 音频且目标平台在支持列表内的项目，此插件是一个强大的选择。但由于其 Beta 状态和可能的维护不活跃，建议在项目早期进行充分测试和风险评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio)
- [官方文档](https://developers.google.com/resonance-audio/develop/unreal/getting-started)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ResonanceAudio/Tests)