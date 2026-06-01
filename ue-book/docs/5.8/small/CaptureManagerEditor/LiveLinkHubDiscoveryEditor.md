# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

CaptureManagerEditor 是 Epic 虚拟制作管线中的**捕获数据导入工具链**，负责将外部设备（如手机扫描、LiDAR 捕获等）产生的 Capture 存档数据导入到 Unreal Engine 或 UEFN（Unreal Editor for Fortnite）中，自动创建所需的资产（Mesh、Texture、Media 等）。

该插件的核心工作流程：
1. **设备发现**：通过 UDP 组播消息发现局域网中的 LiveLink Hub 服务器（`LiveLinkHubDiscoveryEditor`）
2. **数据导出**：LiveLink Hub 服务器将捕获数据通过 HTTP 服务暴露给 UE（`LiveLinkHubExportServer`）
3. **工人管理**：协调多个工作节点并行处理导入任务（`LiveLinkHubWorkerManager`）
4. **数据摄取**：解析捕获存档并生成 UE 资产（`DataIngestCoreEditor`、`CaptureManagerIngestBlueprint`）
5. **设备蓝图**：提供蓝图接口供用户自定义设备交互逻辑（`CaptureManagerDeviceBlueprint`）

插件默认禁用（`EnabledByDefault: false`），需要在项目设置或编辑器中手动启用。

## 使用场景

- 你使用 **RealityCapture** 或其他捕获工具扫描了真实场景，需要将 `.cap` 存档导入 UE → 用 CaptureManagerEditor
- 你在 **虚拟制作** 管线中需要从 LiveLink Hub 自动发现并导入移动设备的捕获数据
- 你在开发 **UEFN** 内容，需要将外部捕获资产批量导入 Fortnite 生态
- 你需要自定义捕获设备的交互逻辑（如手柄控制、UI 反馈）→ 使用 `CaptureManagerDeviceBlueprint` 模块

## 蓝图用法

### 核心节点

该插件的蓝图 API 主要分布在以下模块中：

| 节点 | 说明 | 所在模块 |
|---|---|---|
| 设备交互蓝图接口 | 自定义捕获设备的发现、连接和控制逻辑 | `CaptureManagerDeviceBlueprint` |
| 数据摄取蓝图接口 | 自定义导入流程、资产类型映射和后处理 | `CaptureManagerIngestBlueprint` |
| 编辑器设置访问 | 读写 CaptureManager 的编辑器偏好设置 | `CaptureManagerEditorSettings` |

> 注：`CaptureManagerDeviceBlueprint` 和 `CaptureManagerIngestBlueprint` 模块专为蓝图用户设计，提供 BlueprintCallable/Broadcastable 接口。具体节点请参考引擎蓝图编辑器中的搜索。

### 使用示例（蓝图描述）

1. 在项目设置中启用 CaptureManagerEditor 插件
2. 在蓝图中通过 `CaptureManagerIngestBlueprint` 模块获取可用的导入源列表
3. 选择目标捕获存档，触发导入流程
4. 使用 `CaptureManagerDeviceBlueprint` 模块监听设备状态变化事件，更新 UI 反馈

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkHubDiscoveryEditorModule.h"
#include "DiscoveryResponder.h"
```

### 基本用法：监听设备发现消息

`FDiscoveryResponder` 内部使用 `FMessageEndpoint` 接收 UDP 组播发现请求，并返回 LiveLink Hub Export Server 的连接信息。

```cpp
// 引擎内部自动管理，模块启动时创建 DiscoveryResponder
// LiveLinkHubDiscoveryEditorModule.cpp
void FLiveLinkHubDiscoveryEditor::StartupModule()
{
    DiscoveryResponder = MakeUnique<UE::CaptureManager::FDiscoveryResponder>();
}

void FLiveLinkHubDiscoveryEditor::ShutdownModule()
{
    DiscoveryResponder.Reset();
}
```

### 进阶用法：自定义发现响应

如果需要扩展发现协议或自定义导出服务器信息：

```cpp
// DiscoveryResponder 内部流程：
// 1. 接收 FDiscoveryRequest 消息
// 2. 调用 GetExportServerInfo() 获取当前导出服务器信息
// 3. 调用 GetWorkerManager() 获取工人管理器状态
// 4. 返回包含主机名和服务器信息的响应

// 获取导出服务器信息的内部实现
static TValueOrError<FLiveLinkHubExportServer::FServerInfo, 
                      FLiveLinkHubExportServer::EServerError> 
GetExportServerInfo();
```

## Demo 示例

一个最小的发现响应器实现示例：

```cpp
// MyDiscoveryHandler.h
#pragma once

#include "CoreMinimal.h"
#include "DiscoveryResponder.h"

class FMyDiscoveryHandler
{
public:
    FMyDiscoveryHandler();
    ~FMyDiscoveryHandler();

private:
    TUniquePtr<UE::CaptureManager::FDiscoveryResponder> Responder;
};
```

```cpp
// MyDiscoveryHandler.cpp
#include "MyDiscoveryHandler.h"

FMyDiscoveryHandler::FMyDiscoveryHandler()
{
    // DiscoveryResponder 会在构造时自动启动消息端点
    // 并开始监听局域网上的 LiveLink Hub 发现请求
    Responder = MakeUnique<UE::CaptureManager::FDiscoveryResponder>();
}

FMyDiscoveryHandler::~FMyDiscoveryHandler()
{
    Responder.Reset();
}
```

> 实际使用中，该插件由引擎模块自动管理生命周期（通过 `IModuleInterface`），一般不需要手动实例化。

## 模块依赖

该插件包含 7 个模块，模块间存在以下内部依赖关系：

| 模块 | 用途 |
|---|---|
| `LiveLinkHubExportServer` | 提供 HTTP 导出服务器，将捕获数据暴露给外部客户端 |
| `LiveLinkHubWorkerManager` | 管理并行导入工作节点，协调任务分配 |
| `LiveLinkHubDiscoveryEditor` | UDP 组播发现协议实现，自动发现局域网中的 LiveLink Hub 服务 |
| `DataIngestCoreEditor` | 核心数据摄取逻辑，解析捕获存档并生成 UE 资产 |
| `CaptureManagerDeviceBlueprint` | 设备交互蓝图 API |
| `CaptureManagerIngestBlueprint` | 数据摄取蓝图 API |
| `CaptureManagerEditorSettings` | 编辑器偏好设置存储 |

> 注：模块间具体依赖关系需查看各模块的 `.Build.cs` 文件，当前分析基于 `LiveLinkHubDiscoveryEditor` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 设备蓝图中泛化设备术语，支持更多设备类型 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式摄取蓝图 API 移至独立子类别，改善蓝图节点组织 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增设备蓝图模块，扩展设备交互能力 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退了之前的改动（CL53274396） |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次添加设备蓝图模块（后被回退并重新提交） |

### 维护评价

- **创建时间**：2025-02-04，约 1 年历史，属于较新的插件
- **活跃程度**：最近一周（2026-04-29 ~ 2026-04-30）有密集的功能更新，正在积极扩展蓝图 API
- **功能成熟度**：核心发现和导入流程已稳定，当前主要在完善蓝图接口层
- **已知限制**：
  - 默认禁用，需手动启用
  - 依赖 LiveLink Hub 基础设施
  - 模块命名中含 `Editor` 但类型标记为 `Runtime`，可能存在打包相关限制
- **推荐程度**：⭐⭐⭐⭐ 如果你的虚拟制作管线需要捕获数据导入功能，推荐使用。该插件由 Epic 官方维护，处于活跃开发阶段。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档]()（暂无）
- [LiveLink Hub 相关文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/live-link-in-unreal-engine)