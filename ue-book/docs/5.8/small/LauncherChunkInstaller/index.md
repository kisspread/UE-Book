# Launcher Chunk Installer

> Chunk installer module that hooks into launcher

| 属性 | 值 |
|---|---|
| 中文名 | 启动器块安装器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LauncherChunkInstaller` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-24 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller) | |

## 用途

该插件提供了一个平台块（Chunk）安装器的具体实现，专门用于与 Epic Games 启动器（Launcher）集成。块（Chunk）是 UE 中用于按需加载和流式传输内容（如资产、关卡）的基本单元。`FLauncherChunkInstaller` 类重写了 `FGenericPlatformChunkInstall` 的 `GetChunkLocation` 方法，使得引擎在进行内容流式传输时，能够从启动器管理的特定位置获取块数据，从而实现基于启动器的内容分发和安装管理。

## 使用场景

- 你的游戏通过 Epic Games 启动器发行，并需要支持内容的按需下载和流式加载。
- 你希望利用启动器自身的下载和缓存机制来管理游戏资源的分块加载。
- 你需要在运行时查询特定内容块（Chunk）在磁盘上的确切位置，以配合流式加载系统。

## 蓝图用法

该插件未暴露任何蓝图可调用的函数或属性。其功能主要通过引擎内部的块安装系统和启动器集成机制被动使用。

## C++ 用法

该插件提供的 C++ 接口非常简洁，主要用于被引擎平台抽象层调用。

### 头文件引入

```cpp
#include "LauncherChunkInstaller.h"
```

### 基本用法

该插件的核心是 `FLauncherChunkInstaller` 类，它通常不需要开发者直接实例化或调用。它是平台块安装器系统的一个实现，由引擎在初始化时根据平台和发行渠道（如 Epic Games 启动器）自动选择。

**核心方法：**
`FLauncherChunkInstaller::GetChunkLocation(uint32 ChunkID)` - 根据 ChunkID 返回其存储位置（`EChunkLocation::Type`）。此方法被引擎的流式加载系统调用，以决定从何处加载特定的数据块。

```cpp
// 引擎内部调用示例（概念性，非直接用户代码）
// 当流式加载系统需要知道 ChunkID 为 100 的块位于何处时：
FGenericPlatformChunkInstall* ChunkInstaller = FPlatformMisc::GetPlatformChunkInstall();
if (ChunkInstaller)
{
    EChunkLocation::Type Location = ChunkInstaller->GetChunkLocation(100);
    // 根据 Location（例如在磁盘、需要下载等）采取相应行动
}
```

### 进阶用法

在自定义平台或分发渠道开发中，你可能需要参考此类的实现来创建自己的 `FGenericPlatformChunkInstall` 子类。`GetChunkLocation` 的逻辑决定了游戏内容是被认为已安装、需要按需下载还是位于其他位置（如云存储）。

## Demo 示例

以下示例展示了如何子类化平台块安装器，但请注意，`FLauncherChunkInstaller` 本身是针对启动器的具体实现，通常不需要修改。

```cpp
// MyCustomChunkInstaller.h
#pragma once

#include "GenericPlatform/GenericPlatformChunkInstall.h"

class FMyCustomChunkInstaller : public FGenericPlatformChunkInstall
{
public:
    virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override
    {
        // 你的自定义逻辑，例如检查本地缓存、CDN状态等
        if (IsChunkDownloaded(ChunkID))
        {
            return EChunkLocation::Type::OnDisk;
        }
        return EChunkLocation::Type::NotAvailable;
    }

private:
    bool IsChunkDownloaded(uint32 ChunkID) const
    {
        // 实现你的检查逻辑
        return true;
    }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `29f9ae30` | Enable LinuxArm64 MergeModules server builds. | 为 Linux ARM64 平台启用服务器构建的模块合并功能。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 使用 UnrealGame 构建目标查找并转换文件，为方法/静态变量添加 DLL 导出/导入属性。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件目录的常规维护或批处理更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接以使用安全协议（HTTPS）。 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 从引擎发布暂存区合并到测试区。 |

### 维护评价

**维护评价：**
- **创建时间**：2018年，已有约7年历史。
- **近期更新频率**：最近更新发生在2026年（根据提供信息），但之前更新间隔较长（如2021年至2023年）。更新内容主要是构建系统、平台支持（LinuxArm64）和链接协议等维护性工作，而非功能增强。
- **活跃程度**：该插件代码库极其稳定且轻量（仅2个文件），功能单一明确。更新主要跟随引擎整体构建和平台支持的变更，属于被动维护状态。
- **已知限制**：仅支持 Windows、Linux、LinuxArm64 和 Mac 平台。
- **推荐使用**：**仅当你的项目通过 Epic Games 启动器发行时，此插件才相关且必要**。它是该发行渠道基础设施的一部分，通常由引擎或启动器自动管理，无需开发者直接干预。对于独立发行或其他平台的游戏，此插件不会被激活。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller)