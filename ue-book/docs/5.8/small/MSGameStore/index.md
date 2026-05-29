# Microsoft GDK Store Plug-in for Unreal Engine

> Allows packaging Windows games for submission to the Xbox PC App

| 属性 | 值 |
|---|---|
| 中文名 | 微软 GDK 商店插件 |
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MSGameStore` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGameStore) | |

## 用途
此插件提供了将 Unreal Engine 构建的游戏打包并提交到 Microsoft GDK Store (Xbox PC App) 所需的运行时支持。它封装了与 Microsoft Game Development Kit (GDK) 相关的检测和分块安装功能，简化了游戏发布到 Microsoft 游戏平台的流程。

## 使用场景
- 你正在使用 Unreal Engine 开发一款希望发布到 Xbox PC App 的 Windows 游戏。
- 你的游戏需要利用 Microsoft GDK 的分块安装（Chunk Install）功能来支持可下载内容（DLC）或按需下载大型游戏包。
- 你需要检测游戏是否以应用包（Packaged）的形式在 Microsoft Store 中运行。

## 蓝图用法
该插件主要提供 C++ 模块接口，未在提供的头文件中暴露直接的蓝图可调用函数或属性。其核心功能（如获取分块安装器）主要供 C++ 代码在打包和分发逻辑中使用。

## C++ 用法
### 头文件引入
```cpp
#include "MSGameStoreModule.h"
```
### 基本用法
通过单例模式访问模块，并查询打包状态。
```cpp
// 获取模块实例
IMSGameStoreModule& GameStoreModule = IMSGameStoreModule::Get();

// 检查当前应用是否为打包版本（例如从 Microsoft Store 安装）
bool bIsStorePackage = GameStoreModule.IsPackaged();
if (bIsStorePackage)
{
    // 执行仅在打包环境下运行的逻辑
}
```

### 进阶用法
获取并使用 GDK 分块安装器来管理可下载内容。
```cpp
#include "MSGameStoreModule.h"
#include "Platform/IPlatformChunkInstall.h"

void ManageDLCContent()
{
    IMSGameStoreModule& GameStoreModule = IMSGameStoreModule::Get();
    
    // 获取 GDK 分块安装器接口
    IPlatformChunkInstall* ChunkInstaller = GameStoreModule.GetChunkInstaller();
    
    if (ChunkInstaller)
    {
        // 使用 ChunkInstaller 接口进行分块安装管理
        // 例如查询已安装分块、开始下载特定分块等。
        // 具体 API 取决于 IPlatformChunkInstall 的定义和 GDK 版本。
        UE_LOG(LogTemp, Log, TEXT("GDK Chunk Installer is available."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("GDK Chunk Installer is not available (non-store build)."));
    }
}
```
*(注：`IPlatformChunkInstall` 的具体方法未在提供的源码中定义，实际使用请参考 Microsoft GDK 及 Unreal Engine 的相关文档。)*

## Demo 示例
以下示例展示如何在一个游戏模块中集成 MSGameStore 插件功能。
```cpp
// MyGameModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void CheckGameStoreEnvironment();
};

// MyGameModule.cpp
#include "MyGameModule.h"
#include "MSGameStoreModule.h"

void FMyGameModule::StartupModule()
{
    // 模块启动时检查商店环境
    CheckGameStoreEnvironment();
}

void FMyGameModule::ShutdownModule()
{
}

void FMyGameModule::CheckGameStoreEnvironment()
{
    // 尝试加载 MSGameStore 模块
    FModuleManager::Get().LoadModule(TEXT("MSGameStore"));
    
    if (IMSGameStoreModule::IsAvailable())
    {
        const IMSGameStoreModule& StoreModule = IMSGameStoreModule::Get();
        
        if (StoreModule.IsPackaged())
        {
            UE_LOG(LogTemp, Log, TEXT("Game is running as a packaged Microsoft Store application."));
            
            // 可以在此处初始化依赖分块安装器的系统
            IPlatformChunkInstall* Installer = StoreModule.GetChunkInstaller();
            if (Installer)
            {
                // 初始化 DLC 管理系统...
            }
        }
        else
        {
            UE_LOG(LogTemp, Log, TEXT("Game is running in a development/editor environment."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MSGameStore module is not available or enabled."));
    }
}

IMPLEMENT_PRIMARY_GAME_MODULE(FMyGameModule, MyGame, "MyGame");
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `MSGamingSupport` | 提供基础的 Microsoft 游戏支持功能。 |

## 维护状态
### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 移植函数类型转换警告，确保跨编译器兼容。 |
| 2026-04-24 | `101f2bf3` | Enable GDK ARM64 support in plugins (requires April 2026 GDK & modern folder layout) | 启用 GDK ARM64 支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-09 | `5eb8fada` | [Backout] - CL51493025 | 回退了之前的一次更改（CL51493025）。 |
| 2026-03-06 | `21bccda6` | Enable arm64 support in plugins | 在插件中启用 ARM64 支持（首次尝试）。 |

### 维护评价
该插件创建于 2026 年初，非常年轻。最近半年内有多次活跃更新，主要集中在**平台支持扩展**（ARM64）、**代码健壮性提升**（警告修复）和**构建系统迁移**（日志宏）上。作为标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false` 的实验性插件，它仍在积极开发和迭代中。目前没有发现已知的废弃迹象。**推荐**有 Microsoft Store 发行需求的开发者关注并尝试使用，但需注意其测试版本属性。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/MSGameStore)