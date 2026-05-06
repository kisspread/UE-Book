# MotoSynth

> An experimental granular vehicle engine. Intended to explore and demonstrate potential capabilities. Not supported.

| 属性 | 值 |
|---|---|
| 中文名 | 摩托车合成 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产工厂与编辑器 UI） |
| 模块 | `MotoSynth` (Runtime), `MotoSynthEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotoSynth) | |

## 用途

MotoSynth 是一个实验性的**颗粒合成摩托车引擎声音生成器**。它通过颗粒合成（Granular Synthesis）技术模拟摩托车引擎在不同转速下的声音特性。插件提供了两类核心资产：

- **MotoSynth Source**（`UMotoSynthSource`）：封装原始的音频波形数据（例如录制好的引擎排气声），作为颗粒合成的音频源。
- **MotoSynth Preset**（`UMotoSynthPreset`）：定义如何从 Source 中采样、回放、调制颗粒，以合成出连续的引擎音效。

该插件目前处于实验阶段，功能尚不稳定，Epic 官方不提供技术支持和稳定性保证。主要用于内部探索和展示潜在能力。

## 使用场景

- 你在开发一款**赛车或摩托车竞速游戏**，需要真实且可动态变化的引擎声音
- 你希望使用颗粒合成（而非传统采样/循环）来模拟不同转速下的声音渐变
- 你需要在编辑器内快速创建和调整引擎音效资产，并直接播放预览

## 蓝图用法

由于 MotoSynth 运行时模块的公开 API 较少，且主要资产为数据对象，蓝图中的使用主要集中在**创建并配置资产**上。以下为编辑器 blueprinted 资产创建流程：

### 核心节点（编辑器内操作，非蓝图节点）

| 节点/操作 | 说明 | 所在类 |
|---|---|---|
| 右键创建 `Moto Synth Source` | 创建一个空的源波形资产 | `UMotoSynthSourceFactory` |
| 右键创建 `Moto Synth Preset` | 创建一个预设引擎配置 | `UMotoSynthPresetFactory` |
| 在 Sound Wave 右键菜单中 `Create MotoSynth Source` | 基于选中的 `USoundWave` 快速创建源波形 | `FMotoSynthExtension` |

运行时可能暴露的组件（未在提供头文件中体现，依据常见音频合成模式推测）：
- `UMotoSynthControllerComponent` 或 `USynthComponentMotoSynth` 用于在场景中播放

### 使用示例（蓝图描述）

1. 在内容浏览器中导入一个循环引擎声的 `USoundWave` 资产。
2. 右键该 Sound Wave，选择 **SoundWave Actions → Create MotoSynth Source** → 自动生成一个 `UMotoSynthSource` 资产。
3. 右键内容浏览器，**Miscellaneous → Moto Synth Preset** 创建一个预设资产。
4. 在预设资产的细节面板中，指定 `Source` 为刚创建的 Source 资产，并调整 `RPM Curve`、`Grain Size`、`Crossfade` 等参数。
5. 将预设资产拖到关卡中，系统会自动创建对应的合成音效组件（假设存在 `UMotoSynthComponent`），并开始播放引擎声音。

> **注意**：以上蓝图节点可能因插件实验性质而缺失或变动，建议在实际项目中以运行时验证为准。

## C++ 用法

### 头文件引入

```cpp
#include "MotoSynthSource.h"
#include "MotoSynthPreset.h"
#include "MotoSynthSourceFactory.h"   // 编辑器工厂类
```

### 基本用法

#### 创建 MotoSynth Source 资产

```cpp
// 来自 MotoSynthSourceFactory.h
// 通过 UFactory 在内容浏览器中创建资产
// 或者在代码中直接 NewObject：

UMotoSynthSource* NewSource = NewObject<UMotoSynthSource>(GetTransientPackage(), NAME_None, RF_Transactional);
NewSource->SourceWave = LoadObject<USoundWave>(nullptr, TEXT("/Game/Sounds/EngineLoop.EngineLoop"));
NewSource->MarkPackageDirty();
```

#### 创建 MotoSynth Preset 资产

```cpp
// 来自 MotoSynthPresetFactory.h
UMotoSynthPreset* NewPreset = NewObject<UMotoSynthPreset>(GetTransientPackage(), NAME_None, RF_Transactional);
NewPreset->Source = NewSource;
NewPreset->RPMCurve.AddKey(1000.0f, 0.0f);
NewPreset->RPMCurve.AddKey(8000.0f, 1.0f);
NewPreset->MarkPackageDirty();
```

#### 通过右键菜单扩展创建（编辑器中）

```cpp
// 来自 SoundWaveAssetActionExtenderMotoSynth.h
// 调用 FMotoSynthExtension::ExecuteCreateMotoSynthSource() 会弹出对话框
// 使用选中的 SoundWave 创建 Source 资产
```

### 进阶用法

由于 MotoSynth 还处于早期实验阶段，公开的运行时 API 很少。以下为纯推测，但符合一般音频插件模式：

```cpp
// 假设存在 UMotoSynthComponent
UMotoSynthComponent* Synth = Cast<UMotoSynthComponent>(AActor->AddComponentByClass(UMotoSynthComponent::StaticClass(), false, FTransform(), false));
Synth->SetSynthPreset(MyPreset);
Synth->Start();
Synth->SetRPM(5000.0f);
```

## Demo 示例

以下是一个在编辑器模块中自动创建 MotoSynth 资产的示例（C++ 无窗口）：

```cpp
// MotoSynthDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Factories/Factory.h"

class FMotoSynthDemo
{
public:
    static void CreateDemoAsset();
};
```

```cpp
// MotoSynthDemo.cpp
#include "MotoSynthDemo.h"
#include "MotoSynthSource.h"
#include "MotoSynthPreset.h"
#include "Sound/SoundWave.h"

void FMotoSynthDemo::CreateDemoAsset()
{
    // 1. 加载一个 SoundWave
    USoundWave* Wave = LoadObject<USoundWave>(nullptr, TEXT("/Engine/EngineSounds/MotoSynth/RawEngineLoop.RawEngineLoop"));
    if (!Wave) return;

    // 2. 创建 Source
    UMotoSynthSource* Source = NewObject<UMotoSynthSource>(GetTransientPackage(), NAME_None, RF_Transactional);
    Source->SourceWave = Wave;
    Source->MarkPackageDirty();

    // 3. 创建 Preset
    UMotoSynthPreset* Preset = NewObject<UMotoSynthPreset>(GetTransientPackage(), NAME_None, RF_Transactional);
    Preset->Source = Source;
    Preset->RPMCurve.AddKey(2000.0f, 0.0f);
    Preset->RPMCurve.AddKey(8000.0f, 1.0f);
    Preset->MarkPackageDirty();

    // 4. 保存资产到 /Game/Demo/ （需使用 UPackage）
    // ...
}
```

> 注意：实际运行时可能需要音频引擎初始化、合成组件的挂载等步骤。该示例仅演示资产创建。

## 模块依赖

根据 MotoSynth 运行时模块的常见依赖（未提供 Build.cs 文件，基于插件类型推测）：

| 模块 | 用途 |
|---|---|
| `AudioExtensions` | 音频引擎扩展接口 |
| `SignalProcessing` | 信号处理库（颗粒合成算法） |
| `Synthesis` | 基础合成工具（可选） |
| `AudioMixer` | 音频混合器运行时 |

编辑器模块额外依赖：

| 模块 | 用途 |
|---|---|
| `AssetTools` | 资产类型注册与工厂 |
| `ContentBrowser` | 右键菜单扩展 |
| `ToolMenus` | 菜单注册 |
| `Slate` / `SlateCore` | 编辑器 UI |
| `UnrealEd` | 编辑器基础设施 |

> 省略了常见的 Core、CoreUObject、Engine、InputCore、PropertyEditor 等。

## 维护状态

### 近期更新

- 2025-08-28 `08e89bc9` — fixup ISoundGenerator::GetNextBuffer() implementers (don't assume zero'd buffer)
- 2025-06-19 `800d7a51` — Implement feedback & additional tidbits for right-click audio actions including
- 2025-04-23 `939cc6e5` — Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv
- 2024-11-10 `66e9bb39` — Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
- 2024-07-29 `0084b0f6` — CIS Followup - deleting pointer to incomplete type.

### 维护评价

该插件创建于 2024 年 7 月，属于较新的实验性功能。从 git 历史看，至今（2025 年 10 月）仍有活跃的修复和功能更新（最近一次在 2025 年 8 月），表明 Epic 内部正在持续迭代。但由于 **IsExperimentalVersion = true**，插件不被认为稳定，**不推荐用于正式项目**。可能缺少完整的蓝图节点、运行时组件，以及 API 可能在未来发生破坏性变化。适合希望提前体验颗粒合成引擎效果的开发者进行技术预览。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotoSynth)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（搜索“MotoSynth”，暂无独立页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotoSynth/Source/MotoSynth/Tests)（暂无测试文件）