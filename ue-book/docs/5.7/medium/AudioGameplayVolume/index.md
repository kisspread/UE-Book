# Audio Gameplay Volume

> Audio Gameplay Volume Plugin

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioGameplayVolume` (Runtime), `AudioGameplayVolumeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-27 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioGameplayVolume) | |

## 用途

AudioGameplayVolume 插件提供了一套**基于空间区域的音频行为系统**，用于让音频效果随玩家（音频监听器）的位置动态变化。

核心解决的问题：当玩家从室外走入室内时，你需要自动调整混响、音量衰减、低通滤波、Submix 路由等音频参数。传统的 `AudioVolume` Actor 只能配合 Reverb Volume 使用，而 AudioGameplayVolume 提供了更灵活、可组合的组件化方案——每个 Volume 可以挂载多个 Mutator 组件（混响、滤波、衰减、Submix 发送/覆盖），这些组件会根据监听器是否在 Volume 内部自动生效。

系统还有一个重要概念：**Audio Toggle**（`UAudioGameplayVolumeComponent`）。它不局限于物理空间检测，还支持任意条件（`IAudioGameplayCondition` 接口）来决定 Toggle 的 On/Off 状态，使得音频行为可以绑定到任意游戏逻辑上。

> **注意**：该插件标记为 `IsBetaVersion: true`，仍在实验阶段。Sound Class 中需要设置 "Apply Ambient Volumes" 才能让音源受到 Volume 影响。

## 使用场景

- 你做了一个开放世界游戏，玩家可以从室外走进建筑物 → 在建筑物内放置 AudioGameplayVolume，挂载 Reverb + Filter + Attenuation 组件，自动获得室内音效
- 你需要根据玩家位置动态调整 Submix 效果链（比如水下/洞穴环境） → 使用 SubmixOverrideVolumeComponent
- 你需要将音频源的声音发送到特定 Submix 做后期处理（如回声/混响 bus） → 使用 SubmixSendVolumeComponent
- 你想基于非空间条件（比如某个开关状态）来切换音频行为 → 使用 Audio Toggle + Arbitrary 条件代理

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnabled` | 启用/禁用 Volume | `AAudioGameplayVolume` |
| `OnListenerEnter` | 蓝图事件：监听器进入 Volume | `AAudioGameplayVolume` |
| `OnListenerExit` | 蓝图事件：监听器离开 Volume | `AAudioGameplayVolume` |
| `On Toggled On` | 蓝图事件：Toggle 变为 On | `UAudioGameplayVolumeComponent` |
| `On Toggled Off` | 蓝图事件：Toggle 变为 Off | `UAudioGameplayVolumeComponent` |
| `SetReverbSettings` | 运行时修改混响设置 | `UReverbVolumeComponent` |
| `SetExteriorLPF` | 设置外部低通滤波频率和插值时间 | `UFilterVolumeComponent` |
| `SetInteriorLPF` | 设置内部低通滤波频率和插值时间 | `UFilterVolumeComponent` |
| `SetExteriorVolume` | 设置外部音量衰减和插值时间 | `UAttenuationVolumeComponent` |
| `SetInteriorVolume` | 设置内部音量衰减和插值时间 | `UAttenuationVolumeComponent` |
| `SetSubmixSendSettings` | 运行时修改 Submix 发送设置 | `USubmixSendVolumeComponent` |
| `SetSubmixOverrideSettings` | 运行时修改 Submix 覆盖设置 | `USubmixOverrideVolumeComponent` |
| `SetPriority` | 设置 Mutator 优先级（重叠时高优先级生效） | `UAudioGameplayVolumeMutator` |

### 使用示例（蓝图描述）

**基本室内音效设置：**

1. 在场景中放置一个 `AudioGameplayVolume` Actor（它是 Brush Volume，和 AudioVolume 类似）
2. 在 Actor 上添加 `ReverbVolumeComponent`（蓝图中显示为 "Reverb"），设置混响预设
3. 添加 `AttenuationVolumeComponent`（显示为 "Interior-Exterior Attenuation"），设置 InteriorVolume=1.0, ExteriorVolume=0.3, ExteriorTime=1.0
4. 添加 `FilterVolumeComponent`（显示为 "Filter"），设置 ExteriorLPF=2000 Hz
5. 玩家进入 Volume 时，外部声音自动变安静且加上低通滤波

**使用 Audio Toggle 自定义条件：**

1. 在任意 Actor 上添加 `UAudioGameplayVolumeComponent`（显示为 "Audio Toggle"）
2. 将 Toggle Condition 设为 "Arbitrary"（`UAGVConditionProxy`）
3. 在同一个 Actor 上实现 `IAudioGameplayCondition` 接口
4. 绑定 `On Toggled On` / `On Toggled Off` 事件到你的自定义逻辑

## C++ 用法

### 头文件引入

```cpp
#include "AudioGameplayVolume.h"
#include "AudioGameplayVolumeComponent.h"
#include "ReverbVolumeComponent.h"
#include "FilterVolumeComponent.h"
#include "AttenuationVolumeComponent.h"
#include "SubmixSendVolumeComponent.h"
#include "SubmixOverrideVolumeComponent.h"
```

### 基本用法

创建一个带混响和衰减的 AudioGameplayVolume：

```cpp
// 在场景中 Spawn 一个 AudioGameplayVolume
FActorSpawnParameters SpawnParams;
AAudioGameplayVolume* Volume = GetWorld()->SpawnActor<AAudioGameplayVolume>(
    AAudioGameplayVolume::StaticClass(), SpawnTransform, SpawnParams);

// 获取其内置的 AGV Component
UAudioGameplayVolumeComponent* AGVComp = Volume->FindComponentByClass<UAudioGameplayVolumeComponent>();

// 添加混响组件
UReverbVolumeComponent* ReverbComp = NewObject<UReverbVolumeComponent>(Volume, TEXT("Reverb"));
ReverbComp->RegisterComponent();
FReverbSettings ReverbSettings;
ReverbSettings.bApplyReverb = true;
ReverbSettings.ReverbEffect = LoadObject<UReverbEffect>(nullptr, TEXT("/Game/Audio/MyReverbEffect"));
ReverbSettings.Volume = 0.7f;
ReverbComp->SetReverbSettings(ReverbSettings);

// 添加衰减组件
UAttenuationVolumeComponent* AttenComp = NewObject<UAttenuationVolumeComponent>(Volume, TEXT("Attenuation"));
AttenComp->RegisterComponent();
AttenComp->SetInteriorVolume(1.0f, 0.5f);   // 内部音量 100%, 0.5秒插值
AttenComp->SetExteriorVolume(0.2f, 1.0f);   // 外部音量 20%, 1秒插值
```

### 进阶用法

使用 AudioGameplayVolumeComponentBase 创建自定义 Volume 组件：

```cpp
// 自定义 Volume 组件，响应监听器进出
UCLASS()
class UMyCustomVolumeComponent : public UAudioGameplayVolumeComponentBase
{
    GENERATED_BODY()

public:
    // 重写 IAudioGameplayVolumeInteraction 接口方法
    virtual void OnListenerEnter() override
    {
        // 播放进入音效、触发游戏逻辑等
        UE_LOG(LogTemp, Log, TEXT("Listener entered custom volume!"));
    }

    virtual void OnListenerExit() override
    {
        UE_LOG(LogTemp, Log, TEXT("Listener exited custom volume!"));
    }
};
```

使用 `IActiveSoundUpdateInterface` 通过 Subsystem 直接查询音频设置：

```cpp
// 通过 Subsystem 搜索某个位置的 Mutator
if (UAudioGameplayVolumeSubsystem* Subsystem = GEngine->GetEngineSubsystem<UAudioGameplayVolumeSubsystem>())
{
    FAudioProxyMutatorSearchObject SearchObj;
    SearchObj.Location = ListenerPosition;
    SearchObj.WorldID = GetWorld()->GetUniqueID();
    SearchObj.PayloadType = AudioGameplay::EComponentPayload::AGCP_All;
    SearchObj.bCollectMutators = true;

    FAudioProxyMutatorSearchResult SearchResult;
    // 注意：SearchVolumes 在音频线程上调用
}
```

## Demo 示例

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "AudioGameplayVolume"
});
```

### 最小示例：自定义 Volume 组件

**MyAudioVolumeComponent.h**

```cpp
#pragma once

#include "AudioGameplayVolumeComponent.h"
#include "MyAudioVolumeComponent.generated.h"

UCLASS(ClassGroup = (AudioGameplay), meta = (BlueprintSpawnableComponent))
class UMyAudioVolumeComponent : public UAudioGameplayVolumeComponentBase
{
    GENERATED_BODY()

public:
    virtual void OnListenerEnter() override
    {
        // 监听器进入了 Volume
        // 在此触发你的音频行为
    }

    virtual void OnListenerExit() override
    {
        // 监听器离开了 Volume
    }
};
```

将此组件添加到任意 Actor 上，当音频监听器进入该 Actor 的 Primitive 组件范围时，`OnListenerEnter` 会被调用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎核心（公共依赖） |
| `AudioGameplay` | 音频游戏玩法基础框架（AudioGameplayComponent 等基类） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Volume、Sound、Submix 等） |
| `ToolMenus` | 编辑器菜单扩展（Editor 模块） |
| `UnrealEd` | 编辑器功能（Editor 模块） |
| `Slate` / `SlateCore` | UI 框架（Editor 模块 Detail 自定义） |
| `PropertyEditor` | 属性面板自定义（Editor 模块） |

> **注意**：该插件依赖 `AudioGameplay` 插件（在 .uplugin 中声明），确保你的项目启用了 `AudioGameplay`。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-20 | `1746b7434e` | **大规模重命名和 UI 优化**：Volume Proxy → Audio Toggle、AGV Primitive Proxy → Audio Listener In Primitives、Attenuation → Interior-Exterior Attenuation；增加批量进出通知；更新工具提示 |
| 2025-06-11 | `e0d87df85d` | 替换部分 `FORCEINLINE` 为 `inline`（代码规范化） |
| 2025-05-14 | `aa6721a77b` | AGV Subsystem 增加 CVar 选项，防止重复 Submix Send 被添加到同一个音源 |

### 维护评价

- **创建时间**：2021-10-27，约 5 年历史
- **维护状态**：**活跃维护**。2025 年有多次功能性更新，包括大规模重命名、UI 优化、新功能添加
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，仍标记为实验性
- **推荐程度**：⚠️ **有条件推荐**。功能完善且持续更新，但 Beta 标签意味着 API 可能在未来版本发生变化。对于需要空间化音频行为的项目，这是目前 UE5 中最完善的方案，替代了旧版 AudioVolume 的部分功能。建议关注版本升级时的 Breaking Changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioGameplayVolume)
- 官方文档（无）
- 测试用例（无）
