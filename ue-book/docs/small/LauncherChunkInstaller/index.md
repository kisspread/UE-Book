# Launcher Chunk Installer

> Chunk installer module that hooks into launcher

| 属性 | 值 |
|---|---|
| 分类 | Portal |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | LauncherChunkInstaller (Runtime, LoadingPhase: PostConfigInit) |
| 平台 | Win64, Linux, Mac |
| 创建时间 | 2018-05-23 |
| 年龄标签 | 👴 老古董（~8年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Portal/LauncherChunkInstaller) | |

## 用途

LauncherChunkInstaller 是 Epic Games Launcher 的 **分块安装（Chunk Install）** 系统的桥接模块。它实现了 `IPlatformChunkInstallModule` 接口，将 UE5 的 Chunk 系统与 Epic Games Launcher 的 Pak 文件管理能力连接起来。

**核心逻辑非常简单**：当引擎需要查询某个 Chunk 当前在哪里时，这个模块会去问 `FPakPlatformFile`（Pak 文件系统层）："这个 Chunk 在哪个位置？" 然后把结果返回给引擎的 Chunk Install 框架。

这个 plugin 解决的问题是：Epic Games Launcher 支持按 Chunk 分批下载游戏内容（例如先下载第一关，后台下载后续关卡），而引擎需要一种方式来查询每个 Chunk 的安装状态。LauncherChunkInstaller 就是这个查询的桥梁。

### 为什么存在？

UE5 的 Chunk Install 系统是抽象的（`IPlatformChunkInstall` 接口），不同平台有不同的实现：
- **iOS** → `IOSChunkInstaller`（App Store 分块下载）
- **HTTP** → `HTTPChunkInstaller`（自定义 CDN 分块下载）
- **Epic Launcher** → **LauncherChunkInstaller**（本文档的 plugin）

当游戏通过 Epic Games Launcher 分发时，这个 plugin 负责让引擎知道哪些 Pak 文件已经下载完成、哪些还在等待。

## 使用场景

- 你的游戏通过 **Epic Games Launcher** 发布，且支持分块下载（先下载部分内容即可开始游戏）
- 你需要在运行时查询某个 Pak Chunk 是否已经就绪
- 你想控制分块下载的优先级（例如优先下载玩家即将进入的关卡）

**注意**：对于大多数游戏项目，你不需要直接与这个 plugin 交互。它的行为是自动的——只要 plugin 启用，引擎的 Chunk 系统就会自动使用它来查询 Pak 文件位置。

## 蓝图用法

此 plugin **不暴露任何蓝图接口**。没有 `BlueprintCallable` 或 `BlueprintReadWrite` 的函数。

Chunk Install 系统的查询通过引擎内部的 `IPlatformChunkInstall` 接口完成，该接口是纯 C++ 的。如果你需要在蓝图中查询 Chunk 状态，需要自行封装 C++ 函数。

## C++ 用法

### 理解架构

LauncherChunkInstaller 的核心是一个非常薄的桥接层：

```
IPlatformChunkInstall (引擎接口)
    └── FGenericPlatformChunkInstall (通用基类，提供默认实现)
            └── FLauncherChunkInstaller (本 plugin，仅覆盖 GetChunkLocation)
```

### 头文件引入

```cpp
#include "GenericPlatform/GenericPlatformChunkInstall.h"
```

### 查询 Chunk 位置

本 plugin 本身不提供额外的公共 API。它是通过引擎的模块系统自动加载的。要使用 Chunk Install 系统，通过引擎提供的全局接口：

```cpp
#include "GenericPlatform/GenericPlatformChunkInstall.h"

// 获取平台 Chunk Install 模块
IPlatformChunkInstallModule* ChunkInstallModule = 
    FModuleManager::Get().LoadModulePtr<IPlatformChunkInstallModule>("LauncherChunkInstaller");

if (ChunkInstallModule)
{
    IPlatformChunkInstall* ChunkInstaller = ChunkInstallModule->GetPlatformChunkInstall();
    
    // 查询某个 Pak Chunk 的位置
    EChunkLocation::Type Location = ChunkInstaller->GetPakchunkLocation(0);
    
    switch (Location)
    {
    case EChunkLocation::LocalFast:
        // Chunk 已在本地快速存储上（已下载完成）
        break;
    case EChunkLocation::NotAvailable:
        // Chunk 尚未下载
        break;
    case EChunkLocation::DoesNotExist:
        // 该 Chunk ID 不存在
        break;
    }
}
```

### 核心实现解读

`FLauncherChunkInstaller::GetChunkLocation()` 的完整逻辑（源码位于 `LauncherChunkInstaller.cpp`）：

```cpp
EChunkLocation::Type FLauncherChunkInstaller::GetChunkLocation(uint32 ChunkID)
{
    // 默认假设所有 Chunk 都在本地（快速存储）
    EChunkLocation::Type Result = EChunkLocation::LocalFast;

    // 获取 Pak 文件系统
    FPakPlatformFile* PakPlatformFile = (FPakPlatformFile*)(
        FPlatformFileManager::Get().FindPlatformFile(FPakPlatformFile::GetTypeName()));
    
    // 如果 Pak 文件系统支持 Chunk 查询，使用它来获取真实位置
    if (PakPlatformFile && PakPlatformFile->AnyChunksAvailable())
    {
        Result = PakPlatformFile->GetPakChunkLocation(ChunkID);
    }

    return Result;
}
```

**关键点**：
1. 默认返回 `LocalFast`——假设所有内容都已下载
2. 只有当 `FPakPlatformFile` 报告有 Chunk 可用时，才进行实际查询
3. 这意味着在编辑器开发环境下（没有 Launcher 分块下载），所有 Chunk 都被视为已就绪

### 注册委托监听 Chunk 安装事件

通过基类 `FGenericPlatformChunkInstall` 提供的接口，可以监听 Chunk 安装完成事件：

```cpp
IPlatformChunkInstall* ChunkInstaller = /* 获取实例 */;

// 监听 Chunk 安装完成事件
FDelegateHandle Handle = ChunkInstaller->AddChunkInstallDelegate(
    FPlatformChunkInstallDelegate::CreateLambda([](uint32 ChunkID, bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Chunk %u 安装完成"), ChunkID);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Chunk %u 安装失败"), ChunkID);
        }
    })
);

// 不再需要时移除委托
ChunkInstaller->RemoveChunkInstallDelegate(Handle);
```

## Demo 示例

### 最小使用示例

```cpp
// MyChunkCheck.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyChunkCheck.generated.h"

UCLASS()
class UMyChunkCheckSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    // 检查指定 Chunk 是否已就绪
    UFUNCTION(BlueprintCallable, Category = "Chunk Install")
    bool IsChunkReady(int32 PakChunkIndex) const;

private:
    TSharedPtr<IPlatformChunkInstall> ChunkInstaller;
};
```

```cpp
// MyChunkCheck.cpp
#include "MyChunkCheck.h"
#include "GenericPlatform/GenericPlatformChunkInstall.h"
#include "Modules/ModuleManager.h"

void UMyChunkCheckSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    IPlatformChunkInstallModule* ChunkInstallModule = 
        FModuleManager::Get().LoadModulePtr<IPlatformChunkInstallModule>("LauncherChunkInstaller");
    
    if (ChunkInstallModule)
    {
        ChunkInstaller = MakeShareable(
            ChunkInstallModule->GetPlatformChunkInstall(),
            [](IPlatformChunkInstall*) {}  // 不拥有所有权，不删除
        );
    }
}

bool UMyChunkCheckSubsystem::IsChunkReady(int32 PakChunkIndex) const
{
    if (!ChunkInstaller.IsValid())
    {
        return true;  // 没有 Chunk 系统时假设所有内容可用
    }

    EChunkLocation::Type Location = ChunkInstaller->GetPakchunkLocation(PakChunkIndex);
    return (Location == EChunkLocation::LocalFast || Location == EChunkLocation::LocalSlow);
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "LauncherChunkInstaller"  // 或者通过模块名动态加载
});
```

## 模块依赖

从 `LauncherChunkInstaller.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块，提供 `FGenericPlatformChunkInstall` 基类和文件系统接口 |
| `PakFile` | Pak 文件系统，提供 `FPakPlatformFile` 用于查询 Chunk 位置 |

**注意**：这些都是 `PrivateDependencyModuleNames`，即本 plugin 内部使用。使用本 plugin 的项目模块通常只需要依赖 `Core`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `89df8c17` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types. | 批量修改 DLL 导出宏风格，非功能性变更 |
| 2023-01-12 | `2f78497e` | Updated private files with IWYU for all plugins | 批量 IWYU 头文件清理，非功能性变更 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol | 更新 URL 为 HTTPS，非功能性变更 |

### 维护评价

- **创建时间**：2018年（UE 4.20 时期），已约 8 年历史
- **最近更新**：所有近期 commit 都是批量维护性修改（DLL 导出宏、IWYU、URL 更新），**没有功能性更新**
- **代码量**：极小，核心逻辑仅约 10 行
- **状态**：**稳定/低维护**——代码足够简单，不需要频繁更新
- **已知限制**：源码中有被注释掉的旧逻辑（`#if 0` 块），最初用于 Fortnite 加密 Chunk 支持，已移除
- **推荐**：如果你的游戏通过 Epic Games Launcher 发布，这个 plugin 默认启用且自动工作，无需额外配置。对于自定义分发渠道，考虑使用 `HTTPChunkInstaller`

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Portal/LauncherChunkInstaller)
- [GenericPlatformChunkInstall 接口定义](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Core/Public/GenericPlatform/GenericPlatformChunkInstall.h)
- [HTTPChunkInstaller（替代方案）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HTTPChunkInstaller)
- [DefaultInstallBundleManager（Chunk Install 的上层管理器）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DefaultInstallBundleManager)
