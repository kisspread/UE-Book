# Bridge

> Megascans Link for Quixel Bridge.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Quixel 桥接 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `Bridge` (Editor), `MegascansPlugin` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-09 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge) | |

## 用途

Bridge 插件是 Quixel Bridge 客户端与 Unreal Engine 5 编辑器之间的桥梁。它并非一个独立的功能模块，而是一个**资产导入和材质管理系统**，其核心作用是：
1.  **建立通信**：通过本地 TCP 服务器 (`FTCPServer`) 监听 Quixel Bridge 应用程序的连接请求，实现双向通信。
2.  **资产导入**：接收来自 Bridge 客户端的 JSON 数据，解析后按照资产类型（3D 模型、3D 植物、表面材质、图集等）分派到对应的导入器（`FImportProgressive3D`， `FImportProgressiveSurfaces` 等）。
3.  **材质管理**：提供材质实例创建、材质预设管理、材质混合（`FMaterialBlend`）以及将材质应用到场景中已选对象等功能。
4.  **配置管理**：提供设置面板 (`MegascansSettingsWindow`)，允许用户配置自动填充植被画家、覆盖主材质等选项。

简而言之，它解决了从 Quixel Bridge 库中**高效、自动化地**将 Megascans 资产（模型、材质、纹理）导入并应用到 UE5 项目和场景中的问题，是 Quixel Megascans 工作流的关键集成组件。

## 使用场景

-   **场景美术**：在 Quixel Bridge 中浏览并选择 Megascans 资产（如岩石、植被、地面材质），点击“发送到 UE5”后，资产自动导入项目并生成材质实例。你可以将表面材质拖拽到场景中的 Actor 上进行应用。
-   **材质混合**：需要混合多个表面材质以创造新的复合材质（如草地与泥土的混合）时，可以使用插件提供的材质混合工具，将选中的材质实例混合生成新的混合材质。
-   **植被填充**：在项目设置中启用“Auto-Populate Foliage Painter”后，导入的 3D 植物资产会自动添加到 Foliage 类型列表中，方便直接使用植被画家工具进行绘制。
-   **批量管理**：通过设置，可以为所有导入的 3D 资产、表面材质或植物指定自定义的主材质，替代默认的 Megascans 材质。

## 蓝图用法

Bridge 插件本身不提供广泛的蓝图可调用函数。其功能主要通过编辑器 UI 和与 Bridge 客户端的通信触发。主要的蓝图交互点是通过其暴露的设置类（`UPROPERTY`）在编辑器中进行配置。

### 核心设置

这些设置可以在“项目设置” -> “Plugins” -> “Megascans” 中找到。

| 设置类 | 属性 | 说明 |
|---|---|---|
| `UMegascansSettings` | `bCreateFoliage` | 是否在导入 3D 植物时自动填充 Foliage 类型到 Foliage 编辑器 |
| `UMegascansSettings` | `bApplyToSelection` | 导入表面材质时，是否自动应用到编辑器中当前选中的 Actor |
| `UMaterialBlendSettings` | `BlendedMaterialName` | 材质混合实例的默认名称 |
| `UMaterialBlendSettings` | `BlendedMaterialPath` | 材质混合实例的默认存储路径 |
| `UMaterialAssetSettings` | `MasterMaterial3d` | 所有 3D 资产使用的自定义主材质路径 |
| `UMaterialAssetSettings` | `MasterMaterialSurface` | 所有表面材质使用的自定义主材质路径 |
| `UMaterialAssetSettings` | `MasterMaterialPlant` | 所有植物使用的自定义主材质路径 |
| `UMaterialPresetsSettings` | `MasterMaterial3d/Surface/Plant` | 临时覆盖设置，用于在一次会话中更改主材质 |

### 使用示例（蓝图描述）

你无法直接在蓝图图表中拖拽 Bridge 的节点。其工作流是：
1.  在 Quixel Bridge 应用中选择资产。
2.  通过 Bridge UI 点击发送到 Unreal Engine。
3.  插件内部的 `FAssetsImportController::DataReceived` 接收数据并处理导入。
4.  根据你在“项目设置”中配置的选项，自动执行创建植被类型、应用材质等操作。

## C++ 用法

此插件的公共 C++ API 非常有限，主要用于内部模块通信和启动服务器。开发者通常不需要直接调用其 API，而是通过它提供的编辑器 UI 来使用功能。

### 头文件引入

```cpp
#include "MegascansPlugin/IMegascansLiveLinkModule.h" // 模块接口
#include "Bridge/TCPServer.h" // TCP 服务器
#include "Bridge/AssetsImportController.h" // 导入控制器
```

### 基本用法

启动或获取插件实例，并检查其可用性。

```cpp
// 检查 MegascansPlugin 模块是否已加载
if (IMegascansLiveLinkModule::IsAvailable())
{
    // 获取模块引用 (如果模块已加载)
    IMegascansLiveLinkModule& LiveLinkModule = IMegascansLiveLinkModule::Get();
    // 模块本身没有暴露额外的公共函数，主要用于确认模块存在
}

// 获取资产导入控制器单例 (用于接收来自Bridge客户端的数据)
TSharedPtr<FAssetsImportController> ImportController = FAssetsImportController::Get();
if (ImportController.IsValid())
{
    // 通常不会直接调用，而是由 Bridge 客户端通过 TCP 发送数据，由控制器内部处理
    // ImportController->DataReceived(JsonStringFromBridge); 
}
```

### 进阶用法

直接操作 TCP 服务器（非常规用法，仅用于理解内部机制或扩展）。

```cpp
// FTCPServer 是一个单例，由模块内部管理。
// 理论上，可以通过 FModuleManager 获取模块并访问，但插件没有暴露此接口。
// 以下为概念示例，说明其工作原理：
// 1. 插件启动时，会创建一个 FTCPServer 实例监听 127.0.0.1:13429。
// 2. Quixel Bridge 客户端连接到此端口。
// 3. 客户端发送包含资产信息的 JSON 字符串。
// 4. FTCPServer 将字符串放入静态队列 ImportQueue。
// 5. FAssetsImportController 从队列中取出数据并分发给具体的导入器。
```

## Demo 示例

由于 Bridge 插件的功能主要由编辑器 UI 和外部 Bridge 客户端驱动，没有简单的最小代码示例来演示其用法。一个可编译的最小“使用”示例就是在你的项目中安装并启用此插件，然后按照**使用场景**中的步骤在 Quixel Bridge 中进行操作。

## 模块依赖

根据插件的 `.uplugin` 和 `Build.cs` 分析，除了标准依赖外，此插件有以下独特依赖：

| 模块 | 用途 |
|---|---|
| `EditorScriptingUtilities` | 为编辑器脚本（如可能被内部使用的蓝图函数库）提供支持 |
| `MetaHumanSDK` | 支持与 MetaHuman 相关资产的可能集成（例如 MetaHuman 角色的皮肤材质） |
| `Networking` / `Sockets` | TCP 服务器实现所需的基础网络功能 |

**注意**：插件内部还依赖 `WebBrowser` 模块（根据 git commit 记录），用于显示可能的内嵌网页内容。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4797537` | Fix crash in UMaterialPresetsSettings::PostEditChangeProperty when master material slots are empty o | 修复当主材质插槽为空时，材质预设设置界面崩溃的问题 |
| 2026-04-16 | `aea11131` | Clean up WebBrowser module and init settings, handle module init failures | 清理 WebBrowser 模块代码，初始化设置，并处理模块初始化失败的情况 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 格式 |
| 2026-04-06 | `3e98cc7e` | TLazyObjectPtr Deprecation pt 3: | 继续处理废弃的 TLazyObjectPtr 类型（第三部分） |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 与包保存状态相关的代码检查或修复 |

### 维护评价

-   **年龄**：插件创建于 2020 年底，属于较新的项目。
-   **活跃度**：**非常活跃**。从 2026 年 3 月至 5 月的提交记录看，维护频繁，内容包括**关键崩溃修复**、代码清理、依赖更新和代码风格迁移。这表明 Epic 和 Quixel 团队仍在积极维护此插件，以确保其稳定性和与引擎新特性的兼容性。
-   **已知问题**：代码库中可能存在一些历史遗留结构（如多个 `UPROPERTY(Transient)` 的设置类用于覆盖），但近期修复了材质预设相关的崩溃，表明问题正在被解决。
-   **推荐使用**：**强烈推荐**。作为 Quixel Megascans 工作流的官方集成方案，它功能完整、维护活跃。如果你的工作流涉及 Megascans 资产，这是必不可少的工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge)
-   [官方文档](https://help.quixel.com/hc/en-us/sections/360005846137-Quixel-Bridge-for-Unreal-Engine-5)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge/Source) （插件源码中未发现独立的测试文件）