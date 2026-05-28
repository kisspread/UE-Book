# AndroidFileServer

> Adds support for remote file management to Android projects.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓文件服务器 |
| 分类 | Android |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidFileServer` (Runtime), `AndroidFileServerEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-02-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidFileServer) | |

## 用途

此插件在 Android 设备上运行一个轻量级的文件服务器。它为开发者提供了一种便捷的方式，能够通过网络或 USB 连接远程管理（查看、推送、拉取）项目在 Android 设备上的文件，而无需依赖 ADB 命令或复杂的文件传输流程。主要服务于开发调试和数据交换场景。

## 使用场景

-   **开发调试**：在开发 Android 项目时，频繁需要将编辑器中修改的资产（如 `PAK` 文件、配置文件、Lua 脚本）推送到设备进行测试，使用此插件可以一键完成，无需手动查找设备路径。
-   **自动化测试**：编写自动化测试脚本，通过插件提供的 API 自动将测试资源推送到设备并运行测试。
-   **热更新与资源预览**：在已打包的 Android 应用中启用文件服务器，可以实现无需重新打包即可更新部分游戏资源或配置。
-   **日志与数据回传**：轻松地从设备拉取崩溃日志、玩家存档或运行时数据到 PC 进行分析。

## 蓝图用法

插件通过 `UAndroidFileServerBPLibrary` 提供蓝图接口，用于在运行时控制设备上的文件服务器状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start File Server` | 请求在 Android 设备上启动文件服务器。可分别启用 USB 和网络连接模式，并设置网络端口。 | `UAndroidFileServerBPLibrary` |
| `Stop File Server` | 请求停止在 Android 设备上运行的文件服务器。 | `UAndroidFileServerBPLibrary` |
| `Is File Server Running` | 查询当前文件服务器的运行状态（未运行、仅USB、仅网络、USB与网络混合）。 | `UAndroidFileServerBPLibrary` |

### 使用示例（蓝图描述）

一个典型的调试启动流程可以这样构建蓝图逻辑：
1.  在游戏开始时，调用 `Start File Server` 节点，参数设置为 `USB = true`, `Network = false`，以仅通过 USB 连接启动服务器，这样安全性更高。
2.  在游戏退出或某个调试界面关闭时，调用 `Stop File Server` 节点以关闭服务。
3.  在调试菜单中，可以调用 `Is File Server Running` 节点来显示当前服务状态，供开发者确认。

## C++ 用法

除了蓝图接口，插件也提供了 C++ 模块接口。核心的蓝图函数库 `UAndroidFileServerBPLibrary` 是静态的，因此可以在 C++ 中直接调用。

### 头文件引入

```cpp
#include "AndroidFileServerBPLibrary.h"
```

### 基本用法

从提供的头文件中，我们可以看到核心的控制函数。

```cpp
// 启动文件服务器（仅USB模式，端口默认57099）
bool bStarted = UAndroidFileServerBPLibrary::StartFileServer(true, false, 57099);
if (bStarted)
{
    UE_LOG(LogTemp, Log, TEXT("Android File Server started via USB."));
}

// 查询文件服务器状态
EAFSActiveType::Type ServerStatus = UAndroidFileServerBPLibrary::IsFileServerRunning();
if (ServerStatus == EAFSActiveType::USBOnly)
{
    UE_LOG(LogTemp, Log, TEXT("File server is running on USB."));
}

// 停止文件服务器
UAndroidFileServerBPLibrary::StopFileServer(true, true); // 停止 USB 和网络服务
```

### 进阶用法

结合 `IAndroidRuntimeSettingsModule` 等其他 Android 模块，可以在项目启动时根据构建配置自动管理文件服务器。例如，只在开发包 (`UE_BUILD_DEVELOPMENT`) 中启用它。

## Demo 示例

一个简单的单例类，用于管理应用生命周期中的文件服务器。

### MyFileServerManager.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyFileServerManager
{
public:
    static FMyFileServerManager& Get();
    
    void Startup();
    void Shutdown();

private:
    FMyFileServerManager() = default;
    ~FMyFileServerManager() = default;
    FMyFileServerManager(const FMyFileServerManager&) = delete;
    FMyFileServerManager& operator=(const FMyFileServerManager&) = delete;
};
```

### MyFileServerManager.cpp

```cpp
#include "MyFileServerManager.h"
#include "AndroidFileServerBPLibrary.h"

FMyFileServerManager& FMyFileServerManager::Get()
{
    static FMyFileServerManager Instance;
    return Instance;
}

void FMyFileServerManager::Startup()
{
#if PLATFORM_ANDROID && UE_BUILD_DEVELOPMENT
    // 仅在 Android 开发包中，通过 USB 启动文件服务器
    if (GIsEditor == false) // 确保不是在编辑器中运行
    {
        UAndroidFileServerBPLibrary::StartFileServer(true, false, 57099);
    }
#endif
}

void FMyFileServerManager::Shutdown()
{
#if PLATFORM_ANDROID && UE_BUILD_DEVELOPMENT
    UAndroidFileServerBPLibrary::StopFileServer();
#endif
}
```

## 模块依赖

插件自身的 `Build.cs` 文件未在此提供。根据其功能（运行时控制 Android 文件服务）和编辑器功能（可能包含部署工具），使用者通常需要依赖以下模块（具体以实际 `Build.cs` 为准）：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该插件主要为 Android 平台提供服务，其依赖项可能已包含在引擎基础 Android 支持中。若在自定义模块中使用，通常只需依赖 `Engine` 即可访问其蓝图库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `409776cd` | Fix an issue with compressed file writes to AFS with uncompressable blocks | 修复了向 AFS 写入包含无法压缩块的压缩文件时出现的问题 |
| 2026-05-26 | `2585a962` | [Android] AFS shipping build fix | 修复了 Android 发布构建中 AFS 的问题 |
| 2026-05-25 | `09e10f3d` | [Android] AFS build fix | 修复了 Android 平台下 AFS 的编译问题 |
| 2026-05-23 | `6d9338cd` | Fix unacceptable words in RemoteFileManager.java | 修复了 Java 源文件中不合适的用词 |
| 2026-05-22 | `a35e5b4a` | New version of UnrealAndroidFileTool with better error handling, faster data transfer and new GUI mo | 更新了 UnrealAndroidFileTool，提升了错误处理和传输速度，并改进了 GUI |

### 维护评价

-   **活跃维护**：最近一次提交在 2026 年 5 月，并且近期提交密集，集中在修复构建问题和优化数据传输功能上。
-   **内容健康**：更新内容多为 bug 修复和功能优化，没有出现废弃标记。
-   **推荐使用**：作为 Epic Games 官方维护的 Android 平台核心调试工具之一，其稳定性和集成度很高。对于任何涉及 Android 部署和调试的 UE5 项目，都推荐启用此插件以提升工作效率。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidFileServer)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidFileServer/Tests)