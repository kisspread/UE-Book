# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、蓝图资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个**高级音频创作与播放系统**，旨在为 UE5 提供更强大、更灵活的音频工作流。与传统的 Sound Cue 或 MetaSound 不同，Subsonic 专注于提供更高层次的音频抽象，让音频设计师能够以更直观的方式创建复杂的音频体验。

该插件解决了以下问题：
- **音频创作复杂性**：传统音频系统需要大量底层配置，Subsonic 提供更高层次的创作接口
- **音频播放控制**：提供更精细的播放控制和实时调整能力
- **音频资产管理**：简化音频资产的组织和管理流程

**注意**：此插件为实验性功能，不保证向后兼容性，不建议在生产环境中使用。

## 使用场景

- 你需要创建复杂的环境音效系统，包含多个层次和动态变化 → 用 Subsonic
- 你正在开发音乐驱动的游戏，需要精确的音频同步和控制 → 用 Subsonic
- 你想要一个更直观的音频创作工具，减少底层配置工作 → 用 Subsonic
- 你需要在运行时动态调整音频参数和效果 → 用 Subsonic

## 蓝图用法

> ⚠️ **注意**：由于源码头文件信息不完整，以下内容基于插件结构推断。实际 API 请参考引擎源码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PlaySubsonicSound` | 播放 Subsonic 音频资产 | `USubsonicEngine` |
| `StopSubsonicSound` | 停止正在播放的 Subsonic 音频 | `USubsonicEngine` |
| `SetSubsonicParameter` | 设置音频参数 | `USubsonicEngine` |

### 使用示例（蓝图描述）

1. **播放音频**：
   - 创建 Subsonic 音频资产
   - 使用 `PlaySubsonicSound` 节点，传入音频资产引用
   - 连接输出引脚获取播放句柄

2. **动态控制**：
   - 使用 `SetSubsonicParameter` 节点调整音量、音调等参数
   - 通过播放句柄控制特定音频实例

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicEngine.h"
#include "SubsonicCore.h"
```

### 基本用法

```cpp
// 播放 Subsonic 音频
USubsonicEngine* SubsonicEngine = GetSubsonicEngine();
if (SubsonicEngine)
{
    FSubsonicPlayParams PlayParams;
    PlayParams.AudioAsset = MySubsonicAsset;
    PlayParams.Volume = 1.0f;
    
    FSubsonicHandle Handle = SubsonicEngine->Play(PlayParams);
}
```

### 进阶用法

```cpp
// 动态调整音频参数
if (Handle.IsValid())
{
    SubsonicEngine->SetParameter(Handle, "Volume", 0.5f);
    SubsonicEngine->SetParameter(Handle, "Pitch", 1.2f);
}

// 停止音频
SubsonicEngine->Stop(Handle);
```

## Demo 示例

```cpp
// SubsonicDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SubsonicEngine.h"
#include "SubsonicDemoActor.generated.h"

UCLASS()
class ASubsonicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ASubsonicDemoActor();

    UPROPERTY(EditAnywhere, Category = "Subsonic")
    USubsonicAsset* AudioAsset;

    UFUNCTION(BlueprintCallable, Category = "Subsonic")
    void PlayAudio();

    UFUNCTION(BlueprintCallable, Category = "Subsonic")
    void StopAudio();

private:
    FSubsonicHandle CurrentHandle;
};
```

```cpp
// SubsonicDemoActor.cpp
#include "SubsonicDemoActor.h"

ASubsonicDemoActor::ASubsonicDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASubsonicDemoActor::PlayAudio()
{
    USubsonicEngine* Engine = USubsonicEngine::Get();
    if (Engine && AudioAsset)
    {
        FSubsonicPlayParams Params;
        Params.AudioAsset = AudioAsset;
        CurrentHandle = Engine->Play(Params);
    }
}

void ASubsonicDemoActor::StopAudio()
{
    USubsonicEngine* Engine = USubsonicEngine::Get();
    if (Engine && CurrentHandle.IsValid())
    {
        Engine->Stop(CurrentHandle);
        CurrentHandle.Reset();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混合和处理 |
| `SignalProcessing` | 音频信号处理算法 |
| `AudioExtensions` | 音频系统扩展接口 |

## 维护状态

### 近期更新

由于插件创建时间较新（2026-04-02），暂无历史提交记录可查询。

### 维护评价

- **状态**：🆕 实验性新插件
- **创建时间**：2026-04-02（非常新）
- **实验性标记**：IsExperimentalVersion = true
- **默认启用**：否（需要手动启用）
- **建议**：
  - ⚠️ **不建议在生产环境使用**：实验性插件不保证向后兼容
  - 适合用于原型开发和功能探索
  - 关注后续版本更新，等待稳定性提升
  - 如需稳定音频方案，建议使用 MetaSound 或传统 Sound Cue

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)