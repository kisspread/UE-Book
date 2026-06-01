# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获数据导入编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设备配置） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

---

> **本文档聚焦于 `LiveLinkHubWorkerManager` 子模块。** 完整插件包含 7 个子模块，其余模块文档待补充。

---

## 用途

Capture Manager Editor 是虚幻引擎虚拟制片管线中**捕获数据（Capture Data）导入流水线**的核心插件。它解决的核心问题是：如何将 LiveLink Hub 设备采集到的面部/身体捕获数据（archive），高效地下载到本地并转化为虚幻引擎可用的资产（动画、元数据等）。

`LiveLinkHubWorkerManager` 模块是这条流水线的**编辑器侧 worker 管理层**，负责：

1. **发现 LiveLink Hub 设备** — 通过 UDP 广播/消息系统探测网络上可用的捕获设备
2. **建立并维持连接** — 管理与多个 Hub 设备的 TCP 连接生命周期
3. **并行数据下载** — 为每个连接创建独立的 import worker，支持多设备同时下载捕获文件
4. **触发数据处理** — 下载完成后自动启动 ingest 流程，将原始数据转化为引擎资产

简而言之，这是一个**面向虚拟制片团队的批量捕获数据导入系统**。

## 使用场景

- 你有一台 LiveLink Hub 设备在片场采集面部表情数据，需要批量导入到 UE 关卡中 → 使用 Capture Manager
- 你需要同时管理多台捕获设备，从多台 Hub 并行下载数据 → `LiveLinkHubWorkerManager` 的多 worker 架构
- 你想在 UEFN 中使用真实拍摄的捕获数据 → 通过本插件将数据转换为引擎资产

## 蓝图用法

本模块 (`LiveLinkHubWorkerManager`) 主要提供 C++ API，未直接暴露 `BlueprintCallable` 节点。蓝图层面的捕获导入功能由 `CaptureManagerIngestBlueprint` 和 `CaptureManagerDeviceBlueprint` 模块提供。

如需在蓝图中触发导入流程，应使用上述 sibling 模块的蓝图接口。本模块作为底层连接管理层，由其他模块内部调用。

### 核心节点（其他模块调用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetManager` | 获取全局 Worker Manager 单例 | `FLiveLinkHubWorkerManagerModule` |
| `Disconnect` | 断开所有 Hub 设备连接 | `FLiveLinkHubWorkerManager` |
| `IsConnected` | 查询是否与任何 Hub 设备保持连接 | `FLiveLinkHubWorkerManager` |
| `SendDiscoveryResponse` | 向指定地址发送发现响应 | `FLiveLinkHubWorkerManager` |

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkHubWorkerManagerModule.h"
#include "LiveLinkHubWorkerManager.h"
```

### 基本用法

获取模块单例并检查连接状态：

```cpp
// 来源: Public/LiveLinkHubWorkerManagerModule.h

// 获取 Worker Manager 模块
FLiveLinkHubWorkerManagerModule& Module = FModuleManager::Get().LoadModuleChecked<FLiveLinkHubWorkerManagerModule>("LiveLinkHubWorkerManager");

// 获取管理器实例
TSharedRef<FLiveLinkHubWorkerManager> Manager = Module.GetManager();

// 检查是否已连接到 Hub 设备
bool bConnected = Manager->IsConnected();

// 断开所有连接
Manager->Disconnect();
```

### 进阶用法

通过消息系统发送发现响应，用于自定义设备发现流程：

```cpp
// 来源: Public/LiveLinkHubWorkerManager.h

// 构造发现响应消息
TSharedRef<FLiveLinkHubWorkerManager> Manager = Module.GetManager();

FDiscoveryResponse* Response = new FDiscoveryResponse();
// ... 填充响应数据 ...

FMessageAddress ReceiverAddress; // 目标 Hub 地址
Manager->SendDiscoveryResponse(Response, ReceiverAddress);
```

## Demo 示例

以下展示如何在编辑器模块中集成 LiveLinkHubWorkerManager 的最小示例：

```cpp
// MyCaptureModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyCaptureModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnCaptureRequested();
};
```

```cpp
// MyCaptureModule.cpp
#include "MyCaptureModule.h"
#include "LiveLinkHubWorkerManagerModule.h"
#include "LiveLinkHubWorkerManager.h"

void FMyCaptureModule::StartupModule()
{
    // 确保 LiveLinkHubWorkerManager 模块已加载
    FModuleManager::Get().LoadModuleChecked<FLiveLinkHubWorkerManagerModule>("LiveLinkHubWorkerManager");
}

void FMyCaptureModule::ShutdownModule()
{
}

void FMyCaptureModule::OnCaptureRequested()
{
    auto& WorkerModule = FModuleManager::Get().GetModuleChecked<FLiveLinkHubWorkerManagerModule>("LiveLinkHubWorkerManager");
    TSharedRef<FLiveLinkHubWorkerManager> Manager = WorkerModule.GetManager();

    if (!Manager->IsConnected())
    {
        UE_LOG(LogTemp, Warning, TEXT("No LiveLink Hub device connected. Waiting for discovery..."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Hub connected, capture data download will be handled automatically."));
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。具体依赖关系需参考 `LiveLinkHubWorkerManager.Build.cs`，但基于头文件分析，本模块内部依赖 Capture Manager 的 TCP 客户端、任务进度系统和数据处理管线等私有模块。

| 模块 | 用途 |
|---|---|
| `CaptureManager` (推测) | TCP 客户端处理 (`FTcpClientHandler`)、任务进度 (`FTaskProgress`) |
| `LiveLinkHub` (推测) | 消息协议定义 (`FConnectRequest`, `FDiscoveryResponse` 等) |
| `Messaging` (推测) | 消息地址系统 (`FMessageAddress`) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 设备蓝图模块中泛化设备术语命名 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式 ingest 蓝图 API 移至 Blocking 子分类 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 子模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退了一次提交（CL53274396） |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 再次添加 DeviceBlueprint 模块 |

### 维护评价

**活跃维护**。

- **创建时间**：2025 年 2 月，属于较新的插件（约 1 年历史）
- **更新频率**：最近一次更新在 2026 年 4 月底，距今约 2 个月内，保持活跃
- **更新内容**：近期主要在扩展设备蓝图模块、优化 API 分类，说明插件仍在**功能扩展阶段**
- **模块设计**：7 个子模块的架构表明这是一个设计严谨、职责分明的大型系统
- **注意事项**：`EnabledByDefault=false`，需要手动在项目设置中启用
- **推荐**：虚拟制片团队推荐使用；个人项目如无 LiveLink Hub 设备则无需启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor/Source/LiveLinkHubWorkerManager/Tests)（路径推测，待确认）