# Steam Audio (Deprecated)

> This plugin is deprecated and will be removed in a future engine release. Please use the plugin from Valve's website.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | SteamAudio (Runtime) |
| 创建时间 | 2017-05-02 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamAudio) | |

## 用途

这是 Epic 内置的 Steam Audio 集成模块的**残留存根**。该模块本身几乎不包含任何实质功能代码——它仅在启动时输出一条弃用警告日志，然后将音频处理交给 Phonon 第三方库和 UE 的 AudioMixer 系统。

**核心问题**：Steam Audio（原名 Phonon）是由 Valve 开发的 3D 音频空间化与声学仿真库，支持基于物理的混响、遮挡、衍射和 HRTF 空间化。UE4 时代 Epic 曾内置此集成插件，但从 UE5 起该内置版本已被标记为弃用（`IsBetaVersion: true`, `EnabledByDefault: false`），模块代码仅剩启动/关闭生命周期管理，所有实际功能已被剥离。

**当前状态**：不应使用此内置插件。Steam Audio 的官方 UE 集成应从 [Valve 官网](https://valvesoftware.github.io/steam-audio) 获取，该版本包含完整的烘焙、实时仿真和蓝图接口。

## 使用场景

- ~~你在做一个需要真实声学效果的 VR 游戏（混响、遮挡、HRTF）→ 用 Steam Audio~~（请使用 Valve 官方版本）
- 此内置插件**不提供**任何可用功能，仅作为编译兼容性的存根存在
- 如果你的项目已启用此插件，建议禁用并迁移到 Valve 的独立插件

## 蓝图用法

此插件**不暴露任何蓝图接口**。源码中无 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 声明。

## C++ 用法

### 头文件引入

```cpp
#include "ISteamAudioModule.h"
```

### 基本用法

此模块仅提供标准的 `IModuleInterface` 生命周期方法，无业务 API：

```cpp
// 检查模块是否已加载
if (ISteamAudioModule::IsAvailable())
{
    // 获取模块实例（通常不需要）
    ISteamAudioModule& Module = ISteamAudioModule::Get();
}
```

模块启动时会输出弃用警告：

```
LogSteamAudio: Warning: The Steam Audio plugin is deprecated and will be removed in a future engine release. Get Valve's version here: https://valvesoftware.github.io/steam-audio/doc/unreal/getting-started.html
```

### 进阶用法

无进阶用法。此插件不提供任何可编程接口。

## Demo 示例

不适用。此插件为弃用存根，无可演示功能。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `AudioMixer` | 音频混音器系统 |
| `InputCore` | 输入核心 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `AudioExtensions` | 音频扩展接口（私有依赖） |
| `libPhonon` | Steam Audio 核心第三方库（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-03 | `f4b398bd` | Disable deprecated Steam Audio plugin on Windows Arm64 | 在 Win64:arm64 平台上禁用此插件，因为 Phonon 库不支持 ARM 架构 |
| 2025-04-21 | `751c281d` | oneTBB, Embree, OpenVDB: activate new library versions | 第三方库版本更新波及此插件的构建配置 |
| 2025-03-27 | `093ea461` | Embree: remove unused 2.7.0 version | 第三方库清理，非直接功能更新 |

### 维护评价

- **创建时间**：2017 年 5 月，已有 9 年历史
- **当前状态**：**已弃用（Deprecated）**——`.uplugin` 的 FriendlyName 明确标注 "Deprecated"，Description 声明将在未来版本移除
- **代码活跃度**：近 3 次提交均为构建配置调整（平台禁用、第三方库版本同步），无任何功能开发
- **实质代码量**：仅 3 个源文件（1 个模块头文件、1 个实现头文件、1 个 cpp），总计约 80 行有效代码，仅为存根
- **推荐**：**不推荐使用**。应迁移到 Valve 官方提供的独立 Steam Audio UE 插件，该插件包含完整的烘焙工具、实时仿真、蓝图接口和编辑器集成

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamAudio)
- [Valve 官方 Steam Audio UE 插件](https://valvesoftware.github.io/steam-audio/doc/unreal/getting-started.html)
- [Steam Audio 官网](https://valvesoftware.github.io/steam-audio)
