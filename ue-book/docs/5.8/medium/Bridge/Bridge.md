# Bridge

> Megascans Link for Quixel Bridge.

| 属性 | 值 |
|---|---|
| 中文名 | Quixel Bridge 桥梁插件 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（桌面应用集成） |
| 模块 | `Bridge` (Editor), `MegascansPlugin` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-09 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge) | |

## 用途
该插件的核心功能是将 Quixel Bridge 桌面应用程序与 Unreal Engine 5 编辑器深度集成。它解决的问题是**资产导入工作流的繁琐性**。传统方式下，用户需要从 Bridge 应用导出资产，再手动导入 UE。这个插件通过内嵌一个 Web 浏览器控件并利用 Node.js 进程进行底层通信，实现了在编辑器内直接浏览、下载并拖拽 Quixel Megascans 资产（如材质、模型、植被等）到场景中的工作流，极大简化了流程。

## 使用场景
- 当你是一位环境美术师，正在使用 Quixel Bridge 管理和选择 Megascans 材质与模型，希望直接从 Bridge 界面将资产拖拽到 Unreal Editor 的关卡视口中。
- 当你需要快速预览、筛选并批量导入 Megascans 资产到当前项目中。
- 当你的团队需要标准化资产导入流程，并与 Quixel 账户（用于验证）进行集成。

## 蓝图用法
插件主要通过 `UBrowserBinding` 类暴露接口给 Web 浏览器前端（Bridge 应用的界面），这些函数大多由 JavaScript 回调触发，而非设计为在用户蓝图中直接调用。不过，一些关键状态和事件可通过其暴露的委托访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetProjectPath` | 获取当前 UE 项目的根路径 | `UBrowserBinding` |
| `GetNodePort` | 获取内部 Node.js 进程的通信端口 | `UNodePort` |
| `IsNodeRunning` | 检查 Node.js 进程是否正在运行 | `UNodePort` |
| `ExportDataToMSPlugin` | 将从 Bridge 接收到的 JSON 数据发送到 MegascansPlugin 模块处理 | `UBrowserBinding` |
| `DragStarted` | （内部）开始资产拖拽操作，初始化拖拽数据和回调 | `UBrowserBinding` |

### 使用示例（蓝图描述）
由于该插件的工作流高度依赖浏览器与后端的交互，其核心逻辑并非在用户蓝图中搭建。典型的集成方式是：
1.  插件自动在编辑器工具栏或菜单中添加 “Bridge” 选项卡。
2.  点击后，一个嵌入 Quixel Bridge 网页界面的标签页被打开。
3.  用户在网页界面中登录并选择资产。网页通过 JavaScript 调用 `UBrowserBinding` 上的函数（如 `DragStarted`）发起拖拽。
4.  `UBrowserBinding` 处理拖拽事件，并将资产数据传递给 `MegascansPlugin` 模块完成实际的资产创建和导入。

## C++ 用法
### 头文件引入
```cpp
#include "IBridgeModule.h"
```

### 基本用法
检查模块是否可用并获取其实例。这主要用于确保在使用任何 Bridge 功能前，插件已正确加载。
```cpp
// 检查 Bridge 模块是否已加载
if (IBridgeModule::IsAvailable())
{
    // 获取模块实例
    IBridgeModule& BridgeModule = IBridgeModule::Get();
    // 可以进一步调用模块提供的其他接口...
}
```

### 进阶用法
直接管理 Node.js 进程（通常由插件内部自动管理，但提供接口用于故障恢复）。
```cpp
// 源自 FNodeProcessManager 和 UNodePort 类
// 启动 Node.js 进程
FNodeProcessManager::Get()->StartNodeProcess();

// 检查进程状态
UNodePort* NodePort = NewObject<UNodePort>();
if (NodePort && !NodePort->IsNodeRunning())
{
    // 如果未运行，尝试重启
    FNodeProcessManager::Get()->RestartNodeProcess();
    UE_LOG(LogBridge, Warning, TEXT("Node.js process was not running, attempted restart."));
}
```

## Demo 示例
一个最小化的 C++ 模块示例，展示如何正确集成 Bridge 模块的可用性检查。
`MyBridgeUser.h`
```cpp
#pragma once
#include "CoreMinimal.h"

// 前置声明，避免包含整个 Bridge 模块头文件
class IBridgeModule;

class FMyBridgeUser
{
public:
    /** 初始化并检查 Bridge 功能 */
    void Initialize();

private:
    bool bIsBridgeAvailable = false;
};
```

`MyBridgeUser.cpp`
```cpp
#include "MyBridgeUser.h"
#include "IBridgeModule.h" // 包含 Bridge 模块的公开接口头文件

void FMyBridgeUser::Initialize()
{
    // 检查 Bridge 模块是否在引擎中可用
    bIsBridgeAvailable = IBridgeModule::IsAvailable();

    if (bIsBridgeAvailable)
    {
        UE_LOG(LogTemp, Log, TEXT("Bridge module is available. Megascans workflow is ready."));
        // 在此处可以安全地使用 Bridge 模块提供的任何服务
        // 例如，获取项目路径信息 (通过 BrowserBinding，但通常由插件内部使用)
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Bridge module is not available. Megascans integration is disabled."));
    }
}
```

## 模块依赖
该插件的 `.uplugin` 文件明确声明了对其他插件的依赖。

| 模块 | 用途 |
|---|---|
| `EditorScriptingUtilities` | 提供编辑器脚本相关工具函数，可能用于资产操作或UI交互 |
| `MetaHumanSDK` | 支持与 MetaHuman 相关功能的集成，插件可能用于处理 MetaHuman 相关资产的导出 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4797537` | Fix crash in UMaterialPresetsSettings::PostEditChangeProperty when master material slots are empty o | 修复了主材质槽为空时材质预设设置崩溃的问题。 |
| 2026-04-16 | `aea11131` | Clean up WebBrowser module and init settings, handle module init failures | 清理了 WebBrowser 模块和初始化设置，处理模块初始化失败的情况。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF（可能是新版日志格式）。 |
| 2026-04-06 | `3e98cc7e` | TLazyObjectPtr Deprecation pt 3: | 继续推进 TLazyObjectPtr 的废弃工作（第3部分）。 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 与“正在保存包”的状态相关的修改（可能涉及资产保存流程）。 |

### 维护评价
- **创建时间**：创建于 2020 年 11 月，已维护超过 5 年。
- **更新频率**：从提交历史看，**维护非常活跃**。在最近 2 个月内（截至 2026 年 5 月）仍有功能性更新和 Bug 修复，说明该插件是 Epic Games 工作流中的重要组成部分。
- **内容**：近期更新集中在稳定性和代码现代化上（如修复崩溃、清理模块、更新日志和废弃旧类型），而非添加大量新功能，这表明插件已进入成熟维护期。
- **已知问题/限制**：作为与外部桌面应用（Quixel Bridge）和 Node.js 进程集成的复杂插件，其稳定性可能受外部环境（如端口冲突、Node 进程崩溃）影响。`.uplugin` 中 `EnabledByDefault=true` 意味着对所有使用 Megascans 的项目自动启用。
- **推荐使用**：**强烈推荐**。这是 Quixel Megascans 资产与 Unreal Engine 5 官方集成的标准途径，且持续得到 Epic Games 的维护和更新。是任何使用 Megascans 资产项目的必备插件。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Bridge)
- [官方文档](https://help.quixel.com/hc/en-us/sections/360005846137-Quixel-Bridge-for-Unreal-Engine-5)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Bridge) (推测路径，需确认)