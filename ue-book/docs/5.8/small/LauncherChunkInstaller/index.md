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

本插件为 Epic Games Launcher 的**分块下载系统（Chunk Download System）**提供平台层实现。

Unreal Engine 支持按"块（Chunk）"分块下载游戏内容，玩家无需等待完整下载即可开始游戏——优先下载核心内容，其余内容按需后台下载。本插件中的 `FLauncherChunkInstaller` 继承自 `FGenericPlatformChunkInstall`，重写了 `GetChunkLocation` 方法，用于在运行时判断指定 ChunkID 对应的数据存储位置，从而让引擎的分块下载系统能正确地从 Epic Games Launcher 定位和管理内容块。

简而言之：这是一个纯粹的**基础设施插件**，普通开发者几乎不会直接调用它的 API，它在引擎启动时由平台抽象层自动选择和加载。

## 使用场景

- 你的游戏通过 **Epic Games Launcher** 发布和分发 → 本插件自动生效，管理内容块的存储位置
- 你需要实现**按需下载（Download-on-Demand）**功能，让玩家边玩边下 → 依赖本插件提供的 chunk 定位机制
- 你使用自定义的下载/分发平台 → 本插件不适用，你需要自行实现 `FGenericPlatformChunkInstall` 的子类

**平台限制**：仅支持 Win64、Linux、LinuxArm64、Mac。不支持主机和移动端平台。

## 蓝图用法

本插件**没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。`GetChunkLocation` 是引擎内部调用的虚函数，不面向蓝图用户。

## C++ 用法

本插件的核心功能是引擎内部自动调用的，开发者无需手动使用。以下信息仅用于理解其工作原理。

### 头文件引入

```cpp
#include "LauncherChunkInstaller.h"
```

### 核心接口

插件仅包含一个类，重写了引擎平台抽象层的一个虚函数：

```cpp
// 来源: Engine/Plugins/Portal/LauncherChunkInstaller/Source/LauncherChunkInstaller/Public/LauncherChunkInstaller.h
class FLauncherChunkInstaller : public FGenericPlatformChunkInstall
{
public:
    // 根据 ChunkID 返回该内容块的存储位置
    UE_API virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override;
};
```

`EChunkLocation::Type` 枚举通常包含：
- `EChunkLocation::Invalid` — 无效/未知位置
- `EChunkLocation::OnDisk` — 已在磁盘上
- `EChunkLocation::NotAvailable` — 不可用/未下载

引擎在加载 Chunk 时会调用此方法判断该 Chunk 是否已安装，若未安装则触发 Launcher 的下载流程。

### 工作原理

```
游戏请求加载 Chunk 15
        ↓
引擎 Chunk Install 子系统
        ↓
FLauncherChunkInstaller::GetChunkLocation(15)
        ↓
返回 OnDisk / NotAvailable
        ↓
OnDisk → 直接加载    NotAvailable → 通知 Launcher 开始下载
```

## Demo 示例

本插件不提供面向开发者的公共 API。以下是展示其在引擎中如何被自动注册的最小说明：

```cpp
// LauncherChunkInstaller.cpp（插件内部实现）
#include "LauncherChunkInstaller.h"

// 引擎启动时通过平台抽象层自动注册此实现
// 开发者无需手动实例化 FLauncherChunkInstaller

// 如果你需要自定义 chunk 安装逻辑（不依赖 Epic Launcher），
// 可参考本插件的模式，继承 FGenericPlatformChunkInstall：
class FMyCustomChunkInstaller : public FGenericPlatformChunkInstall
{
public:
    virtual EChunkLocation::Type GetChunkLocation(uint32 ChunkID) override
    {
        // 你的自定义逻辑：查询本地存储、CDN、或数据库
        if (IsChunkLocallyAvailable(ChunkID))
        {
            return EChunkLocation::OnDisk;
        }
        return EChunkLocation::NotAvailable;
    }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等基础模块）。`FGenericPlatformChunkInstall` 定义在 Core 模块中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `29f9ae30` | Enable LinuxArm64 MergeModules server builds. | 为 LinuxArm64 服务器构建启用模块合并 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 将导出符号标记迁移到 UE_API 宏风格 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件通用更新（批量改动） |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的厂商链接更新为 HTTPS 协议 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 从引擎 Staging 分支合并到 Test 分支 |

### 维护评价

- **年龄**：约 8 年，创建于 UE 4.20 时期
- **活跃度**：**极低**。近 5 年内没有任何功能性更新，所有 commit 均为构建系统维护（符号导出迁移、平台支持扩展、协议更新等）
- **代码规模**：仅 1 个头文件 + 1 个实现文件，总计约 400 行，极其精简
- **稳定性**：作为底层基础设施插件，功能成熟且稳定，长期无改动属于正常现象
- **风险**：无已知问题。但注意它仅限桌面平台，主机/移动端需要其他实现

**结论**：这是一个稳定的小型基础设施插件，长期处于维护状态（不活跃但未废弃）。如果你的游戏仅通过 Epic Games Launcher 分发到桌面平台，它会自动工作，无需额外关注。**推荐保持默认启用状态，不要手动修改。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Portal/LauncherChunkInstaller)
- [官方文档]() — 无（.uplugin 中 DocsURL 为空）