# Bridge

> Megascans Link for Quixel Bridge.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质预设、Web 前端 UI 资源、图标） |
| 模块 | `Bridge` (Editor), `MegascansPlugin` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-09 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Bridge) | |

## 用途

Bridge 是 Quixel Bridge（原 Megascans）桌面应用程序与 Unreal Engine 之间的桥梁插件。它在编辑器内嵌入一个基于 Web 的界面，让用户可以直接浏览、下载和导入 Quixel Megascans 资产（3D 模型、表面材质、植物、图集等），无需离开 UE 编辑器。

插件的核心架构是：在 UE 编辑器中启动一个本地 Node.js 进程作为后端，通过内嵌的 Chromium WebBrowser 加载本地 HTML/JS 前端界面，前端通过 JavaScript 绑定（`UBrowserBinding`）与 UE 的 C++ 后端通信，完成资产的下载和导入流程。同时还有一个 TCP 服务器（`FTCPServer`）监听 127.0.0.1:13429 端口，用于接收来自 Quixel Bridge 桌面应用的资产数据。

随着 Epic Games 将 Quixel Megascans 免费资源迁移至 Fab 平台，此插件正在逐步适配新的 Fab 工作流，但其核心导入逻辑仍然围绕 Megascans 资产格式构建。

## 使用场景

- 你需要从 Quixel Megascans 库中导入高质量的 3D 扫描资产（建筑、岩石、植被等）到你的 UE 项目中
- 你需要快速将扫描的表面材质（Surface）应用到场景中的已有 Actor 上
- 你需要批量导入大量 Megascans 资产，而不是逐个手动下载和导入
- 你需要将多个表面材质混合（Blend）生成新的复合材质
- 你需要在导入植物资产时自动填充 Foliage Painter

## 蓝图用法

此插件几乎不暴露蓝图接口。唯一的 BlueprintCallable 函数是 `UVersionInfoHandler::Get()`，用于获取资产版本信息。插件的主要交互通过编辑器 UI 完成，而非蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UVersionInfoHandler::Get()` | 获取资产版本信息处理器的单例实例 | `UVersionInfoHandler` |

### 使用示例（蓝图描述）

此插件不通过蓝图使用。所有操作通过编辑器工具栏的 "Bridge" 按钮或 Content Browser 右键菜单的 "Add Quixel Content" 选项启动。

## C++ 用法

此插件主要面向内部使用，不鼓励外部开发者直接调用其 C++ API。以下是架构层面的关键类和接口。

### 头文件引入

```cpp
#include "IBridgeModule.h"
#include "IMegascansLiveLinkModule.h"
```

### 基本用法 — 检查插件可用性

```cpp
// 检查 Bridge 模块是否已加载
if (IBridgeModule::IsAvailable())
{
    IBridgeModule& BridgeModule = IBridgeModule::Get();
    // 模块可用
}

// 检查 MegascansPlugin 模块是否已加载
if (IMegascansLiveLinkModule::IsAvailable())
{
    IMegascansLiveLinkModule& MSModule = IMegascansLiveLinkModule::Get();
    // 模块可用
}
```

### 进阶用法 — 资产导入控制器

`FAssetsImportController` 是接收 Bridge 前端数据的核心入口。它通过 JSON 字符串接收资产数据，然后根据资产类型（`3d`、`3dplant`、`atlas`、`surface`）分发给不同的导入工厂：

```cpp
// FAssetsImportController 是单例
auto ImportController = FAssetsImportController::Get();

// 接收来自 Bridge 前端的 JSON 数据
// 内部会解析 JSON 并根据 assetType 分发到 IAssetImportFactory
ImportController->DataReceived(JsonDataString);
```

导入工厂 `IAssetImportFactory` 使用工厂模式，根据 `EAssetImportType` 创建具体的导入器：
- `FImportUAssetNormal` — 标准 UAsset 导入（已下载的 .uasset 文件直接导入）
- `FImportProgressive3D` — 3D 资产的渐进式导入（先显示低质量预览，再替换为高质量）
- `FImportProgressiveSurfaces` — 表面材质的渐进式导入

```cpp
// 工厂模式创建导入器
auto Importer = IAssetImportFactory::CreateImporter(EAssetImportType::MEGASCANS_UASSET);
Importer->ImportAsset(JsonObject);
```

### 进阶用法 — Node.js 进程管理

Bridge 模块会启动一个本地 Node.js 进程来运行 Quixel Bridge 的 Web 后端：

```cpp
// FNodeProcessManager 是单例
auto NodeManager = FNodeProcessManager::Get();

// 启动 Node.js 进程（从 ThirdParty 目录加载）
NodeManager->StartNodeProcess();

// 重启 Node.js 进程
NodeManager->RestartNodeProcess();
```

Node.js 进程的端口信息通过 `UNodePort` 获取，存储在 `ThirdParty/node_port.txt` 文件中：

```cpp
UNodePort* NodePortInfo = NewObject<UNodePort>();
FString Port = NodePortInfo->GetNodePort();
bool bRunning = NodePortInfo->IsNodeRunning();
```

### 进阶用法 — TCP 服务器通信

`FTCPServer` 在端口 13429 上监听来自 Quixel Bridge 桌面应用的连接：

```cpp
// FTCPServer 继承自 FRunnable，在独立线程中运行
// 启动时自动监听 127.0.0.1:13429
FTCPServer* SocketListener = new FTCPServer();

// 收到的资产数据通过静态队列传递
FString Message;
while (FTCPServer::ImportQueue.Dequeue(Message))
{
    // 处理导入消息
}
```

## Demo 示例

此插件是编辑器级插件，不提供可编译的独立示例。以下是使用其 Settings API 的最小示例：

```cpp
// MegascansSettingsExample.h
#pragma once
#include "CoreMinimal.h"

// Build.cs 依赖: MegascansPlugin
```

```cpp
// MegascansSettingsExample.cpp
#include "MSSettings.h"

void ConfigureMegascansImport()
{
    // 创建设置对象
    UMegascansSettings* Settings = NewObject<UMegascansSettings>();

    // 启用自动填充 Foliage Painter（适用于 3D 植物资产）
    Settings->bCreateFoliage = true;

    // 启用将导入的 Surface 自动应用到选中的 Actor
    Settings->bApplyToSelection = true;
}

void ConfigureMaterialOverrides()
{
    // 配置自定义主材质覆盖
    UMaterialAssetSettings* MatSettings = NewObject<UMaterialAssetSettings>();

    // 为 3D 资产指定自定义主材质路径
    MatSettings->MasterMaterial3d = TEXT("/Game/MyMaterials/M_Master3D");

    // 为 Surface 指定自定义主材质路径
    MatSettings->MasterMaterialSurface = TEXT("/Game/MyMaterials/M_MasterSurface");

    // 为植物指定自定义主材质路径
    MatSettings->MasterMaterialPlant = TEXT("/Game/MyMaterials/M_MasterPlant");
}
```

## 模块依赖

### Bridge 模块（公共依赖）

| 模块 | 用途 |
|---|---|
| `Projects` | 插件/项目信息查询 |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `UnrealEd` | 编辑器功能 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `UMG` | UMG UI 框架 |
| `Json` | JSON 解析 |
| `WebBrowser` | 内嵌 Web 浏览器（Chromium） |
| `Networking` | 网络功能 |
| `Sockets` | Socket 通信 |
| `ToolMenus` | 编辑器菜单扩展 |
| `ContentBrowserData` | 内容浏览器数据 |
| `PlacementMode` | 放置模式 |
| `MegascansPlugin` | 本插件的资产导入模块 |
| `MetaHumanSDKEditor` | MetaHuman 集成 |
| `ApplicationCore` | 应用核心 |

### MegascansPlugin 模块（私有依赖）

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册表 |
| `ContentBrowser` | 内容浏览器集成 |
| `LevelEditor` | 关卡编辑器集成 |
| `Settings` | 编辑器设置 |
| `MaterialEditor` | 材质编辑器 |
| `FoliageEdit` | 植被编辑 |
| `Foliage` | 植被系统 |
| `HTTP` | HTTP 请求 |
| `StaticMeshEditor` | 静态网格编辑器 |
| `MeshBuilder` | 网格构建 |
| `TargetPlatform` | 目标平台 |
| `EditorScriptingUtilities` | 编辑器脚本工具 |
| `MetaHumanSDKEditor` | MetaHuman 集成 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `EditorScriptingUtilities` | 编辑器脚本辅助 |
| `MetaHumanSDK` | MetaHuman 角色支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-25 | `d5d2a3741693` | 修复 macOS WebKit 下 Fab 和 Quixel 插件的 Tab 显示/隐藏可见性 bug |
| 2025-08-19 | `501b04d0c6bd` | 适配 macOS WebKit WebBrowser 插件 |
| 2025-08-05 | `5a9ca4ac32be` | 修复 NodeProcess 和 LiveCoding 传 NULL 给 CreateProc 参数的问题 |

### 维护评价

- **创建时间**：2020 年 11 月，约 5 年前
- **最近更新**：2025 年 9 月，最近一次更新在约 1 个月内，属于活跃维护
- **维护状态**：**活跃维护中**。近期更新集中在 macOS WebKit 适配和进程管理修复，说明 Epic 仍在积极维护此插件
- **已知限制**：仅支持 Win64、Mac、Linux 三个平台；需要 WebBrowser 插件启用；依赖本地 Node.js 进程
- **推荐程度**：**推荐使用**。这是 Quixel Megascans 资产导入 UE 的官方通道，如果你使用 Quixel/Fab 的 Megascans 资产，这是必装插件。随着 Epic 将免费 Megascans 资产迁移到 Fab 平台，此插件正在逐步适配新工作流

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Bridge)
- [官方文档](https://help.quixel.com/hc/en-us/sections/360005846137-Quixel-Bridge-for-Unreal-Engine-5)
- [Quixel 官网](https://www.quixel.se)
