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

这是一个平台特定的、用于与 Epic Games Launcher 集成的分块安装器实现。它本身并非一个通用的分块管理器，而是一个**驱动**或**后端实现**。其核心作用是通过重写 `GetChunkLocation` 方法，为引擎提供一个与 Epic Games 启动器交互的通道，告诉引擎每个游戏内容分块（Chunk）的具体存储位置（可能是本地磁盘、云端或其他位置），从而实现更智能的分块加载、下载和安装流程。它的存在是为了让引擎能够利用启动器提供的特定功能来优化游戏内容的交付和安装体验。

## 使用场景

- 你的游戏通过 **Epic Games Store** 进行发布和分发。
- 你需要实现游戏的 **分块安装** 或 **按需下载**，即玩家可以先下载游戏的核心部分开始玩，其余内容在后台或按需下载。
- 你希望游戏的安装和更新过程能与 Epic Games Launcher 的下载管理器深度集成，实现更高效的内容管理。

## 蓝图用法

该插件主要通过虚函数重写来扩展引擎底层功能，没有提供公开的蓝图接口或节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 插件未暴露任何蓝图可调用函数。 | - |

## C++ 用法

### 头文件引入

```cpp
#include "LauncherChunkInstaller.h"
```

### 基本用法

该插件的核心是重写引擎的分块安装接口。通常，你不会直接调用此插件的 API，而是由引擎内部自动使用。作为开发者，你主要需要理解其工作原理。

从 `LauncherChunkInstaller.h` 提取的类定义展示了其核心职责：

```cpp
// 文件路径: Engine/Plugins/Portal/LauncherChunkInstaller/Source/LauncherChunkInstaller/Public/LauncherChunkInstaller.h

class FLauncherChunkInstaller : public FGenericPlatformChunkInstall
{
public:
	// 核心函数：重写此函数以决定给定 ChunkID 的存储位置。
	// 返回值可能指示该分块在本地可用，或需要从云端下载等。
	UE_API virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override;
};
```

### 进阶用法

要使此插件生效，通常需要通过引擎的模块化系统（Module Manager）将其加载并设置为活动的 `IPlatformChunkInstall` 实现。这一般在引擎初始化或平台抽象层配置阶段完成。对于大多数游戏开发者，这个过程是透明的，由引擎和启动器自动处理。

## Demo 示例

下面的示例展示了一个简化的自定义分块安装器的实现模式，它与 `LauncherChunkInstaller` 的设计思路类似。

**MyGameChunkInstaller.h**
```cpp
#pragma once

#include "GenericPlatform/GenericPlatformChunkInstall.h"

// 自定义的分块安装器，可用于非启动器场景或测试
class FMyGameChunkInstaller : public FGenericPlatformChunkInstall
{
public:
	virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override;

	// 可以添加额外的自定义逻辑，例如检查本地缓存
	bool IsChunkCached(uint32 ChunkID) const;
};
```

**MyGameChunkInstaller.cpp**
```cpp
#include "MyGameChunkInstaller.h"

EChunkLocation::Type FMyGameChunkInstaller::GetChunkLocation(uint32 ChunkID)
{
	// 示例逻辑：
	// 1. 首先检查此分块是否已在本地缓存
	if (IsChunkCached(ChunkID))
	{
		return EChunkLocation::Type::Local;
	}
	// 2. 对于核心分块(ChunkID < 10)，总是要求从本地加载（假设已预装）
	else if (ChunkID < 10)
	{
		return EChunkLocation::Type::Local;
	}
	// 3. 其他分块位于云端，需要下载
	else
	{
		return EChunkLocation::Type::Cloud;
	}
}

bool FMyGameChunkInstaller::IsChunkCached(uint32 ChunkID) const
{
	// 实现具体的缓存检查逻辑，例如查询本地文件系统或缓存数据库
	// 此处为占位实现
	return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 插件继承自引擎的 `GenericPlatformChunkInstall`，相关依赖已由引擎公共模块提供。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `29f9ae30` | Enable LinuxArm64 MergeModules server builds. | 为 LinuxArm64 平台的合并模块服务器构建提供支持。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i... | 使用 UnrealGame 构建目标，并转换文件以使用 DLL 存储属性。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件目录的通用维护性提交。 |

### 维护评价

- **创建时间**：2018年，历史较长。
- **更新频率**：更新不频繁，但持续有维护性提交，以确保其在新平台（如 LinuxArm64）上的编译兼容性。
- **活跃度**：**维护中**。作为引擎基础设施的一部分，它保持与最新引擎版本和构建系统的兼容性。最近的提交主要是构建和平台支持相关的，表明它仍在被维护以保障基础功能的运行，但未见有重大功能变更。
- **限制**：该插件紧密依赖于 **Epic Games Launcher** 的运行时环境。脱离该环境（例如在 Steam 或纯离线环境中）将无法发挥其作用。
- **推荐**：如果你的项目**仅通过 Epic Games Store 分发**，此插件是默认且必要的。对于其他分发渠道，此插件将不起作用，你的游戏将回退到引擎默认的分块安装逻辑。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller)