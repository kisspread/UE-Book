# Launcher Chunk Installer

> Chunk installer module that hooks into launcher

| 属性 | 值 |
|---|---|
| 中文名 | 启动器分块安装器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LauncherChunkInstaller` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-24 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller) | |

## 用途

此插件提供了一个特定于 Epic Games 启动器的分块（Chunk）安装器实现。它通过继承 `FGenericPlatformChunkInstall` 并覆盖其 `GetChunkLocation` 方法，使得 Unreal Engine 能够确定在 Epic 启动器分发环境下，游戏数据块（Chunk）的物理存储路径。其核心作用是让引擎知道去哪里加载特定的游戏内容数据，是实现“按需下载”或“分块加载”功能在启动器平台上的关键一环。

## 使用场景

此插件主要服务于通过 **Epic Games Launcher** 分发和运行游戏的场景。
- 当你的游戏作为产品发布在 Epic Games Store 上，并且启用了“分块下载”功能以减少初始下载大小时，此插件会被引擎自动使用。
- 作为一个平台抽象层的具体实现，开发者通常**无需直接与之交互**。引擎的资产管理器和流式加载系统会在后台调用它来确定资源位置。

## 蓝图用法

无公开蓝图API。该插件的功能完全在引擎内部集成，不暴露给蓝图可视化脚本系统。

## C++ 用法

开发者通常不需要直接使用此类，引擎的基础设施会自动调用。其代码结构如下：

### 头文件引入

```cpp
#include "LauncherChunkInstaller.h"
```

### 基本用法

该类的主要作用是为 `FGenericPlatformChunkInstall` 接口提供一个具体的、针对 Epic 启动器的实现。其核心是覆盖一个虚函数。

**来源文件**: `Engine/Plugins/Portal/LauncherChunkInstaller/Source/LauncherChunkInstaller/Public/LauncherChunkInstaller.h`

```cpp
// 此类继承自平台通用的分块安装器接口
class FLauncherChunkInstaller : public FGenericPlatformChunkInstall
{
public:
    // 覆盖虚函数，返回指定 ChunkID 的物理存储位置
    UE_API virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override;
};
```

### 进阶用法

（无更复杂的用法，此插件功能单一且专用于启动器平台。）

## Demo 示例

此插件为引擎内部使用的平台抽象实现，无独立使用示例。其行为由引擎的 **ChunkDownloader** 子系统和平台层隐式调用。

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。此插件模块实现轻量，主要依赖引擎底层的分块管理框架。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `29f9ae30` | Enable LinuxArm64 MergeModules server builds. | 为 LinuxArm64 平台的合并模块服务器构建启用此插件。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i... | 将所有导出的类方法和静态变量标记为 DLL 存储，以适配模块化构建。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件目录的常规重组或更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内链接为安全协议（HTTPS）。 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 从引擎发布分支合并代码到测试分支。 |

### 维护评价

该插件创建于 2018 年，属于引擎的底层平台基础设施。最近的更新均为维护性质（如编译警告修复、平台支持扩展、链接更新），**自创建以来未发现有明确的功能性变更记录**。这表明其接口和功能已经非常稳定。作为 Epic Games Launcher 集成的关键一环，它仍被支持（体现在平台列表的维护），但已不处于活跃的功能开发阶段。对于使用 Epic Games Launcher 分发游戏的开发者，此插件是隐式依赖且可靠的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller)