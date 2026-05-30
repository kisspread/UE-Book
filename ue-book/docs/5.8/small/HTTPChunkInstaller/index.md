# HTTP Chunk Installer

> Implements a streaming install client

| 属性 | 值 |
|---|---|
| 中文名 | HTTP分块安装器 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HTTPChunkInstaller` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-14 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HTTPChunkInstaller) | |

## 用途

HTTPChunkInstaller 是一个为大型游戏设计的流式内容分发系统。它解决了游戏初始下载包体积过大的问题，允许玩家先下载一个较小的启动包，然后根据游戏进程，动态地从远程服务器（如CDN）下载并安装游戏所需的资源包（Chunk）。

该插件的核心是实现了一个客户端，能够：
1.  **查询和读取远程清单**：从云端获取可用的资源包列表及其元数据。
2.  **分块下载与安装**：根据优先级和游戏需求，按需下载资源包（`.pak`文件）和清单文件（`.manifest`）。
3.  **管理本地安装状态**：维护已安装、待安装和可更新的资源包状态，处理文件缓存、移动和挂载。
4.  **集成构建补丁服务**：深度集成UE的BuildPatchServices (BPS) 模块来处理资源的差异更新和安装验证。

它本质上是一个**运行时分块下载器和安装管理器**，而不是一个简单的文件下载器。

## 使用场景

-   **制作大型开放世界或3A级游戏**：玩家无需等待数十GB的完整下载，即可开始体验游戏的前期内容。
-   **实现“边玩边下”功能**：根据玩家所处的游戏区域或接下来的剧情，提前下载后续场景的资源。
-   **管理DLC或季节性内容**：作为动态内容更新的分发客户端。
-   **优化移动游戏或云游戏的首次加载时间**：减少玩家等待时间，提升体验。

## 蓝图用法

该插件主要提供底层的C++运行时控制，未发现直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 节点。其控制和状态查询通常通过C++代码访问 `FHTTPChunkInstall` 单例或相关子系统来完成。

## C++ 用法

### 头文件引入

```cpp
#include "HTTPChunkInstaller.h"
```

### 基本用法

该插件作为平台分块安装系统的一个实现。通常，你不需要直接实例化 `FHTTPChunkInstall`，而是通过平台子系统接口访问。核心交互是控制安装行为和查询状态。

**源码来源**: `Source/Public/HTTPChunkInstaller.h`

```cpp
// 获取HTTP分块安装器的实例（通常通过平台子系统）
// 假设已通过正确方式获取到 FHTTPChunkInstall* HTTPChunkInstaller
FHTTPChunkInstall* HTTPChunkInstaller = ...;

// 1. 设置安装速度（例如，在主菜单降低下载速度，游戏中提高速度）
HTTPChunkInstaller->SetInstallSpeed(EChunkInstallSpeed::Fast);

// 2. 查询特定资源块的下载进度
float Progress = HTTPChunkInstaller->GetChunkProgress(MyChunkID, EChunkProgressReportingType::PercentageComplete);
UE_LOG(LogHTTPChunkInstaller, Log, TEXT("Chunk %u 下载进度: %.2f%%"), MyChunkID, Progress * 100.0f);

// 3. 为即将进入的游戏场景提升某个资源块的优先级
bool bPrioritized = HTTPChunkInstaller->PrioritizeChunk(MySceneChunkID, EChunkPriority::High);
if (bPrioritized)
{
    UE_LOG(LogHTTPChunkInstaller, Log, TEXT("已为资源块 %u 设置高优先级"), MySceneChunkID);
}
```

### 进阶用法

了解其内部状态机和关键任务可以帮助你进行更深入的集成或调试。

**源码来源**: `Source/Public/HTTPChunkInstaller.h`, `Source/Public/ChunkSetup.h`, `Source/Public/ChunkInstall.h`

```cpp
// 内部状态机 (`ChunkInstallState`) 反映了安装流程的各个阶段
// Setup -> QueryRemoteManifests -> MoveInstalledChunks -> SearchTitleFiles -> ReadTitleFiles -> Idle/Installing

// 关键任务类理解：
// FChunkSetupTask: 在后台线程扫描本地安装目录、内容目录和暂存目录，整理已安装和待处理的资源块清单。
// FChunkMountTask: 在后台线程挂载已下载的.pak文件，并注册安装。
// FChunkInstallTask: 处理单个资源块的复制、清单保存和.pak文件挂载。
// FHTTPChunkInstall::Tick(): 驱动整个安装状态机的核心函数，每帧更新状态。
```

## Demo 示例

以下是一个集成和查询HTTPChunkInstaller的最小C++示例。

### ChunkDownloaderSubsystem.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "HTTPChunkInstaller.h" // 包含插件头文件
#include "ChunkDownloaderSubsystem.generated.h"

UCLASS()
class UChunkDownloaderSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 查询特定资源块的下载状态 */
    UFUNCTION(BlueprintCallable, Category = "Chunk Downloader")
    float GetChunkDownloadProgress(uint32 ChunkID) const;

    /** 请求优先下载指定的资源块 */
    UFUNCTION(BlueprintCallable, Category = "Chunk Downloader")
    bool RequestPrioritizeChunk(uint32 ChunkID);

private:
    /** 指向插件提供的安装器实例的弱指针 */
    TWeakPtr<FHTTPChunkInstall> ChunkInstallerPtr;
};
```

### ChunkDownloaderSubsystem.cpp
```cpp
#include "ChunkDownloaderSubsystem.h"
#include "HTTPChunkInstaller.h"
#include "HAL/IConsoleManager.h"

void UChunkDownloaderSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    // 通常，HTTPChunkInstall 实例由平台子系统管理。
    // 这里演示一种可能的获取方式（实际路径取决于项目配置和平台）。
    // 一个常见的模式是监听平台子系统的初始化。
    // 为简化，我们假设已经通过某种机制（如模块加载后）获得了实例。
    // 在实际项目中，你可能需要通过 FModuleManager 或平台接口获取。
    
    // 示例：尝试查找模块中可能存在的全局或静态实例（仅为演示）
    // 注意：这不是标准用法，实际项目应参考平台集成文档。
    // ChunkInstallerPtr = ...;
    
    UE_LOG(LogTemp, Log, TEXT("ChunkDownloaderSubsystem 初始化完成。"));
}

void UChunkDownloaderSubsystem::Deinitialize()
{
    ChunkInstallerPtr.Reset();
    Super::Deinitialize();
}

float UChunkDownloaderSubsystem::GetChunkDownloadProgress(uint32 ChunkID) const
{
    if (ChunkInstallerPtr.IsValid())
    {
        return ChunkInstallerPtr.Pin()->GetChunkProgress(ChunkID, EChunkProgressReportingType::PercentageComplete);
    }
    return -1.0f; // 表示无效
}

bool UChunkDownloaderSubsystem::RequestPrioritizeChunk(uint32 ChunkID)
{
    if (ChunkInstallerPtr.IsValid())
    {
        return ChunkInstallerPtr.Pin()->PrioritizeChunk(ChunkID, EChunkPriority::High);
    }
    return false;
}
```

## 模块依赖

从插件源码和其用途可知，它深度依赖于构建和补丁服务。

| 模块 | 用途 |
|---|---|
| `BuildPatchServices` | 核心依赖。用于加载和保存清单（.manifest）、验证安装、管理应用安装注册。 |
| `Json` | 可能用于解析云服务返回的配置或清单信息。 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复日志格式说明符在32位/64位参数下的匹配问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的`UE_LOG`宏迁移至新的`UE_LOGF`宏。 |
| 2025-06-11 | `664cf2cd` | Replace some usages of FORCEINLINE with inline in Foundation modules. | 在基础模块中将部分`FORCEINLINE`替换为`inline`。 |
| 2023-10-12 | `ffb133e7` | Update more code using FJsonObject to use TCHAR strings instead of ANSI strings. Removes unnecessary | 更新代码，使`FJsonObject`更多地使用TCHAR字符串而非ANSI字符串。 |
| 2023-08-03 | `02c422c5` | Add http request progress delegate 64 bit support. | 为HTTP请求进度委托添加64位支持。 |

### 维护评价

该插件**创建时间较早（2017年）**，是一个相对成熟但专业的组件。**最近一次包含功能性改进的提交是2023年10月和8月**（关于字符串类型和进度委托），此后近3年的更新均为**编译兼容性维护和代码风格迁移**。

综合来看：
- **年龄**：约9年历史，属于“老古董”范畴。
- **活跃度**：**维护不活跃**。近2-3年没有新的功能开发，仅有基础的代码维护和编译修复。
- **稳定性**：由于长时间无功能性变更，其核心逻辑可能已经稳定，但也意味着不会获得新特性或针对新平台特性的优化。
- **推荐使用**：**有条件推荐**。如果你的项目确实需要一个官方的、基于BPS的HTTP流式安装方案，且能接受其当前状态，可以使用。但应注意，它默认禁用，可能需要较多的平台集成和配置工作。对于新项目，也值得评估是否有更新的或更适合项目需求的社区/官方方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HTTPChunkInstaller)
- 官方文档：未提供