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
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller) | |

## 用途

此插件为 Epic Games Launcher 的**分块下载系统**提供引擎端实现。当游戏通过 Epic Games Launcher 发布并使用分块（Chunk）机制进行按需下载时，该插件负责告诉引擎每个游戏分块（Chunk）的实际存储位置——是已经在本地磁盘上，还是需要从 Launcher 的服务端下载。

核心类 `FLauncherChunkInstaller` 继承自 `FGenericPlatformChunkInstall`，重写了 `GetChunkLocation` 方法，将分块位置查询桥接到 Launcher 的安装系统。这是 UE5 内容分块（Chunk-based packaging）工作流中 Launcher 端的关键对接层。

仅支持桌面平台（Win64、Linux、LinuxArm64、Mac），因为 Epic Games Launcher 仅覆盖这些平台。

## 使用场景

- 你通过 Epic Games Launcher 分发游戏，并启用了 **Chunk 安装**（分包）功能 → 此插件自动生效
- 你的游戏体积很大，需要让玩家按章节/内容分块下载 → Launcher 的分块系统配合此插件实现按需加载
- 你使用 **Project Launcher** 或 **UnrealAutomationTool** 进行分块打包发布 → 底层依赖此插件查询分块位置

> **注意**：普通开发者通常不需要直接调用此插件的 API。它在引擎启动时通过模块系统自动注册，由引擎的 ChunkInstall 子系统在后台使用。

## 蓝图用法

此插件不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。所有功能均在 C++ 层面通过引擎内部的 ChunkInstall 子系统调用。

## C++ 用法

### 头文件引入

```cpp
#include "LauncherChunkInstaller.h"
```

### 基本用法

此插件的实现非常精简，核心是一个单文件的 Runtime 模块。以下是其主要实现：

**Source/LauncherChunkInstaller/Public/LauncherChunkInstaller.h**

```cpp
// 继承平台通用分块安装器接口，将分块位置查询委托给 Launcher
class FLauncherChunkInstaller : public FGenericPlatformChunkInstall
{
public:
    // 重写：根据 ChunkID 返回该分块当前的存储位置
    // 返回值 EChunkLocation::Type 包括：OnDisk（已安装）、Downloading（下载中）等
    UE_API virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override;
};
```

### 进阶用法

此插件作为引擎 ChunkInstall 子系统的平台后端，通常由引擎内部自动使用：

```cpp
// 引擎启动时会自动选择对应的 ChunkInstall 实现
// 当检测到运行在 Epic Games Launcher 环境下时，会使用 FLauncherChunkInstaller
// 开发者通过标准的 FChunkInstallInterface 查询分块状态：

IPlatformChunkInstall* ChunkInstaller = FPlatformMisc::GetPlatformChunkInstall();
if (ChunkInstaller)
{
    EChunkLocation::Type Location = ChunkInstaller->GetChunkLocation(MyChunkID);
    switch (Location)
    {
    case EChunkLocation::OnDisk:
        // 分块已安装，可以直接加载
        break;
    case EChunkLocation::NotAvailable:
        // 分块未安装，需要请求下载
        break;
    }
}
```

## Demo 示例

此插件不提供可供直接使用的示例——它是一个引擎内部的桥接模块。以下是最小的模块结构展示：

```cpp
// LauncherChunkInstaller.Build.cs（参考结构）
using UnrealBuildTool;

public class LauncherChunkInstaller : ModuleRules
{
    public LauncherChunkInstaller(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { });
        PrivateDependencyModuleNames.AddRange(new string[] { });
    }
}
```

```cpp
// LauncherChunkInstaller.h - 完整的公共头文件（仅约 10 行代码）
#pragma once

#include "GenericPlatformChunkInstall.h"

class FLauncherChunkInstaller : public FGenericPlatformChunkInstall
{
public:
    UE_API virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override;
};

#undef UE_API
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等基础模块）。

该插件通过 `FGenericPlatformChunkInstall` 基类间接依赖引擎的平台抽象层，但这些均属于引擎标准模块，使用者无需额外配置依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `29f9ae30` | Enable LinuxArm64 MergeModules server builds. | 为 LinuxArm64 启用服务器构建的模块合并支持 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 批量添加 DLL 导出标记（API 宏），适配模块化构建 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件目录级别的批量改动 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的第三方链接为 HTTPS 协议 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 版本分支合并 |

### 维护评价

- **活跃程度**：**不活跃**。自 2023 年以来无实质性功能更新，最近两次提交均为全局性构建基础设施改动（添加 DLL 导出标记、启用新平台构建），而非针对此插件本身的功能修复
- **稳定性**：该插件功能极简（仅一个类、一个虚函数重写），结构自 2018 年创建以来基本未变，说明其实现已非常成熟稳定
- **风险评估**：低风险。代码量极少，逻辑清晰，不太可能出现 bug；但需注意此插件仅服务于 Epic Games Launcher 生态，如果你使用 Steam 或其他分发平台，此插件不会生效
- **推荐程度**：**不需要特别关注**。除非你在排查 Launcher 环境下的分块加载问题，否则此插件会静默运行，无需任何手动配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller)
- 官方文档：无（此为 Epic Games Launcher 内部组件，无公开文档）