# AndroidFileServer

> Adds support for remote file management to Android projects.

| 属性 | 值 |
|---|---|
| 分类 | Android |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AndroidFileServer (Runtime), AndroidFileServerEditor (Editor) |
| 创建时间 | 2022-02-24 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidFileServer) | |

## 用途

AndroidFileServer 是一个**远程文件传输工具**，让你能从 PC 端直接读写 Android 设备上的游戏文件，无需 `adb push/pull`。

它解决的核心问题是：**在开发和测试阶段，你经常需要把大文件（如资源包、.obb）推送到设备上，或者从设备拉取日志、存档等文件**。传统的 `adb` 命令行操作繁琐且不支持压缩传输。AndroidFileServer 在设备端运行一个轻量级文件服务器，UE 编辑器通过 USB 或网络直接与之通信，支持目录浏览、文件读写、GZIP 压缩传输等操作。

底层实现是 Java 层的 `RemoteFileManager`（基于 socket 的二进制协议服务器），运行在 `RemoteFileManagerService`（Android Foreground Service）中。UE 编辑器侧的 UnrealAndroidFileTool 客户端负责连接和传输。

## 使用场景

- 你正在做 Android 游戏开发，需要频繁把 `.pak` / `.obb` 资源包推送到测试设备 → 启用 AndroidFileServer，编辑器自动通过它加速部署
- 你想从设备上拉取游戏日志、崩溃报告或存档文件进行调试 → 通过 AFS 直接浏览设备文件系统
- 你需要在 Shipping 包中保留远程文件访问能力（如 QA 测试） → 在设置中勾选 `IncludeInShipping`
- 你需要从外部（非 UE 编辑器）独立启动文件服务器 → 使用 `RemoteFileManagerActivity` 的 Intent 接口

## 设置项

通过 **Edit → Project Settings → Platforms → Android → File Server** 配置（由 `UAndroidFileServerRuntimeSettings` 提供）：

### Packaging 类

| 设置 | 说明 |
|---|---|
| **Use AndroidFileServer** | 是否在打包时嵌入 AFS（默认 true） |
| **Allow Network Connection** | 是否允许通过网络（WiFi）连接（默认仅 USB） |
| **Security Token** | 安全令牌，连接时需验证（留空则禁用验证） |
| **Include in Shipping** | 是否在 Shipping 构建中嵌入 AFS（默认 false） |
| **Allow External Start in Shipping** | 允许在 Shipping 构建中通过外部 Intent 启动 AFS |
| **Compile AFS Project** | 编译独立的 AFS APK（AFSStub 项目） |

### Deployment 类

| 设置 | 说明 |
|---|---|
| **Use Compression** | 传输时启用 GZIP 压缩 |
| **Log Files** | 记录传输的文件列表 |
| **Report Stats** | 报告传输速率统计 |

### Connection 类

| 设置 | 说明 |
|---|---|
| **Connection Type** | USB Only / Network Only / USB + Network Combined |
| **Use Manual IP Address** | 手动指定设备 IP（仅适用于单设备部署） |
| **Manual IP Address** | 设备的 IP 地址 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartFileServer` | 启动 Android 文件服务器（指定 USB/网络/端口） | `UAndroidFileServerBPLibrary` |
| `StopFileServer` | 停止文件服务器 | `UAndroidFileServerBPLibrary` |
| `IsFileServerRunning` | 查询服务器运行状态（返回 `EAFSActiveType`） | `UAndroidFileServerBPLibrary` |

### 连接类型枚举

`EAFSActiveType`：
- `None` (0) — 未运行
- `USBOnly` (1) — 仅 USB
- `NetworkOnly` (2) — 仅网络
- `Combined` (3) — USB + 网络同时

### 使用示例（蓝图描述）

**启动 USB 文件服务器：**
1. 创建 `StartFileServer` 节点
2. `bUSB` = true, `bNetwork` = false
3. `Port` 默认 57099
4. 返回值为 bool，表示是否成功发起启动请求

**查询服务器状态：**
1. 创建 `IsFileServerRunning` 节点
2. 返回 `EAFSActiveType` 枚举，可通过分支节点判断当前连接类型

## C++ 用法

### 头文件引入

```cpp
#include "AndroidFileServerBPLibrary.h"
```

### 基本用法

```cpp
// 启动 USB 文件服务器（默认端口 57099）
bool bStarted = UAndroidFileServerBPLibrary::StartFileServer(true, false);

// 启动 USB + 网络混合模式
bool bStarted = UAndroidFileServerBPLibrary::StartFileServer(true, true, 57099);

// 查询运行状态
EAFSActiveType::Type Status = UAndroidFileServerBPLibrary::IsFileServerRunning();
if (Status == EAFSActiveType::USBOnly)
{
    UE_LOG(LogTemp, Log, TEXT("AFS running on USB"));
}

// 停止文件服务器
UAndroidFileServerBPLibrary::StopFileServer(true, true);
```

> 所有 API 均为 `static` + `BlueprintCallable`，无需实例化对象。

## Demo 示例

以下是一个最小化示例：在 Android 设备上启动文件服务器，检查状态，然后停止。

### MyAFSActor.h

```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyAFSActor.generated.h"

UCLASS()
class AMyAFSActor : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable)
    void StartAndCheckAFS();

    UFUNCTION(BlueprintCallable)
    void StopAFS();
};
```

### MyAFSActor.cpp

```cpp
#include "MyAFSActor.h"
#include "AndroidFileServerBPLibrary.h"

void AMyAFSActor::StartAndCheckAFS()
{
    // 启动 USB + 网络模式
    bool bOk = UAndroidFileServerBPLibrary::StartFileServer(true, true, 57099);
    UE_LOG(LogTemp, Log, TEXT("AFS Start request: %s"), bOk ? TEXT("OK") : TEXT("Failed"));

    // 查询状态
    auto Status = UAndroidFileServerBPLibrary::IsFileServerRunning();
    UE_LOG(LogTemp, Log, TEXT("AFS Status: %d"), (int)Status);
}

void AMyAFSActor::StopAFS()
{
    UAndroidFileServerBPLibrary::StopFileServer(true, true);
    UE_LOG(LogTemp, Log, TEXT("AFS Stopped"));
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "AndroidFileServer" });
```

> 注意：`AndroidFileServer` 模块本身只依赖 `Core`，非常轻量。

## 模块依赖

### AndroidFileServer (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和模块系统 |
| `CoreUObject` | UObject 反射系统（私有） |
| `Engine` | 引擎核心（私有） |
| `Slate` / `SlateCore` | UI 框架（私有） |
| `Launch` | Android 平台启动支持（仅 Android 平台） |

### AndroidFileServerEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 反射 |
| `UnrealEd` | 编辑器功能（设置面板注册） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-16 | `07941336` | Unshelved from pending changelist '45879216' | 从待处理变更列表中恢复 |
| 2025-09-09 | `51ed33ec` | Fix java compilation due to missing import | 修复 Java 编译错误（缺少 import） |
| 2025-09-09 | `82dd3d34` | AFS interface included only on embed #jira UE-318701 | 修复 AFS 接口仅在嵌入模式下包含的问题 |

### 维护评价

- **创建时间**：2022 年 2 月，约 4 年历史
- **最近更新**：2025 年 9 月，有实质性 bug 修复和接口修正
- **活跃度**：**维护中** — 最近 1 年内有功能性更新
- **已知限制**：
  - 默认端口 57099 不可配置（蓝图接口支持自定义端口，但 Android Service 层默认固定）
  - Shipping 构建中默认不嵌入，需手动开启 `IncludeInShipping`
  - 网络模式需要设备和 PC 在同一局域网
- **推荐使用**：✅ 推荐，这是 UE5 Android 开发工作流的标配工具

## 架构概览

```
PC 端 (UE Editor)                     Android 设备端
┌─────────────────┐                  ┌──────────────────────────────┐
│ UnrealAndroid   │  USB / WiFi      │ RemoteFileManagerActivity    │
│ FileTool        │◄────────────────►│  ↓ (Intent 驱动)             │
│ (编辑器内置)     │  Socket          │ RemoteFileManagerService     │
└─────────────────┘  端口 57099      │  ↓ (Foreground Service)      │
                                     │ RemoteFileManager            │
                                     │  ↓ (socket 线程)             │
                                     │ 文件系统操作 (read/write/dir) │
                                     └──────────────────────────────┘
```

文件路径别名系统（`FixupPath`）：
- `^ext/` → 设备外部存储目录
- `^int/` → 设备内部存储目录
- `^storage/` → 外部 SD 卡根目录
- `^project/` → UE 项目目录
- `^logs/` → 日志目录
- `^mainobb` / `^patchobb` → OBB 文件路径

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidFileServer)
- 官方文档：无（.uplugin 的 DocsURL 为空）
