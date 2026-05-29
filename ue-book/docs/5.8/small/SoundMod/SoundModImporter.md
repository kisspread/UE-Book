# Sound Module Plugin

> Supports playback of ProTracker (MOD), Scream Tracker 3 (S3M), Fast Tracker II (XM), and Impulse Tracker (IT) files.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐模块播放器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SoundMod` (Runtime), `SoundModImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-06-13 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundMod) | |

## 用途

这个插件用于在 UE5 中播放**追踪器（Tracker）音乐格式**文件。追踪器音乐是上世纪 80-90 年代流行的模块化音乐格式，在 demoscene（演示场景）和早期游戏音轨制作中被广泛使用。与现代音频格式不同，追踪器文件将采样数据和播放指令（音符、效果命令）打包在一起，文件体积非常小，适合游戏嵌入。

插件支持以下四种经典追踪器格式：

- **MOD**（ProTracker）：Commodore Amiga 平台的标志性格式，几乎所有追踪器格式的鼻祖
- **S3M**（Scream Tracker 3）：DOS 平台流行格式，支持更多通道和效果
- **XM**（Fast Tracker II）：支持多采样乐器和高级效果，非常流行的 DOS 格式
- **IT**（Impulse Tracker）：功能最强大的 DOS 追踪器格式，支持压缩采样和高级音量/声像控制

Runtime 模块负责这些格式的解码和播放，Editor 模块（SoundModImporter）负责将这些文件作为资产导入编辑器。

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要在插件设置中手动启用。且仅支持 Win64、Mac、Linux 和 Android 平台。

## 使用场景

- 你正在移植一个使用 MOD/S3M/XM/IT 音乐的复古游戏 → 用 SoundMod 导入并播放原始追踪器文件
- 你制作独立游戏想要使用复古风格的芯片音乐（chiptune），手头有追踪器格式的音乐文件 → 用 SoundMod
- 你在制作 demoscene 风格的演示项目 → 用 SoundMod 播放经典模块音乐
- 你有一个体积限制严格的项目，需要比 MP3/OGG 更小的音轨方案 → 追踪器格式文件通常只有几十 KB

## 蓝图用法

基于源码分析，该插件的蓝图 API 较为有限。编辑器侧主要提供资产操作，Runtime 侧的蓝图接口在提供的代码片段中未暴露明显的 `BlueprintCallable` 函数。

### 编辑器资产操作

在内容浏览器中导入 `.mod`、`.s3m`、`.xm`、`.it` 文件后，会自动生成 `USoundMod` 类型的资产。右键菜单提供以下操作：

| 操作 | 说明 |
|---|---|
| Play Sound | 在编辑器中预览播放该追踪器音乐 |
| Stop Sound | 停止当前正在播放的预览 |

### 使用方式

1. 将 `.mod` / `.s3m` / `.xm` / `.it` 文件拖入内容浏览器
2. 自动生成 `USoundMod` 资产
3. 在蓝图中通过 `PlaySound` 等标准音频节点使用（需要参考 SoundMod Runtime 模块的具体暴露接口）

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块 - 播放功能
#include "SoundMod.h"

// Editor 模块 - 资产导入（仅编辑器使用）
#include "SoundModImporterPrivate.h"
```

### 基本用法

追踪器文件作为资产导入后，以 `USoundMod` 对象形式存在于内容浏览器中。可以通过标准的 UE 音频播放接口来播放：

```cpp
// 假设已有 USoundMod* SoundModAsset 从内容浏览器获取
USoundMod* SoundModAsset = LoadObject<USoundMod>(nullptr, TEXT("/Game/Audio/MyTrackerSong"));

if (SoundModAsset)
{
    // 使用标准 UGameplayStatics 播放声音
    UGameplayStatics::PlaySound2D(GetWorld(), SoundModAsset);
}
```

### 自定义资产工厂

`SoundModImporter` 模块中的 `USoundModImporterFactory` 负责将原始二进制数据转换为 `USoundMod` 资产：

```cpp
// 工厂类处理二进制数据导入（编辑器内部使用）
// 当用户将 .mod/.s3m/.xm/.it 文件拖入编辑器时，自动调用:
// FactoryCreateBinary(Class, InParent, Name, Flags, Context, Type, Buffer, BufferEnd, Warn)
```

## 模块依赖

### SoundMod（Runtime）

Runtime 模块的具体依赖在提供的信息中未完整展示，但作为音频播放模块，预期依赖：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混音引擎 |
| `AudioModulation` | 音频调制（可能的依赖） |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

### SoundModImporter（Editor）

Editor 模块负责资产导入。

| 模块 | 用途 |
|---|---|
| `SoundMod` | Runtime 播放模块，提供 USoundMod 资产类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and sub | 修复三元运算符编译器警告 |
| 2025-05-27 | `5961ff5b` | Fix for loctext collision | 修复本地化文本键名冲突 |
| 2023-05-16 | `381f77ac` | Optimized include module name dependencies. | 优化模块头文件包含依赖 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 批量引擎插件更新 |
| 2022-12-14 | `96ab5837` | Deprecate use of TUniquePtr in Audio::IProxyData | 废弃音频代理数据中 TUniquePtr 的用法 |

### 维护评价

⚠️ **维护不活跃 — 可能已进入半废弃状态**

- 该插件创建于 **2014 年**，已超过 11 年历史，是 Epic 早期的工具类插件
- 最近一次**功能性更新**是 2022 年 12 月的代理数据接口变更，距今约 3 年
- 2023-2025 年的更新仅限于编译器警告修复、头文件优化和本地化修复，无任何功能改进
- **默认未启用**（`EnabledByDefault: false`），表明 Epic 并不将其视为核心功能
- 追踪器格式属于小众需求，平台支持有限（不包含 iOS、主机平台）
- 由于没有任何 BlueprintCallable API 的明显暴露，蓝图集成可能有限

**建议**：如果你需要在 UE5 中播放追踪器音乐，这个插件仍然可以使用（功能完整），但不要期待新功能或及时的 bug 修复。对于需要更多格式支持或跨平台能力的项目，考虑使用第三方音频库（如 libopenmpt）自行集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundMod)
- [官方文档]()（无）