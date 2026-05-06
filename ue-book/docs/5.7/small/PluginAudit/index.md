# Plugin Audit

> Editor plugin for auditing plugin connectivity.

| 属性 | 值 |
|---|---|
| 中文名 | 插件审核 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginAudit` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PluginAudit) | |

## 用途

`PluginAudit` 是一个编辑器工具插件，用于**审核插件之间的连接关系**，尤其是 **Game Features 插件** 的依赖完整性。它通过可视化的列表和状态标记，帮助开发者：

- 快速查看所有已启用插件的依赖链
- 模拟禁用某个插件后的连锁影响（哪些插件会因此缺少依赖）
- 识别缺失的 Game Feature 插件或依赖循环等潜在问题
- 通过双击插件名称直接打开**插件引用查看器**（Plugin Reference Viewer）

该插件主要面向大型项目中使用大量 Game Features 和自定义插件的团队，用于在部署或重构前评估改动风险。

## 使用场景

- **项目复杂度提升**：当项目包含 50+ 插件，且依赖关系错综复杂时，手动检查依赖变得不可行。
- **Game Features 管理**：使用 `GameFeature` 框架时，插件可能依赖于特定的 Game Feature 数据（如标签源、内容根目录），`PluginAudit` 可以标记出缺失的依赖。
- **插件禁用影响评估**：在临时禁用某个插件（例如旧版角色系统）之前，模拟禁用效果并查看哪些功能会受影响。
- **新人入职/代码审查**：快速了解当前插件拓扑结构，检查是否存在不合理依赖。

## 蓝图用法

`PluginAudit` **不提供任何 BlueprintCallable 函数**。它是一个纯编辑器工具，所有交互通过编辑器界面完成。用户通常从 **Window → Plugin Audit**（如果已注册菜单项）或通过命令行 `PluginAudit ` 打开。

### 交互方式

| 操作 | 说明 |
|---|---|
| 双击插件行 | 打开该插件的**插件引用查看器** |
| 右键上下文菜单 | 提供“打开插件属性”、“在引用查看器中查看” |
| 搜索框 | 按插件名称过滤列表 |
| 全局禁用复选框 | 将列表中所有插件标记为“已禁用”（模拟） |

## C++ 用法

`PluginAudit` 的主要实现位于 `Private` 目录，**没有公开的公共 API 头文件**（`.h` 均为私有）。因此其他模块通常**无法直接调用**其内部类。如果需要从代码中触发审核界面，可通过编辑器命令或 `FGlobalTabmanager` 调用（前提是插件已注册 Tab）。

### 头文件引入（仅供参考，非公开 API）

```cpp
// 该头文件为插件内部使用，如直接引用会违反隔离性
// #include "PluginAudit/Private/SPluginAuditBrowser.h"  // 不推荐
```

### 通过 Editor Subsystem 打开（示例，需验证）

假设插件已注册名为 `"PluginAudit"` 的 Tab，可以在任意编辑器工具中通过以下方式打开：

```cpp
#include "Editor.h"
#include "Framework/Docking/TabManager.h"

void OpenPluginAuditWindow()
{
    if (GEditor)
    {
        TSharedPtr<FTabManager> TabManager = FGlobalTabmanager::Get();
        TSharedPtr<SDockTab> Tab = TabManager->TryInvokeTab(FName("PluginAudit"));
        if (!Tab.IsValid())
        {
            UE_LOG(LogTemp, Warning, TEXT("PluginAudit tab not found. Make sure the plugin is enabled."));
        }
    }
}
```

> **注意**：上述 Tab 名称 `"PluginAudit"` 基于 .uplugin 模块名推测，实际注册名称需查看 `PluginAuditModule::StartupModule()` 中的 `FGlobalTabmanager::RegisterTabSpawner` 调用。

### 使用命令行（推荐）

在编辑器控制台输入：
```
PluginAudit
```

若插件正确注册了控制台命令，即可打开审核窗口。

## Demo 示例

由于 `PluginAudit` 是纯编辑器工具，且无公开 API，无法提供可独立编译的 C++ 示例。以下是一个 **Editor Utility Widget** 蓝图示例（假设您希望从自定义工具中打开审核窗口）：

1. 创建 Editor Utility Widget（蓝图类）。
2. 在按钮的 OnClicked 事件中调用 `Execute Console Command` 节点，命令字符串为 `"PluginAudit"`。
3. 编译后运行编辑器，点击按钮即可打开审核界面。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 分析 Game Feature 插件结构（模块列表、脚本包、内容根目录） |
| `AssetManagerEditor` | 通过资产管理器获取插件资产依赖信息 |
| `PluginReferenceViewer` | 双击插件时打开引用查看器，展示该插件的引用关系图 |

> 无其他特殊依赖。

## 维护状态

### 近期更新

```
2024-08-02   cecb3fd7   Separate GFP PluginDetails and PluginURL query functionality.
2024-02-14   7028c9b8   Added ability to cancel the Plugin Audit process in the editor.
2023-10-13   2a4f92dd   GetGameFeaturePluginDetails API cleanup
2023-06-09   af9ea875   Double clicking a plugin name entry in the audit list will open the plugin reference viewer focused
2023-06-09   f038a266   Moving the plugin reference viewer into it's own plugin and module so it can also be launched from t
```

### 维护评价

- **活跃度**：最后一次功能性更新在 2024-08-02（约 7 个月前，以 2025-03 计），之后没有新提交，处于半维护状态。
- **实验性标记**：插件官方标记为 Beta（实验性），意味着 API 可能不稳定，未来可能被移除或合并到其他工具。
- **适用建议**：对于严肃的大型项目，推荐优先使用更成熟的工具（如 **Plugin Reference Viewer** 手动检查），或考虑将 `PluginAudit` 的代码作为参考自行实现审核逻辑。如果项目已启用 Game Features，可以测试使用，但需注意实验性风险。

## 相关链接

- [源码仓库](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PluginAudit)
- [插件引用查看器（Plugin Reference Viewer）](https://docs.unrealengine.com/5.2/en-US/plugin-reference-viewer-in-unreal-engine/)（官方文档，该插件的核心依赖之一）