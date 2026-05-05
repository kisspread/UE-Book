# Sound Module Plugin

> Supports playback of ProTracker (MOD), Scream Tracker 3 (S3M), Fast Tracker II (XM), and Impulse Tracker (IT) files.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ `CanContainContent: false` |
| 模块 | SoundMod (Runtime), SoundModImporter (Editor) |
| 创建时间 | 2014-06-13 |
| 年龄标签 | 🏛️ 文物 (>10年) |
| 平台 | Win64, Mac, Linux, Android |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundMod) | |

## 用途

SoundMod 插件让 UE5 能够播放 **Tracker 模块音乐文件**——一种在 90 年代流行的音乐格式（MOD/S3M/XM/IT）。这些格式与常见的 WAV/MP3 不同，它们存储的是采样数据 + 播放指令序列（类似"音频版 MIDI"），文件体积非常小，适合对音频文件大小敏感的场景。

插件内部使用 [libxmp](http://xmp.sourceforge.net/)（打包为 `coremod` 第三方库）来解码和播放模块文件。导入时会通过 libxmp 验证文件合法性并提取时长信息，播放时通过 `USoundModWave`（继承自 `USoundWaveProcedural`）实时生成 44100Hz 双声道 PCM 数据。

> ⚠️ **注意**：此插件默认不启用。使用前需要在项目设置或 .uproject 中手动启用 `"SoundMod"` 插件。

## 使用场景

- 你正在移植一款使用 MOD/S3M/XM/IT 格式音乐的老游戏 → 直接导入原文件即可播放
- 你需要极小体积的背景音乐（tracker 文件通常比同等质量的 MP3 小很多）→ 用 tracker 格式替代传统音频格式
- 你正在制作复古风格游戏，想使用 chiptune / tracker 社区的音乐资源 → 导入 .mod/.xm/.it 文件作为 Sound Asset
- 你需要在 Sound Cue 中混入 tracker 音乐与其他音效 → 使用 Mod Player 节点

## 支持的文件格式

| 扩展名 | 格式 | 说明 |
|---|---|---|
| `.mod` | ProTracker | Amiga 经典格式 |
| `.s3m` | Scream Tracker 3 | DOS 时代流行格式 |
| `.xm` | Fast Tracker II | 支持多采样乐器 |
| `.it` | Impulse Tracker | 功能最丰富的 tracker 格式 |

## 编辑器用法

### 导入文件

1. 在 Content Browser 中右键 → **Import**
2. 选择 `.mod`、`.s3m`、`.xm` 或 `.it` 文件
3. 导入后生成 `USoundMod` 资产（图标与普通 Sound Wave 类似）

### 预览播放

- 双击资产或在 Content Browser 中选中后按 **Space** 即可预览播放
- 右键资产可以看到 **Play** / **Stop** 菜单项

### 蓝图用法

此插件**没有暴露任何 `BlueprintCallable` 函数**。在蓝图中使用 tracker 音乐的方式与普通音频资产一致：

1. 将导入的 `USoundMod` 资产拖入 Sound Cue 编辑器，使用 **Mod Player** 节点
2. 或在 Actor 上添加 **Audio Component**，将 `Sound` 属性设为 `USoundMod` 资产

### Sound Cue 中的 Mod Player 节点

在 Sound Cue 编辑器中，可以添加 **Mod Player** 节点（`USoundNodeModPlayer`）：

| 属性 | 说明 |
|---|---|
| Sound Mod | 引用一个 `USoundMod` 资产 |
| Looping | 是否循环播放 |

Mod Player 节点是叶子节点（没有子节点输入），只能作为音频源使用。

## C++ 用法

### 头文件引入

```cpp
#include "SoundMod.h"            // USoundMod 资产类
#include "SoundNodeModPlayer.h"  // Sound Cue 节点
```

### 模块依赖（Build.cs）

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "SoundMod",
    "AudioExtensions",
    "Core",
    "CoreUObject",
    "Engine"
});
```

> ⚠️ 如果你需要在模块中引用 `USoundMod`，需要依赖 `SoundMod` 模块。libxmp 的链接由插件内部通过 `coremod` 第三方库自动处理。

### 基本用法

在代码中加载并使用 tracker 音乐资产：

```cpp
#include "SoundMod.h"

// 异步加载 USoundMod 资产
TSoftObjectPtr<USoundMod> ModAsset(
    FSoftObjectPath("/Game/Audio/MyTrackerMusic.MyTrackerMusic"));

// 同步加载（简单示例）
USoundMod* SoundMod = ModAsset.LoadSynchronous();
if (SoundMod)
{
    // USoundMod 继承自 USoundBase，可以直接用于 PlaySound
    UGameplayStatics::PlaySound2D(this, SoundMod);
}
```

### 在 Sound Cue 中使用 Mod Player

```cpp
#include "SoundNodeModPlayer.h"

// 创建 Mod Player 节点
USoundNodeModPlayer* ModPlayer = NewObject<USoundNodeModPlayer>();
ModPlayer->SetSoundMod(MySoundMod);
ModPlayer->bLooping = true;

// 将节点添加到 Sound Cue（需要在 Sound Cue 编辑器中操作，代码方式较少使用）
```

### 检测插件是否可用

```cpp
#include "SoundModPlugin.h"

if (ISoundModPlugin::IsAvailable())
{
    // 插件已加载，可以安全使用 USoundMod
}
```

## 源码架构

插件分为两个模块：

```
SoundMod/
├── Source/
│   ├── SoundMod/                    # Runtime 模块
│   │   ├── Classes/
│   │   │   ├── SoundMod.h           # USoundMod — 资产类，存储 MOD 文件原始数据
│   │   │   └── SoundModWave.h       # USoundModWave — 程序化音频生成（PCM 输出）
│   │   ├── Public/
│   │   │   ├── SoundNodeModPlayer.h # Sound Cue 中的 Mod Player 节点
│   │   │   └── SoundModPlugin.h     # 模块接口
│   │   └── Private/
│   │       ├── SoundMod.cpp         # 资产解析，创建 xmp_context 并加载模块
│   │       ├── SoundModWave.cpp     # 实时 PCM 数据生成（调用 xmp_play_frame）
│   │       ├── SoundNodeModPlayer.cpp
│   │       └── SoundModPlugin.cpp
│   └── SoundModImporter/            # Editor 模块
│       ├── Classes/
│       │   └── SoundModImporterFactory.h
│       └── Private/
│           ├── SoundModImporterFactory.cpp  # 工厂类，处理 .mod/.s3m/.xm/.it 导入
│           ├── AssetTypeActions_SoundMod.cpp # Content Browser 右键菜单（Play/Stop）
│           └── SoundModImporterModule.cpp
```

### 核心类关系

```
USoundBase (Engine)
  └── USoundMod (SoundMod)          — 资产，持有 FByteBulkData 原始模块数据
        └── 创建 USoundModWave      — 程序化音频对象
              └── 调用 libxmp       — xmp_play_frame() 生成 PCM

USoundNodeAssetReferencer (Engine)
  └── USoundNodeModPlayer           — Sound Cue 节点，引用 USoundMod
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioExtensions` | 音频扩展框架 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（SoundBase、AudioComponent 等） |
| `coremod`（第三方库） | libxmp — tracker 模块文件解码与播放 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator | 静态分析警告修复，三元运算符临时对象问题 |
| 2025-05-27 | `5961ff5b` | Fix for loctext collision #jira UE-290562 | LOCTEXT 命名空间冲突修复，小问题 |
| 2023-05-16 | `381f77ac` | Optimized include module name dependencies | 优化头文件依赖，编译性能改进 |

### 维护评价

- **创建时间**：2014 年 6 月，距今超过 11 年，属于 🏛️ 文物级插件
- **维护状态**：**维护不活跃**。最近 3 次提交均为编译器警告修复或小问题修复，没有功能性更新。最近一次实质性代码改动在 2023 年，已经 2 年以上没有功能更新。
- **是否推荐使用**：⚠️ **有条件推荐**。插件功能完整且稳定，能够正常工作。但属于极小众功能（tracker 格式在现代游戏开发中几乎不再使用），Epic 不太可能投入资源维护。如果你确实需要播放 tracker 文件，可以放心使用；如果是新项目，建议考虑将音乐转换为 WAV/OGG 等主流格式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundMod)
- [libxmp 官网](http://xmp.sourceforge.net/) — 插件使用的 tracker 回放库
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 测试用例：无（未找到相关自动化测试）
